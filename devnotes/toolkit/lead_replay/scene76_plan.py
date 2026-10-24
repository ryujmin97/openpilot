#!/usr/bin/env python3
"""scene76_plan.py (311cha) route 000004bf 세그먼트 76 정지 차량 노출 장면 재생, 실제 `LongitudinalPlanner.update`의 MPC 호출부를 그대로 따른다. 실차 검증 아님.
scene76_replay.py와 다른 점(실제 플래너 코드 longitudinal_planner.py 5339d98 읽고 맞춤):
  - MPC 시작 상태는 측정값이 아니라 (v_desired_filter.x, a_desired): v_desired_filter는 FirstOrderFilter(rc 2.0)가 v_ego로 당기고 매 사이클 계획 가속도를 적분한다.
  - 명령은 a_solution[0.05초]가 아니라 `get_accel_from_plan(v_traj, a_traj, CONTROL_N_T_IDX, action_t=LongActuatorDelay*0.01+DT_MDL)`의 a_target_base(로그 aTargetBase). 로그 LongActuatorDelay=20 -> 0.25초.
  - a_change_cost_starting은 로그 AChangeCostStarting=150(재생 도구 기본 10이 아니다), accel 하한 min(A_CRUISE_MIN -2.0, a_desired+0.05).
311cha 후속: Plan.lar(LeadAccelResponse 레벨, 기본 0 = 로그 설정)와 Plan.ss(get_accel_from_plan의 should_stop)를 start_replay.py가 쓴다(기본 동작은 그대로).
모드: ol(열린 루프: 로그 vEgo/aEgo/앞차 입력, aTargetBase와 비교) / cl(폐루프: 정지 차량 노출 TR부터 자차는 1차 플랜트).
한계: 모델 궤적(x,v,a,j)은 0, lead preview(aTarget-aTargetBase, 최대 약 -0.2 m/s^2)와 controlsd 한계는 없음, 앞차 위치는 로그 거리에서 만든 추정, 센서 지연/노이즈 없음, 설정속도는 가정.
사전 준비: pytest_ci_setup.sh -> cl_sim/prep_base.sh HEAD(cl_sim이 기준선 모듈을 임포트, 쓴 뒤 long_mpc_base110.py 삭제) -> extract_log.py(log_lead.pkl) + extract_plan_ext.py(lp_ext.pkl).
값 중 route 000004bf 세그먼트 76 전용: T_SW(정지 차량 노출 183.355954초), A_CHANGE_COST_STARTING 150, LongActuatorDelay 20, VEgoStopping 5, sd 7.0, tau 0.35(plant_fit.py 181~192초), 설정속도 15 m/s 가정. 다른 로그에는 이 값부터 바꾼다.
실행: python3 scene76_plan.py ol (열린 루프 검증) / python3 scene76_plan.py cl [런 이름...] (폐루프 8런, 약 1.5분).
환경: PYTHONPATH=/home/claude/repo:/home/claude/repo/opendbc_repo, LR_PKL, LP_PKL(lp_ext.pkl), CL_SIM_DIR.
"""
import sys, os, math, pickle
import numpy as np, pandas as pd
from types import SimpleNamespace as NS
sys.path.insert(0, os.environ.get('CL_SIM_DIR', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'cl_sim')))
from openpilot.selfdrive.controls.lib.longitudinal_mpc_lib import long_mpc as M
from openpilot.selfdrive.controls.lib.drive_helpers import CONTROL_N, get_accel_from_plan
from openpilot.selfdrive.modeld.constants import ModelConstants
from openpilot.common.filter_simple import FirstOrderFilter
import cl_sim

