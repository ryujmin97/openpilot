#!/usr/bin/env python3
"""plant_fit.py (276cha 복원) 자차 1차 플랜트(시정수 tau + 순수 지연 delay)를 로그 명령(carControl.actuators.accel)과 실제 vEgo에 맞춘다.
t 110~124초(인자로 변경)를 0.01초 격자로 보간해 tau 0.1~1.0, delay 0~0.6초 격자 탐색, vEgo RMSE 상위 5개를 출력한다.
275cha/276cha 로그 결과: tau 0.40/delay 0.0, RMSE 0.236 m/s(상위 근접값 tau 0.35/delay 0.05 등). `cl_replay.py`의 TAU, DELAY에 반영했다(0.4, 0.0).
환경변수 LR_PKL(기본 ./log_lead.pkl). 결과 plant.pkl. 실차 검증 아님."""
import sys, os, pickle
import numpy as np
D = pickle.load(open(os.environ.get('LR_PKL', 'log_lead.pkl'), 'rb')); cs, cc = D['cs'], D['cc']
lo, hi = (float(sys.argv[1]), float(sys.argv[2])) if len(sys.argv) >= 3 else (110.0, 124.0)
tt = np.arange(lo, hi, 0.01)
vE = np.interp(tt, cs.t, cs.vEgo); acc = np.interp(tt, cc.t, cc.accel)
best = []
for tau in np.arange(0.1, 1.01, 0.05):
    for dl in np.arange(0.0, 0.61, 0.05):
        v = vE[0]; a = 0.0; q = [0.0] * int(round(dl / 0.01)); out = []
        for k in range(len(tt)):
            q.append(acc[k]); c = q.pop(0); a += (c - a) * (1 - np.exp(-0.01 / tau)); v = max(0, v + a * 0.01); out.append(v)
        best.append((float(np.sqrt(np.mean((np.array(out) - vE) ** 2))), float(tau), float(dl)))
best.sort(); print([(round(r, 3), round(t, 2), round(d, 2)) for r, t, d in best[:5]])
pickle.dump(best[0], open('plant.pkl', 'wb'))
