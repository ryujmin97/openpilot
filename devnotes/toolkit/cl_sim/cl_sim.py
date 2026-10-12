"""폐루프 시뮬레이션: 실제 acados LongitudinalMpc(HEAD) vs 기준선 모듈 비교 (269cha, carrot-ryu 760905a vs 110cff9).
실차 검증 아님. 자차 플랜트=1차 지연(ego_tau)+순수 지연(delay), 레이더=이상적(노이즈/지연 없음), 앞차 1대.
플래너의 리셋 램프/끼어들기 사전감속/SCC 실제 거동은 넣지 않았다.

기준선 모듈 준비(저장소 루트에서, 약 1초): prep_base.sh <기준선 커밋> -> long_mpc_base110.py 생성.
실행: cd /home/claude/repo && export PYTHONPATH=/home/claude/repo:/home/claude/repo/opendbc_repo
      python3 <이 폴더>/sweep.py   (scen.py, cl_sim.py가 같은 폴더에 있어야 한다)
"""
import sys, importlib, math
from types import SimpleNamespace as NS
import numpy as np
from openpilot.selfdrive.controls.lib.longitudinal_mpc_lib import long_mpc as head_mod
from openpilot.selfdrive.controls.lib.longitudinal_mpc_lib import long_mpc_base110 as base_mod
from openpilot.selfdrive.carrot.radar_motion.lane_change_gap import LaneChangeGapPlan

DT = 0.05


def mk_carrot(tf=1.45, cb=2.5, sd=6.0, vcruise=40.0):
  return NS(comfort_brake=cb, stop_distance=sd, v_cruise=vcruise, stop_dist=1000., mode='acc', myDrivingMode=3,
            trafficStopDistanceAdjust=0., trafficStopModelLeadOffset=0., leadAccelResponse=0,
            get_T_FOLLOW=lambda *a, **k: tf, jerk_factor=1., autoNaviSpeedDecelRate=1.0, dynamicTFollowLC=.9,
            lane_change_gap=LaneChangeGapPlan())


def lead_ns(on, d, vl, vego, al, tid):
  if not on:
    return NS(status=False, radar=False, radarTrackId=-1, dRel=0., vRel=0., vLead=0., aLeadK=0., aLeadTau=0.,
              modelProb=0., cutOutTime=0., cutOutConfidence=0.)
  return NS(status=True, radar=True, radarTrackId=tid, dRel=d, vRel=vl - vego, vLead=vl, aLeadK=al, aLeadTau=1.5,
            modelProb=.99, cutOutTime=0., cutOutConfidence=0.)


def run(mod, scen, tf=1.45, ego_tau=0.35, delay=0.15, T=40.0, v0=None, vset=40.0, tid=50, lead_gap_enabled=True):
  mpc = mod.LongitudinalMpc(dt=DT); mpc.mode = 'acc'; mpc.reset()
  carrot = mk_carrot(tf=tf, vcruise=vset)
  v0 = scen['v0'] if v0 is None else v0
  v, a_act, x_ego = v0, 0.0, 0.0
  x_lead = x_ego + scen['gap0']
  a_desired = 0.0
  mpc.prev_a = np.zeros(mod.N + 1)
  cmd_q = [0.0] * int(round(delay / DT))
  log = []
  reset = True
  lt_frames = [0, 0]
  zeros = lambda: np.zeros(mod.N + 1)
  for k in range(int(T / DT)):
    t = k * DT
    vl, al, present = scen['lead'](t)
    ap = scen.get('appear')
    if ap and abs(t - ap[0]) < DT / 2:
      x_lead = x_ego + ap[1]
    if k > 0:
      x_lead += vl * DT
    gap = x_lead - x_ego
    ld = lead_ns(present, gap, vl, v, al, tid if present else -1)
    rs = NS(leadOne=ld, leadTwo=lead_ns(False, 0, 0, v, 0, -1))
    lt_frames = [lt_frames[0] + 1 if present else 0, 0]
    mpc.set_accel_limits(-3.5, 1.5)
    mpc.set_cur_state(v, a_desired)
    mpc.update(carrot, reset, rs, vset, zeros(), zeros(), zeros(), zeros(),
               prev_accel_constraint=True, jerk_factor=1., a_change_cost_starting=10.,
               lead_accel_response_enabled=False, lead_gap_enabled=lead_gap_enabled,
               lead_track_frames=tuple(lt_frames), measured_a_ego=a_act, cutout_relief_enabled=True)
    reset = False
    a_traj = mpc.a_solution
    a_desired = float(np.interp(DT, np.array(mod.T_IDXS), a_traj))
    cmd_q.append(a_desired); a_cmd = cmd_q.pop(0)
    a_act += (a_cmd - a_act) * (1 - math.exp(-DT / ego_tau))
    v = max(0.0, v + a_act * DT); x_ego += v * DT
    bs = getattr(mpc, 'braking_gap_states', None)  # 기준선 모듈에는 없다(margin/relief 0으로 기록)
    log.append(dict(t=t, v=v, a=a_act, gap=gap, vl=vl, present=present, th=(gap / v if v > 0.5 else 99),
                    crash=mpc.crash_cnt, status=mpc.solution_status,
                    margin=(bs[0].margin if bs else 0.), relief=(bs[0].relief if bs else 0.),
                    floor=(bs[0].floor if bs and bs[0].floor is not None else float('nan')),
                    des=float(mpc.desired_distance if np.ndim(mpc.desired_distance) == 0 else np.ravel(mpc.desired_distance)[0])))
  return log


def metrics(log):
  v = np.array([r['v'] for r in log]); a = np.array([r['a'] for r in log]); g = np.array([r['gap'] for r in log])
  pres = np.array([r['present'] for r in log]); vl = np.array([r['vl'] for r in log])
  th = np.array([r['th'] for r in log]); crash = max(r['crash'] for r in log)
  j = np.diff(a) / DT
  rel_v = v - vl
  ttc = np.where((rel_v > 0.1) & pres, g / np.maximum(rel_v, 0.1), 99)
  return dict(min_gap=float(g[pres].min()), min_th=float(th[pres].min()), min_ttc=float(ttc.min()),
              a_min=float(a.min()), jerk_min=float(j.min()), jerk_max=float(j.max()), crash_max=float(crash),
              bad_status=int(sum(r['status'] != 0 for r in log)),
              max_margin=max(r['margin'] for r in log), max_relief=max(r['relief'] for r in log),
              v_end=float(v[-1]), gap_end=float(g[-1]))
