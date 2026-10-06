#!/usr/bin/env python3
"""256cha: 실차 로그(route 00000492--6a8e8eee69--4)의 정지 버스 접근 장면을 carrot-ryu 670f72c 실제
LongitudinalPlanner(acados MPC)에 넣어 JerkCostEgo=5/8/12/20 폐루프 비교.

usage: sim_jerk.py <plan.pkl> <out.pkl>
시나리오: A=로그 그대로의 인식(거리 오차 + 로그 vLead/aLeadK), A2=거리 오차만 로그 그대로(vLead=0),
          B=이상적 인식(정지 버스, 오차 없음)
구동계: 지연 0.30 s + 1차 지연 0.15 s (로그 aTarget->aEgo 피팅, RMSE 0.20 m/s^2)
"""
import sys, pickle, collections
import numpy as np

import openpilot.cereal.messaging as messaging
from openpilot.cereal import log
from openpilot.common.params import Params, ParamKeyType
from openpilot.common.prefix import OpenpilotPrefix
from openpilot.selfdrive.test.longitudinal_maneuvers.plant import Plant, FakeSubMaster
from openpilot.selfdrive.modeld.constants import ModelConstants
from openpilot.selfdrive.controls.lib.longcontrol import LongCtrlState
from openpilot.selfdrive.controls.radar_constants import LEAD_ACCEL_TAU

DT = 0.05
DELAY_S, TAU_S = 0.30, 0.15


def inject_params(p, dev):
  n = 0
  for k, v in dev.items():
    if k.startswith('_') or not p.check_key(k):
      continue
    t = p.get_type(k)
    try:
      if t == ParamKeyType.BOOL: p.put(k, str(v).strip().lower() in ('1', 'true'))
      elif t == ParamKeyType.INT: p.put(k, int(float(v)))
      elif t == ParamKeyType.FLOAT: p.put(k, float(v))
      elif t == ParamKeyType.STRING: p.put(k, str(v))
      else: continue
      n += 1
    except Exception:
      pass
  return n


class SimPlant(Plant):
  """Plant.step 복사본 + (1) 앞차 측정값 직접 주입 (2) 구동계 지연 모델."""
  def __init__(self, *a, **k):
    super().__init__(*a, **k)
    self.a_act = 0.0
    self.cmd_hist = collections.deque([0.0] * int(round(DELAY_S / DT)), maxlen=int(round(DELAY_S / DT)))

  def step2(self, lead, v_cruise):
    radar = messaging.new_message('radarState')
    control = messaging.new_message('controlsState')
    ss = messaging.new_message('selfdriveState')
    car_state = messaging.new_message('carState')
    lp = messaging.new_message('liveParameters')
    car_control = messaging.new_message('carControl')
    model = messaging.new_message('modelV2')

    ld = log.RadarState.LeadData.new_message()
    if lead is not None:
      ld.dRel = float(lead['dRel']); ld.yRel = 0.0
      ld.vRel = float(lead['vLead'] - self.speed)
      ld.aRel = float(lead['aLeadK'] - self.a_act)
      ld.vLead = float(lead['vLead']); ld.vLeadK = float(lead['vLead'])
      ld.aLeadK = float(lead['aLeadK']); ld.aLeadTau = float(lead.get('aLeadTau', LEAD_ACCEL_TAU))
      ld.status = True; ld.modelProb = float(lead['prob']); ld.radar = False; ld.radarTrackId = -1
    else:
      ld.dRel = 0.0; ld.status = False
    radar.radarState.leadOne = ld
    radar.radarState.leadTwo = ld

    position = log.XYZTData.new_message()
    position.x = [float(x) for x in (self.speed + 0.5) * np.array(ModelConstants.T_IDXS)]
    position.y = [0.0 for _ in ModelConstants.T_IDXS]
    position.z = [0.0 for _ in ModelConstants.T_IDXS]
    position.t = [float(t) for t in ModelConstants.T_IDXS]
    model.modelV2.position = position
    model.modelV2.action.desiredAcceleration = float(self.acceleration + 0.1)
    velocity = log.XYZTData.new_message()
    velocity.x = [float(x) for x in (self.speed + 0.5) * np.ones_like(ModelConstants.T_IDXS)]
    velocity.x[0] = float(self.speed)
    model.modelV2.velocity = velocity
    acc = log.XYZTData.new_message()
    acc.x = [float(x) for x in np.zeros_like(ModelConstants.T_IDXS)]
    model.modelV2.acceleration = acc
    model.modelV2.meta.disengagePredictions.gasPressProbs = [1.0 for _ in range(6)]

    control.controlsState.longControlState = LongCtrlState.pid
    ss.selfdriveState.experimentalMode = False
    ss.selfdriveState.personality = self.personality
    control.controlsState.forceDecel = False
    car_state.carState.vEgo = float(self.speed)
    car_state.carState.aEgo = float(self.a_act)
    car_state.carState.vEgoCluster = float(self.speed)
    car_state.carState.standstill = bool(self.speed < 0.01)
    car_state.carState.vCruise = float(v_cruise * 3.6)
    car_control.carControl.orientationNED = [0., 0., 0.]

    sm = FakeSubMaster({'radarState': radar.radarState, 'carState': car_state.carState,
                        'carControl': car_control.carControl, 'controlsState': control.controlsState,
                        'selfdriveState': ss.selfdriveState, 'liveParameters': lp.liveParameters,
                        'modelV2': model.modelV2})
    self.planner.update(sm, self.carrot)
    a_cmd = float(self.planner.output_a_target)
    # 구동계: 지연 + 1차 지연
    delayed = self.cmd_hist[0]
    self.cmd_hist.append(a_cmd)
    self.a_act += DT / TAU_S * (delayed - self.a_act)
    self.acceleration = a_cmd
    self.speed = max(0.0, self.speed + self.a_act * DT)
    if self.speed <= 0.0:
      self.a_act = max(self.a_act, 0.0) if a_cmd >= 0 else 0.0
    self.distance += self.speed * DT
    return dict(a_cmd=a_cmd, a_act=self.a_act, v=self.speed, x=self.distance, src=self.planner.mpc.source,
                fcw=bool(self.planner.fcw))


