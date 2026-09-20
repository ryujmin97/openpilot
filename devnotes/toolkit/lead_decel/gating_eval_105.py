#!/usr/bin/env python3
"""105차 리드 감속 게이트(margin_ratio + TTC 하이브리드) 폐루프 평가. gating_eval.py의 확장판. 실차 검증 아님, acados 실물 아님.
gating_eval.py(시간차 h 기반 A/B안)의 simulate()에 105차 carrot-ryu long_mpc.py 게이트(`_gate_raw`)를 후보 'M105'로 추가했다.
  m = (gap + vLead^2/(2*2.5)) / (0.8 * d_comf(vEgo, tFollow, cb, sd)),  d_comf = vEgo^2/(2*cb) + tFollow*vEgo + sd
  g = max( clip((M_HI-m)/(M_HI-M_LO)), TTC 성분 clip((T_HI-ttc)/(T_HI-T_LO)) ),  M 1.0/1.2, T 6/12 s. 상승 즉시/하강 시정수 1.0 s.
  약화: tau_used = g*aLeadTau + (1-g)*1.5 (투사 감쇠만, 저역통과 없음 = 실제 코드와 동일).
  (실제 코드는 정지환산거리에 모듈 상수 COMFORT_BRAKE=2.5, 쾌적거리에 carrot.comfort_brake를 쓴다 -> 여기서도 동일하게 분리했다.)
사용: gating_eval_105.py <tag> <event_idx,...> <gap_offsets,...> [variants,...]   결과 out/gate_<tag>.pkl
  variants 기본값 base,B,M105 (base/B는 gating_eval.CANDS 그대로 -> 같은 조건 비교). 리드 게이트 상수는 아래 M105 dict에서 수정(튜닝용).
필요: 작업 폴더의 out/merged.pkl, out/events.pkl (merge_lead_series.py -> events.py 순서), 같은 폴더의 gating_eval.py/mpc_replica.py.
한계: mpc_replica(acados 실물 아님, 로그 대비 RMSE 약 0.22 m/s²), 리드는 로그 재생(외생), 액추에이터 1차 지연, 로그의 tFollow 사용(cb=2.47, sd=11.6은 desiredDistance 역산값). 실차 검증 아님.
백그라운드로 돌릴 때는 setsid nohup 사용. 폐루프 1회 약 9 s(CPU 1코어).
"""
import sys, os, time, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mpc_replica as R
import gating_eval as G            # M, E, CANDS, gate_raw(base/A/B용), summary, LPF_TAU/TAU_G/TAU_TARGET/SIM_PRE/SIM_POST 재사용

M105 = dict(m_lo=1.0, m_hi=1.2, t_lo=6.0, t_hi=12.0, mode='tau', kind='margin')   # long_mpc.py GATE_M_*/GATE_T_*와 일치시킬 것
COMFORT_BRAKE_STOPEQ = 2.5                                                          # long_mpc.py 모듈 상수 COMFORT_BRAKE(정지환산거리용)
CANDS = dict(G.CANDS); CANDS['M105'] = M105

def gate_margin(c, gap, vE, vL, tf, cb, sd):
    d_comf = R.d_comf(vE, tf, cb, sd)
    m = (gap + max(vL, 0.0) ** 2 / (2 * COMFORT_BRAKE_STOPEQ)) / max(0.8 * d_comf, 1e-3)
    g = float(np.clip((c['m_hi'] - m) / (c['m_hi'] - c['m_lo']), 0., 1.))
    if vE - vL > 0.1:
        g = max(g, float(np.clip((c['t_hi'] - gap / (vE - vL)) / (c['t_hi'] - c['t_lo']), 0., 1.)))
    return g, m

def simulate(ev, cand, gap_off=0.0, jf=1.0, lag=0.35, act_t=0.4, cb=2.47, sd=11.6, dt=0.05):
    """gating_eval.simulate와 동일한 루프. 차이: 후보가 kind='margin'이면 gate_margin(tFollow 필요)을 쓰고 m 열을 추가로 기록."""
    c = CANDS[cand]; m_ = G.M[ev.pair]
    w = m_[(m_.t >= ev.t_start - G.SIM_PRE) & (m_.t <= ev.t_start + G.SIM_POST)].reset_index(drop=True)
    vE, aE = w.vEgo[0], w.aEgo[0]; gap = w.dRel[0] + gap_off
    prev_a = np.full(13, w.accels[0][0]); a_pl = w.accels[0][0]
    vLf = w.vLead[0]; g = None; out = []; warm = None
    for i in range(len(w)):
        r = w.iloc[i]; vL, aL, tau = r.vLead, r.aLeadK, r.aLeadTau
        vLf += (vL - vLf) * dt / G.LPF_TAU
        mm = np.nan
        if c is None: gg = 1.0; tau_use, v_in = tau, vL
        else:
            if c.get('kind') == 'margin': graw, mm = gate_margin(c, gap, vE, vL, r.tFollow, cb, sd)
            else: graw = G.gate_raw(c, gap, vE, vL)
            g = graw if (g is None or graw > g) else g + (graw - g) * dt / G.TAU_G
            gg = g
            tau_use = gg * tau + (1 - gg) * G.TAU_TARGET if c['mode'] in ('tau', 'both') else tau
            v_in = gg * vL + (1 - gg) * vLf if c['mode'] in ('lpf', 'both') else vL
        xt, vt = R.process_lead(gap, v_in, aL, tau_use, vE)
        X, J = R.solve(vE, a_pl, R.obstacle(xt, vt, cb), r.tFollow, prev_a, jerk_factor=jf, cb=cb, sd=sd, warm=warm)
        warm = (X, J)
        a_cmd = float(np.interp(act_t, R.T, X[2])); a_pl = float(np.interp(dt, R.T, X[2]))
        prev_a = np.interp(R.T + dt, R.T, X[2])
        ttc = gap / (vE - vL) if vE - vL > 0.1 else np.inf
        out.append((r.t, vE * 3.6, vL * 3.6, gap, aE, a_cmd, gg, gap / max(vE, 1.0), ttc, mm))
        aE += (a_cmd - aE) * dt / lag; gap += (vL - vE) * dt; vE = max(0.0, vE + aE * dt)
    return pd.DataFrame(out, columns=['t', 'vE_kph', 'vL_kph', 'gap', 'aE', 'aCmd', 'g', 'hw', 'ttc', 'm'])

if __name__ == '__main__':
    tag = sys.argv[1]; idxs = [int(x) for x in sys.argv[2].split(',')]
    offs = [float(x) for x in sys.argv[3].split(',')]
    variants = (sys.argv[4] if len(sys.argv) > 4 else 'base,B,M105').split(',')
    res = {}
    for i in idxs:
        for off in offs:
            for v in variants:
                t0 = time.time(); d = simulate(G.E.loc[i], v, off); s = G.summary(d); res[(i, off, v)] = (d, s)
                print(f"#{i} off={off:+.0f} {v:4s}: aEmin={s['aEmin']:6.2f} minGap={s['minGap']:5.1f} minHw={s['minHw']:4.2f} "
                      f"minTTC={s['minTTC']:6.1f} gMax={s['gMax']:.2f} gMean={s['gMean']:.2f} ({time.time()-t0:.0f}s)", flush=True)
    pd.to_pickle(res, f'out/gate_{tag}.pkl')
