#!/usr/bin/env python3
"""256cha: sim_jerk.py를 지연 0.35 s / 1차 지연 0.15 s로 덮어써 A/A2/B x JerkCostEgo 5/8/12/20 12회를 돌리고 지표 표를 출력한다.
usage: run_final.py <plan.pkl> [out.pkl]
plan.pkl은 gap_replay/ext2.py 출력(열 r_aLeadK, r_modelProb 필요). sim_jerk.py와 같은 폴더에 둘 것.
환경: pytest_ci_setup.sh로 만든 /home/claude/repo(PYTHONPATH=/home/claude/repo:/home/claude/repo/opendbc_repo)에서 실행.
0.35 s는 로그 10.85초 실속도(13.69 m/s)에 J=20 시뮬레이션을 맞춘 값이다(256cha 보정)."""
import os, sys, pickle
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sim_jerk as S
from openpilot.common.prefix import OpenpilotPrefix

S.DELAY_S, S.TAU_S = 0.35, 0.15
plan = pickle.load(open(sys.argv[1], 'rb')); df, dev = plan['df'], plan['params']
inp = S.build_inputs(df, 5.0, 3.4)
rows = []
with OpenpilotPrefix():
  for sc in ['A', 'A2', 'B']:
    for J in [5, 8, 12, 20]:
      r = S.run(dev, inp, J, sc)
      w = r[r.t >= 8.0].reset_index(drop=True)
      areq = np.where(w.gap_true > 0.3, w.v ** 2 / (2 * np.maximum(w.gap_true, 0.3)), 0)
      i = (w.t - 10.83).abs().idxmin()
      jerk = np.gradient(w.a_act.values, w.t.values)
      hit = w[(w.gap_true <= 0.05) & (w.v > 0.5)]
      rows.append(dict(scn=sc, J=J, v1083=w.v[i], gap1083=w.gap_true[i], areq1083=areq[i], areq_max=areq.max(),
                       peak_decel=w.a_act.min(), peak_jerk=jerk.min(), min_gap=w.gap_true.min(),
                       t_hit=(hit.t.iloc[0] if len(hit) else np.nan), v_hit=(hit.v.iloc[0] if len(hit) else np.nan)))
T = pd.DataFrame(rows)
pd.set_option('display.width', 220)
print(T.round(2).to_string(index=False))
if len(sys.argv) > 2:
  T.to_pickle(sys.argv[2])