D = pickle.load(open(os.environ.get('LR_PKL', 'log_lead.pkl'), 'rb')); rs, cs, lp, cc = D['rs'], D['cs'], D['lp'], D['cc']
LPX = pickle.load(open(os.environ.get('LP_PKL', 'lp_ext.pkl'), 'rb'))
DT = 0.05
CONTROL_N_T_IDX = ModelConstants.T_IDXS[:CONTROL_N]
A_CRUISE_MIN = -2.0
ACTION_T = 0.20 + DT      # LongActuatorDelay 20 * 0.01 + DT_MDL
V_EGO_STOPPING = 0.05     # VEgoStopping 5 * 0.01
A_CHANGE_COST_STARTING = 150.0
T_SW = 183.355954         # 레이더 tid 0이 정지 차량을 처음 잡은 프레임
tc = cs.t.values
xe_c = np.concatenate([[0], np.cumsum(np.diff(tc) * cs.vEgo.values[1:])])
xego_log = lambda q: float(np.interp(q, tc, xe_c))
_ix = lambda q: int(np.clip(np.searchsorted(rs.t.values, q, side='right') - 1, 0, len(rs) - 1))
R = lambda c, q: rs[c].values[_ix(q)]
XS = xego_log(T_SW) + float(R('l1_dRel', T_SW))
ZOH = lambda df, c, q: float(df[c].values[int(np.clip(np.searchsorted(df.t.values, q, side='right') - 1, 0, len(df) - 1))])


class Plan:
    """longitudinal_planner.py update()의 MPC 호출부 사본(reset_state False, acc 모드)."""
    def __init__(self, v0, a0, sd=7.0, cb=2.5, vset=15.0, vset_gate=None, a_chg=A_CHANGE_COST_STARTING, gate_off=False):
        self.mpc = M.LongitudinalMpc(dt=DT); self.mpc.mode = 'acc'; self.mpc.reset(); self.mpc.prev_a = np.full(M.N + 1, a0)
        self.vf = FirstOrderFilter(v0, 2.0, DT); self.a_des = a0; self.lt = 0; self.first = True
        self.sd, self.cb, self.vset, self.a_chg = sd, cb, vset, a_chg
        self.orig = M.LongitudinalMpc.__dict__['_gate_raw']
        if gate_off:
            raw = self.orig.__func__; M.LongitudinalMpc._gate_raw = staticmethod(lambda *a, **k: (1.0, raw(*a, **k)[1]))
        self.gate_off = gate_off

    def close(self):
        M.LongitudinalMpc._gate_raw = self.orig

    def step(self, v_ego, a_ego, l1, tf, standstill=False):
        z = lambda: np.zeros(M.N + 1)
        lim0 = min(A_CRUISE_MIN, self.a_des + 0.05)
        self.vf.x = max(0.0, self.vf.update(v_ego))
        self.lt = self.lt + 1 if (l1.status and l1.radar) else 0
        carrot = cl_sim.mk_carrot(tf=tf, cb=self.cb, sd=self.sd, vcruise=self.vset)
        self.mpc.set_accel_limits(lim0, 1.5); self.mpc.set_cur_state(self.vf.x, self.a_des)
        rsx = NS(leadOne=l1, leadTwo=cl_sim.lead_ns(False, 0, 0, v_ego, 0, -1))
        self.mpc.update(carrot, False, rsx, self.vset, z(), z(), z(), z(), prev_accel_constraint=not standstill, jerk_factor=1.,
                        a_change_cost_starting=self.a_chg, lead_accel_response_enabled=(getattr(self, 'lar', 0) > 0), lead_gap_enabled=True,
                        lead_track_frames=(self.lt, 0), measured_a_ego=a_ego, cutout_relief_enabled=True)
        v_tr = np.interp(CONTROL_N_T_IDX, M.T_IDXS, self.mpc.v_solution); a_tr = np.interp(CONTROL_N_T_IDX, M.T_IDXS, self.mpc.a_solution)
        a_prev = self.a_des; self.a_des = float(np.interp(DT, CONTROL_N_T_IDX, a_tr))
        self.vf.x = self.vf.x + DT * (self.a_des + a_prev) / 2.0
        a_base, self.ss, _, _ = get_accel_from_plan(v_tr, a_tr, CONTROL_N_T_IDX, action_t=ACTION_T, vEgoStopping=V_EGO_STOPPING)
        return a_base, self.a_des, float(self.mpc.desired_distance), self.mpc


