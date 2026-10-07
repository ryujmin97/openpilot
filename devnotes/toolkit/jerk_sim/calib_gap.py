#!/usr/bin/env python3
"""260cha: run_gap.py 의 G(끊김 유지)/A(끊김 채움) 시나리오를 구동 지연 0.10~0.45 s 로 바꿔 JerkCostEgo=20 에서 돌리고,
실차 속도(vEgo)와의 8~11.5 s 구간 RMSE 및 10.85 s 속도를 출력한다(어느 시나리오가 실제와 맞는지 보는 보정 검사).
usage: calib_gap.py <plan.pkl>   (sim_jerk.py, run_gap.py 와 같은 폴더, pytest_ci_setup.sh 로 만든 repo 환경에서 실행)
260cha 결과: A 는 지연 0.35 s 에서 RMSE 0.12(그 지연이 A, J=20 에 맞춘 값이라 일부 순환), G 는 어떤 지연에서도 0.37 이상(0.10 s 에서 최소)."""
import sys, pickle
import numpy as np
import sim_jerk as S
import run_gap as R
from openpilot.common.prefix import OpenpilotPrefix

plan = pickle.load(open(sys.argv[1], 'rb')); df, dev = plan['df'], plan['params']
inp = S.build_inputs(df, 5.0, 3.4)
valid = df.r_status.values.astype(bool) & (df.r_dRel.values > 1.0)
t_log, v_log = df.t.values, df.vEgo.values
print('log v @10.85: %.2f' % np.interp(10.85, t_log, v_log))
with OpenpilotPrefix():
  for d in [0.10, 0.20, 0.30, 0.35, 0.45]:
    R.S.DELAY_S = d
    out = []
    for sc in ['G', 'A']:
      r = R.run(dev, inp, valid, 20, sc)
      m = (r.t >= 8.0) & (r.t <= 11.5)
      rm = np.sqrt(np.mean((r.v[m].values - np.interp(r.t[m].values, t_log, v_log)) ** 2))
      i = (r.t - 10.85).abs().idxmin()
      out.append('%s v10.85=%.2f rmse(8-11.5)=%.2f' % (sc, r.v[i], rm))
    print('delay %.2f | ' % d + ' | '.join(out), flush=True)
