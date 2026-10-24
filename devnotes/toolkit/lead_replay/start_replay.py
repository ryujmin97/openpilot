#!/usr/bin/env python3
"""start_replay.py (311cha 후속) route 000004bf 세그먼트 77 정지 후 출발(앞차 따라 출발, 로그 238초) 재생. 실차 검증 아님.
scene76_plan.py(같은 폴더)의 Plan(플래너 MPC 호출부 사본)을 그대로 쓴다. 앞차는 로그 leadOne(vLead/aLeadK, 위치=xego_log+dRel)이다.
모드(첫 인자):
  ol     열린 루프(t 233~241초): 로그 자차 상태로 플래너 MPC를 돌려 로그 aTargetBase와 RMSE를 보고 설정 변형별 출발 램프(shouldStop 해제 시각, 0.2/0.4/0.6 m/s^2 도달 시각)를 비교
  cl     폐루프(t 235~262초, 자차 1차 플랜트 tau 0.35 delay 0.15): 변형 런(JerkCostEgo, a_change_cost_starting, tFollow, StopDistanceCarrot)별 속도/간격
  lar    폐루프, LeadAccelResponse 레벨 0/1/2/3/5
  gap    폐루프, 정차 간격 가정(자차를 앞차 로그 위치에서 off만큼 뒤에 세움): 2.7/5/7 m
  combo  폐루프, LeadAccelResponse 4/5와 tFollow 1.4/1.2 조합
사전 준비와 환경변수는 scene76_plan.py와 같다(LR_PKL, LP_PKL=extract_plan_ext.py로 150~300초 추출한 pkl, PYTHONPATH, CL_SIM_DIR). `python3 start_replay.py ol`
한계: 로그의 출발 한 건이다. 플랜트는 1차 지연이라 차가 움직이기 시작하는 문턱(명령 약 0.4 m/s^2)을 재현하지 못한다(재생 v240 0.87 대 로그 1.44 m/s, v250 7.25 대 6.98). 설정속도 15 m/s 가정, 모델 궤적 0, lead preview 없음.
"""
import sys, os, math, pickle
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scene76_plan as S
cl_sim = S.cl_sim; M = S.M; cs, rs, lp = S.cs, S.rs, S.lp
DT = S.DT


def _patched_carrot(jerk, jf, lar):
    orig = cl_sim.mk_carrot

    def mk(**k):
        c = orig(**k); c.jerkCostEgo = jerk; c.jerk_factor = jf; c.leadAccelResponse = lar
        return c
    cl_sim.mk_carrot = mk
    return orig


def run(t0=235.0, t1=262.0, tau=0.35, delay=0.15, tf=None, jerk=12.0, a_chg=150.0, sd=7.0, jf=1.0, vset=15.0, amax=1.4, lar=0, off=0.0):
    """폐루프. 자차는 정지(v=0)에서 시작, 앞차는 로그 궤적. off: 자차를 로그 위치보다 뒤에 세우는 거리(m)."""
    P = S.Plan(0.0, 0.0, sd=sd, vset=vset, a_chg=a_chg); P.lar = lar
    orig = _patched_carrot(jerk, jf, lar)
    v = 0.0; xe = S.xego_log(t0) - off; a_act = 0.0; q = [0.0] * int(round(delay / DT)); out = []
    try:
        for k in range(int(round((t1 - t0) / DT))):
            t = t0 + k * DT
            gap = S.xego_log(t) + float(S.R('l1_dRel', t)) - xe
            l1 = S.lead_in(t, gap, v, False, 'log')
            ab, ad, dd, mpc = P.step(v, a_act, l1, tf or S.ZOH(lp, 'tFollow', t) or 1.6, standstill=v < 0.02)
            ab = min(ab, amax)
            q.append(ab); cmd = q.pop(0)
            out.append((t, v, a_act, ab, gap, dd, float(l1.vLead), P.ss))
            a_act += (cmd - a_act) * (1 - math.exp(-DT / tau)); v = max(0., v + a_act * DT); xe += v * DT
    finally:
        cl_sim.mk_carrot = orig; P.close()
    return pd.DataFrame(out, columns='t v a a_base gap desired vlead ss'.split())


def ol(t0=233.0, t1=241.0, jerk=12.0, a_chg=150.0, tf=None, jf=1.0, lar=0, **kw):
    """열린 루프: 로그 vEgo/aEgo/앞차(dRel 로그 그대로)로 플래너 MPC를 돌린다."""
    orig = _patched_carrot(jerk, jf, lar)
    P = S.Plan(float(np.interp(t0, S.tc, cs.vEgo)), float(np.interp(t0, cs.t, cs.aEgo)), a_chg=a_chg, **kw); P.lar = lar
    out = []
    try:
        for k in range(int(round((t1 - t0) / DT))):
            t = t0 + k * DT; v = float(np.interp(t, S.tc, cs.vEgo)); a = float(np.interp(t, cs.t, cs.aEgo))
            l1 = S.lead_in(t, float(S.R('l1_dRel', t)), v, False, 'log')
            ab, ad, dd, _ = P.step(v, a, l1, tf or S.ZOH(lp, 'tFollow', t) or 1.6, standstill=v < 0.02)
            out.append((t, ab, P.ss, dd))
    finally:
        cl_sim.mk_carrot = orig; P.close()
    return pd.DataFrame(out, columns='t a_base ss desired'.split())


