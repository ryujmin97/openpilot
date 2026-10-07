#!/usr/bin/env python3
"""260cha: sim_jerk.py(256cha)의 시나리오 A(로그 인식, 끊김 프레임은 선형 보간으로 채워짐)에 대해,
로그의 앞차 끊김을 그대로 두는 시나리오 G(끊긴 프레임은 앞차 없음 = 670f72c 게이트 거동)를 추가해 A와 비교한다.
G: 로그 r_status/r_dRel>1 이 False인 프레임(직전값 유지)에서 lead=None, 그 외는 A와 같은 입력.
A(채움)는 1326f21 게이트가 끊김을 없앤 경우의 근사다(채운 프레임의 dRel/vLead는 보간값이지 그 프레임 비전 원시값이 아니다).
usage: run_gap.py <plan.pkl> [out.pkl]   (sim_jerk.py 와 같은 폴더, run_final.py 와 같은 환경, 지연 0.35 s / 시상수 0.15 s)
"""
import os, sys, pickle
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sim_jerk as S
from openpilot.common.params import Params
from openpilot.common.prefix import OpenpilotPrefix

S.DELAY_S, S.TAU_S = 0.35, 0.15
DT = S.DT


def run(dev, inp, valid, J, scenario, t0=5.0, t1=14.0, v_cruise=17.9):
  p = Params(); S.inject_params(p, dev); p.put('JerkCostEgo', int(J))
  v0 = float(np.interp(t0, inp['t'], inp['v_log']))
  plant = S.SimPlant(lead_relevancy=True, speed=v0, distance_lead=200.0, enabled=True, personality=3)
  x0 = float(np.interp(t0, inp['t'], inp['x_log']))
  rows = []
  for k in range(int(round((t1 - t0) / DT))):
    tk = t0 + k * DT
    gap = inp['X_bus'] - (x0 + plant.distance)
    lead = None
    if tk >= inp['first_valid'] and gap > 0.5:
      vi = max(0, int(np.searchsorted(inp['t'], tk, 'right')) - 1)
      if scenario == 'A' or valid[vi]:
        e = float(np.interp(tk, inp['t'], inp['err']))
        lead = dict(dRel=max(1.0, gap + e), vLead=float(np.interp(tk, inp['t'], inp['vlead'])),
                    aLeadK=float(np.interp(tk, inp['t'], inp['alead'])),
                    prob=max(0.6, float(np.interp(tk, inp['t'], inp['prob']))))
    o = plant.step2(lead, v_cruise)
    rows.append((tk, o['v'], o['a_act'], o['a_cmd'], gap, o['src'], o['fcw'], lead is not None))
  return pd.DataFrame(rows, columns=['t', 'v', 'a_act', 'a_cmd', 'gap_true', 'src', 'fcw', 'has_lead'])


if __name__ == '__main__':
  plan = pickle.load(open(sys.argv[1], 'rb')); df, dev = plan['df'], plan['params']
  inp = S.build_inputs(df, 5.0, 3.4)
  valid = df.r_status.values.astype(bool) & (df.r_dRel.values > 1.0)
  rows, res = [], {}
  with OpenpilotPrefix():
    for sc in ['G', 'A']:
      for J in [5, 8, 12, 20]:
        r = run(dev, inp, valid, J, sc); res[(sc, J)] = r
        w = r[r.t >= 8.0].reset_index(drop=True)
        areq = np.where(w.gap_true > 0.3, w.v ** 2 / (2 * np.maximum(w.gap_true, 0.3)), 0)
        i = (w.t - 10.83).abs().idxmin()
        jerk = np.gradient(w.a_act.values, w.t.values)
        hit = w[(w.gap_true <= 0.05) & (w.v > 0.5)]
        rows.append(dict(scn=sc, J=J, no_lead_frames=int((~w.has_lead & (w.gap_true > 0.5)).sum()), v1083=w.v[i], gap1083=w.gap_true[i],
                         areq1083=areq[i], areq_max=areq.max(), peak_decel=w.a_act.min(), peak_jerk=jerk.min(),
                         min_gap=w.gap_true.min(), t_hit=(hit.t.iloc[0] if len(hit) else np.nan),
                         v_hit=(hit.v.iloc[0] if len(hit) else np.nan)))
  T = pd.DataFrame(rows); pd.set_option('display.width', 220)
  print('log valid frames in 8~14 s:', int(valid[(df.t.values >= 8) & (df.t.values <= 14)].sum()), '/', int(((df.t.values >= 8) & (df.t.values <= 14)).sum()))
  print(T.round(2).to_string(index=False))
  if len(sys.argv) > 2: pickle.dump(dict(T=T, res=res), open(sys.argv[2], 'wb'))
