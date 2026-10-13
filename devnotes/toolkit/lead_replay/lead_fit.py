#!/usr/bin/env python3
"""lead_fit.py (276cha, lead15.py 복원) 앞차 감속 시작 시각/크기 역산.
119.0초(기본 T) 레이더 값에 앞차 위치·속도를 고정하고, ts부터 일정 감속 a(<0), 그 전은 등속이라고 놓은 궤적 `lead_traj(ts, a)`를 만든다.
`python3 lead_fit.py [t_lo t_hi]`: 비전 단독 프레임(기본 116.7~118.9초)의 dRel/vLead에 soft_l1 최소제곱으로 (ts, a)를 맞춘다.
275cha/276cha 로그에서는 비전 거리가 흔들려(절대위치 표준편차 15 m) 해가 경계(a=-6)에 붙었고 적합이 나빴다(RMS 6.1 m). 그래서 이 적합값 대신
레이더 인계 시점 값에 고정하고 ts를 116.1/116.8/117.5로 놓은 민감도 3점을 `cl_replay.py`에서 썼다. 적합 결과는 참고용이다.
환경변수 LR_PKL(기본 ./log_lead.pkl). 결과 leadfit.pkl. 의존: numpy pandas scipy. 실차 검증 아님."""
import sys, os, pickle
import numpy as np, pandas as pd
from scipy.optimize import least_squares
D = pickle.load(open(os.environ.get('LR_PKL', 'log_lead.pkl'), 'rb')); rs, cs = D['rs'], D['cs']
t = rs.t.values
tc = cs.t.values; xe_c = np.concatenate([[0], np.cumsum(np.diff(tc) * cs.vEgo.values[1:])])
xego = lambda tt: np.interp(tt, tc, xe_c)


def lead_traj(ts, a, T=119.0):
    """x_lead_abs(t), v_lead(t): T초 레이더 값에 고정, ts부터 일정 감속 a(<0), 그 전은 등속"""
    k = np.abs(t - T).argmin(); v119 = rs.l1_vLead.values[k]; x119 = xego(t[k]) + rs.l1_dRel.values[k]; tk = t[k]
    v0 = v119 - a * (tk - ts)

    def v(tt):
        tt = np.asarray(tt, float)
        return np.where(tt < ts, v0, v119 + a * (tt - tk)).clip(0)

    def x(tt):
        tt = np.asarray(tt, float); out = np.empty_like(tt)
        for i, q in enumerate(tt):
            g = np.linspace(q, tk, 200); out[i] = x119 - np.trapezoid(v(g), g)
        return out
    return x, v


if __name__ == '__main__':
    lo, hi = (float(sys.argv[1]), float(sys.argv[2])) if len(sys.argv) >= 3 else (116.7, 118.9)
    vis = rs[(rs.t >= lo) & (rs.t <= hi) & rs.l1_status & ~rs.l1_radar]
    tv = vis.t.values; dv = vis.l1_dRel.values; vv = vis.l1_vLead.values

    def res(p):
        ts, a = p; x, v = lead_traj(ts, a)
        e1 = (x(tv) - xego(tv)) - dv; e2 = (v(tv) - vv) * 3
        return np.concatenate([e1, e2])
    best = None
    for ts0 in (115.5, 116.3, 117.0):
        r = least_squares(res, [ts0, -3.5], loss='soft_l1', f_scale=3.0, bounds=([114.5, -6], [118.5, -1.0]))
        if best is None or r.cost < best.cost:
            best = r
    ts, a = best.x; print('fit ts=%.2f a=%.2f cost=%.1f' % (ts, a, best.cost))
    for tsx, ax in ((ts, a), (116.8, -3.6), (116.1, -3.6), (116.8, -2.0)):
        x, v = lead_traj(tsx, ax); r = res([tsx, ax])
        print('ts=%.2f a=%.2f  rms dRel err %.1f m, v lead at 116.0/117/118/118.5: %s' % (tsx, ax, np.sqrt(np.mean(r[:len(tv)] ** 2)), np.round(v([116.0, 117, 118, 118.5]), 1)))
    pickle.dump((ts, a), open('leadfit.pkl', 'wb'))