def ramp(df):
    d = df[df.t >= 236.0]; r = d[~d.ss]
    f = lambda x: (lambda q: round(float(q.t.iloc[0]), 2) if len(q) else float('nan'))(d[d.a_base >= x])
    at = lambda q: round(float(d.a_base.iloc[(d.t - q).abs().argmin()]), 2)
    return dict(release=round(float(r.t.iloc[0]), 2) if len(r) else float('nan'), t_a02=f(0.2), t_a04=f(0.4), t_a06=f(0.6), a_at_238=at(238.0), a_at_239=at(239.0))


def summ(df, name):
    f = lambda t, c='v': float(df[c].iloc[(df.t - t).abs().argmin()])
    mv = df[(df.t >= 238.0) & (df.t <= 246.0)]
    return dict(name=name, v240=round(f(240), 2), v243=round(f(243), 2), v246=round(f(246), 2), v250=round(f(250), 2), a_mean_238_246=round(float(mv.a.mean()), 2),
                a_base_max=round(float(df[(df.t > 238) & (df.t < 250)].a_base.max()), 2), gap246=round(f(246, 'gap'), 1), desired246=round(f(246, 'desired'), 1))


def log_row():
    g = lambda t: float(np.interp(t, S.tc, cs.vEgo))
    return dict(name='LOG', v240=round(g(240), 2), v243=round(g(243), 2), v246=round(g(246), 2), v250=round(g(250), 2),
                a_mean_238_246=round(float(cs[(cs.t >= 238) & (cs.t <= 246)].aEgo.mean()), 2), gap246=round(float(S.R('l1_dRel', 246)), 1))


if __name__ == '__main__':
    pd.set_option('display.width', 250)
    mode = sys.argv[1] if len(sys.argv) > 1 else 'ol'
    if mode == 'ol':
        LPX = S.LPX; lg = LPX[(LPX.t >= 236.0) & (LPX.t <= 240.0)]
        base = ol(); m = ((base.t >= 236.5) & (base.t <= 240)).values
        rmse = float(np.sqrt(np.mean((base.a_base.values[m] - np.interp(base.t.values, LPX.t.values, LPX.aTargetBase.values)[m]) ** 2)))
        print('열린 루프 a_target_base 대 로그 aTargetBase(236.5~240초) RMSE %.3f' % rmse)
        print('LOG aTargetBase 0.2/0.4 도달: %s, a@238 %.2f a@239 %.2f' % ([round(float(lg[lg.aTargetBase >= x].t.iloc[0]), 2) for x in (0.2, 0.4)],
              float(lg.aTargetBase.iloc[(lg.t - 238).abs().argmin()]), float(lg.aTargetBase.iloc[(lg.t - 239).abs().argmin()])))
        rows = []
        for nm, kw in [('base', {}), ('jerk20', dict(jerk=20.)), ('jerk8', dict(jerk=8.)), ('achg_start 50', dict(a_chg=50.)), ('achg_start 400', dict(a_chg=400.)),
                       ('tf1.2', dict(tf=1.2)), ('sd5', dict(sd=5.0)), ('LAR5', dict(lar=5))]:
            d = ramp(ol(**kw)); d['name'] = nm; rows.append(d)
        print(pd.DataFrame(rows).to_string(index=False))
    else:
        plans = {'cl': [('base', {}), ('jerk20', dict(jerk=20.)), ('jerk8', dict(jerk=8.)), ('achg50', dict(a_chg=50.)), ('tf1.2', dict(tf=1.2)), ('sd5', dict(sd=5.0))],
                 'lar': [('LAR%d' % L, dict(lar=L)) for L in (0, 1, 2, 3, 5)],
                 'gap': [('정차 2.7 m(로그)', dict(t0=233.0, off=0.0)), ('정차 5 m(가정)', dict(t0=233.0, off=2.3)), ('정차 7 m(가정)', dict(t0=233.0, off=4.3))],
                 'combo': [('LAR0 tf1.6', dict(t0=233.0)), ('LAR4', dict(t0=233.0, lar=4)), ('LAR5', dict(t0=233.0, lar=5)), ('LAR5+tf1.4', dict(t0=233.0, lar=5, tf=1.4)), ('LAR5+tf1.2', dict(t0=233.0, lar=5, tf=1.2))]}[mode]
        rows = [log_row()]
        for nm, kw in plans:
            df = run(**kw); d = summ(df, nm)
            if mode == 'gap':
                d.update(ramp(df)); d['gap236'] = round(float(df.gap.iloc[(df.t - 236.0).abs().argmin()]), 1)
            rows.append(d); print(nm, flush=True)
        print(pd.DataFrame(rows).to_string(index=False))