def lead_in(t, gap, v_ego, stopped, inputs):
    if stopped and inputs == 'ideal':
        return NS(status=True, radar=True, radarTrackId=0, dRel=gap, vRel=-v_ego, vLead=0.0, aLeadK=0.0, aLeadTau=0.3, modelProb=.99, cutOutTime=0., cutOutConfidence=0.)
    st = bool(R('l1_status', t)) or stopped
    vl = float(R('l1_vLead', t)); rad = bool(R('l1_radar', t)) or stopped
    return NS(status=st, radar=rad, radarTrackId=0 if rad else -1, dRel=gap, vRel=vl - v_ego, vLead=vl, aLeadK=float(R('l1_aLeadK', t)), aLeadTau=float(R('l1_aLeadTau', t)),
              modelProb=float(R('l1_prob', t)) or .95, cutOutTime=0., cutOutConfidence=0.)


def ol(t0=170.0, t1=192.0, **kw):
    """열린 루프: 로그 vEgo/aEgo/앞차 입력(dRel은 로그 그대로)으로 플래너 MPC를 돌려 a_target_base를 로그 aTargetBase와 비교."""
    P = Plan(float(np.interp(t0, tc, cs.vEgo)), float(np.interp(t0, cs.t, cs.aEgo)), **kw)
    out = []
    try:
        for k in range(int(round((t1 - t0) / DT))):
            t = t0 + k * DT
            v = float(np.interp(t, tc, cs.vEgo)); a = float(np.interp(t, cs.t, cs.aEgo))
            l1 = lead_in(t, float(R('l1_dRel', t)), v, False, 'log')
            ab, ad, dd, _ = P.step(v, a, l1, ZOH(lp, 'tFollow', t) or 1.6, standstill=v < 0.05)
            out.append((t, ab, ad, dd))
    finally:
        P.close()
    return pd.DataFrame(out, columns='t a_base a_des desired'.split())


def cl(tr=T_SW, inputs='log', t0=181.0, t1=200.0, tau=0.35, delay=0.0, use_preview=False, **kw):
    """폐루프: t < tr 은 로그 자차 상태(열린 루프로 플래너 상태를 데움), tr부터 자차는 cmd=a_target_base를 1차 플랜트(tau, delay)로 따른다."""
    v = float(np.interp(t0, tc, cs.vEgo)); xe = xego_log(t0); a_act = float(np.interp(t0, cs.t, cs.aEgo))
    P = Plan(v, a_act, **kw); q = [0.0] * int(round(delay / DT)); out = []
    try:
        for k in range(int(round((t1 - t0) / DT))):
            t = t0 + k * DT
            if t < tr:
                v = float(np.interp(t, tc, cs.vEgo)); xe = xego_log(t); a_act = float(np.interp(t, cs.t, cs.aEgo))
            stopped = t >= tr
            gap = (XS if stopped else xego_log(t) + float(R('l1_dRel', t))) - xe
            l1 = lead_in(t, gap, v, stopped, inputs)
            ab, ad, dd, mpc = P.step(v, a_act, l1, ZOH(lp, 'tFollow', t) or 1.6, standstill=v < 0.05)
            pred_gap = gap - float(mpc.x_sol[-1, 0] - mpc.x_sol[0, 0])
            out.append((t, v, a_act, ab, gap, dd, pred_gap, int(mpc.solution_status != 0)))
            if t >= tr:
                q.append(ab); cmd = q.pop(0)
                a_act += (cmd - a_act) * (1 - math.exp(-DT / tau)); v = max(0., v + a_act * DT); xe += v * DT
    finally:
        P.close()
    return pd.DataFrame(out, columns='t v a a_base gap desired pred_gap bad'.split())