def build_inputs(df, t_start, bus_gap_final):
  t = df.t.values
  dt = np.diff(t, prepend=t[0])
  x_log = np.cumsum(df.vEgo.values * dt)
  # 운전자가 세운 뒤 정지(vEgo<0.1, t>12) 시점의 vision dRel로 버스 위치 복원
  si = int(np.where((t > 12.0) & (df.vEgo.values < 0.1))[0][0])
  bus_gap_final = float(df.r_dRel.values[si])
  X_bus = x_log[si] + bus_gap_final
  print('stop idx t=%.2f x=%.2f dRel_final=%.2f -> X_bus=%.2f' % (t[si], x_log[si], bus_gap_final, X_bus))
  valid = df.r_status.values.astype(bool) & (df.r_dRel.values > 1.0)
  true_gap = X_bus - x_log
  err = np.where(valid, df.r_dRel.values - true_gap, np.nan)
  vl = np.where(valid, df.r_vLead.values, np.nan)
  ak = np.where(valid, df.r_aLeadK.values, np.nan)
  pr = np.where(valid, df.r_modelProb.values, np.nan)
  first_valid = t[valid][0]
  def fill(a):
    idx = np.where(~np.isnan(a))[0]
    return np.interp(t, t[idx], a[idx])
  return dict(t=t, x_log=x_log, X_bus=X_bus, err=fill(err), vlead=fill(vl), alead=fill(ak), prob=fill(pr),
              first_valid=first_valid, v_log=df.vEgo.values)


def run(dev, inp, J, scenario, t0=5.0, t1=14.0, v_cruise=17.9, verbose=False):
  p = Params()
  inject_params(p, dev)
  p.put('JerkCostEgo', int(J))
  v0 = float(np.interp(t0, inp['t'], inp['v_log']))
  plant = SimPlant(lead_relevancy=True, speed=v0, distance_lead=200.0, enabled=True, personality=3)
  x0 = float(np.interp(t0, inp['t'], inp['x_log']))
  rows = []
  n = int(round((t1 - t0) / DT))
  for k in range(n):
    tk = t0 + k * DT
    x_ego = x0 + plant.distance
    gap = inp['X_bus'] - x_ego
    lead = None
    if tk >= inp['first_valid'] and gap > 0.5:
      e = float(np.interp(tk, inp['t'], inp['err']))
      pr = max(0.6, float(np.interp(tk, inp['t'], inp['prob'])))
      if scenario == 'A':
        lead = dict(dRel=max(1.0, gap + e), vLead=float(np.interp(tk, inp['t'], inp['vlead'])),
                    aLeadK=float(np.interp(tk, inp['t'], inp['alead'])), prob=pr)
      elif scenario == 'A2':
        lead = dict(dRel=max(1.0, gap + e), vLead=0.0, aLeadK=0.0, prob=pr)
      elif scenario == 'B':
        lead = dict(dRel=max(1.0, gap), vLead=0.0, aLeadK=0.0, prob=0.9)
    o = plant.step2(lead, v_cruise)
    v = o['v']
    rows.append((tk, v, o['a_act'], o['a_cmd'], gap, x_ego, o['src'], o['fcw'],
                 lead['dRel'] if lead else np.nan, lead['vLead'] if lead else np.nan))
  cols = ['t', 'v', 'a_act', 'a_cmd', 'gap_true', 'x', 'src', 'fcw', 'dRel_meas', 'vLead_meas']
  import pandas as pd
  return pd.DataFrame(rows, columns=cols)


if __name__ == '__main__':
  plan = pickle.load(open(sys.argv[1], 'rb'))
  df, dev = plan['df'], plan['params']
  inp = build_inputs(df, 5.0, 3.4)
  res = {}
  with OpenpilotPrefix():
    for sc in ['A', 'A2', 'B']:
      for J in [5, 8, 12, 20]:
        res[(sc, J)] = run(dev, inp, J, sc)
        r = res[(sc, J)]
        print(sc, J, 'min a %.2f  v_end %.2f  min gap %.2f' % (r.a_act.min(), r.v.iloc[-1], r.gap_true.min()), flush=True)
  pickle.dump(dict(res=res, inp={k: v for k, v in inp.items() if k != 'x_log'}), open(sys.argv[2], 'wb'))