def summ(df, tr, name):
    d = df[df.t >= tr]; st = d[d.v < 0.05]
    stop_gap = float(st.gap.iloc[0]) if len(st) else float(d.gap.iloc[-1]); t_stop = float(st.t.iloc[0] - tr) if len(st) else float('nan')
    first = d[d.t < tr + 0.5]; moving = d[d.v > 1.0]
    at = lambda q, c: float(d[c].iloc[(d.t - q).abs().argmin()])
    return dict(name=name, stop_gap=round(stop_gap, 2), t_stop=round(t_stop, 1), a_min=round(float(d.a.min()), 2), a_base_min=round(float(d.a_base.min()), 2),
                a_base_first05=round(float(first.a_base.mean()), 2), min_ttc=round(float((moving.gap / moving.v).min()), 2) if len(moving) else None,
                pred_gap_t0=round(at(tr + 0.05, 'pred_gap'), 1), pred_gap_t1=round(at(tr + 1.0, 'pred_gap'), 1), desired_stop=round(float(st.desired.iloc[0]) if len(st) else float('nan'), 2), bad=int(df.bad.sum()))


def log_row():
    d = cs[(cs.t >= T_SW) & (cs.t <= 200)]; g = np.interp(d.t.values, rs.t.values, np.where(rs.l1_status, rs.l1_dRel, np.nan)); k = (d.vEgo < 0.05).values.argmax()
    w = LPX[(LPX.t >= T_SW) & (LPX.t < T_SW + 0.5)]
    return dict(name='LOG(actual)', stop_gap=round(float(g[k]), 2), t_stop=round(float(d.t.values[k] - T_SW), 1), a_min=round(float(d.aEgo.min()), 2),
                a_base_min=round(float(LPX[LPX.t >= T_SW].aTargetBase.min()), 2), a_base_first05=round(float(w.aTargetBase.mean()), 2))


if __name__ == '__main__':
    pd.set_option('display.width', 250)
    mode = sys.argv[1] if len(sys.argv) > 1 else 'ol'
    if mode == 'ol':
        o = ol(); sel = (o.t >= 183.3) & (o.t <= 190)
        lg = np.interp(o.t.values, LPX.t.values, LPX.aTargetBase.values)
        print('열린 루프 a_target_base vs 로그 aTargetBase(183.3~190초): RMSE %.3f, 평균차 %.3f, 최대차 %.3f' % (np.sqrt(np.mean((o.a_base[sel] - lg[sel]) ** 2)), np.mean(o.a_base[sel] - lg[sel]), np.max(np.abs(o.a_base[sel] - lg[sel]))))
        for t in [182, 183, 183.3, 183.4, 183.5, 183.7, 184, 184.5, 185, 186, 187, 188, 190]:
            i = int((o.t - t).abs().argmin()); print('%6.2f  replay %6.2f   log %6.2f   desired %5.1f' % (t, o.a_base.iloc[i], lg[i], o.desired.iloc[i]))
        pickle.dump(o, open('scene76_ol.pkl', 'wb'))
    else:
        plan = [('base_log_inputs', dict()), ('ideal_stationary', dict(inputs='ideal')), ('gate_off', dict(gate_off=True)),
                ('sd6.0', dict(sd=6.0)), ('sd8.0', dict(sd=8.0)), ('reveal_-0.5s', dict(tr=T_SW - 0.5, inputs='ideal')),
                ('reveal_-1.0s', dict(tr=T_SW - 1.0, inputs='ideal')), ('reveal_-2.0s', dict(tr=T_SW - 2.0, inputs='ideal'))]
        only = sys.argv[2:]; rows = [log_row()]; res = {}
        for nm, kw in plan:
            if only and nm not in only:
                continue
            tr = kw.get('tr', T_SW); df = cl(**kw); res[nm] = df; rows.append(summ(df, tr, nm)); print(nm, flush=True)
        pickle.dump(res, open('scene76_plan_cl.pkl', 'wb')); print(pd.DataFrame(rows).to_string(index=False))
