"""리드 감속 게이팅 후보 평가(폐루프, mpc_replica 사용). 실차 검증 아님, acados 실물 아님.
게이트 g in [0,1] (1=현행 투사 그대로, 0=투사 약화): 관측 가능한 값만 사용(시간차 h=gap/vE, TTC=gap/(vE-vL)).
  g_h=clip((h_hi-h)/(h_hi-h_lo)), g_t=clip((ttc_hi-ttc)/(ttc_hi-ttc_lo)), g=max. 상승 즉시/하강 시정수 tau_g.
  약화 방식: tau_used=g*tau_log+(1-g)*1.5, v_in=g*vL+(1-g)*LPF(vL, lpf_tau).
사용: gating_eval.py <tag> <event_idx,...> <gap_offsets,...> <variants,...>   결과 out/gate_<tag>.pkl
  event_idx: events.py 표의 idx(리드 감속 이벤트), gap_offsets: 초기 거리에 더할 m(스트레스 시나리오, 예: 0,-10,-20), variants: CANDS 키.
후보: base(현행) / G1,G2,G3(투사 감쇠+저역통과 동시) / G1L,G2L(저역통과만) / G1T,G2T(투사 감쇠만). 별칭 A=G1T, B=G2T(98차 채택).
한계: mpc_replica(acados 실물 아님), 리드는 로그 재생, 액추에이터 1차 지연 가정, v1 코드 기록 로그의 tFollow 사용. 실차 검증 아님. 결과 해석은 WIP.md 98차.
시뮬 창: 이벤트 시작 -1 s ~ +9 s(SIM_PRE/SIM_POST). 폐루프 1회(약 10 s 구간)가 CPU 1코어 기준 약 10 s. 백그라운드로 돌릴 때는 setsid nohup 사용(호출이 끝나면 죽는 환경이 있음).
"""
import sys, os, time, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mpc_replica as R
M = pd.read_pickle('out/merged.pkl'); E = pd.read_pickle('out/events.pkl')
LPF_TAU, TAU_G, TAU_TARGET = 1.0, 1.0, 1.5
SIM_PRE, SIM_POST = 1.0, 9.0
CANDS = {
  'base': None,
  'G1':  dict(h_lo=1.2, h_hi=2.0, t_lo=5.0, t_hi=9.0,  mode='both'),
  'G2':  dict(h_lo=1.5, h_hi=2.2, t_lo=6.0, t_hi=12.0, mode='both'),
  'G3':  dict(h_lo=1.2, h_hi=1.8, t_lo=None, t_hi=None, mode='both'),   # 시간차만
  'G1L': dict(h_lo=1.2, h_hi=2.0, t_lo=5.0, t_hi=9.0,  mode='lpf'),
  'G2L': dict(h_lo=1.5, h_hi=2.2, t_lo=6.0, t_hi=12.0, mode='lpf'),
  'G1T': dict(h_lo=1.2, h_hi=2.0, t_lo=5.0, t_hi=9.0,  mode='tau'),
  'G2T': dict(h_lo=1.5, h_hi=2.2, t_lo=6.0, t_hi=12.0, mode='tau'),
}
CANDS['A'] = CANDS['G1T']; CANDS['B'] = CANDS['G2T']   # B안 = 98차 채택 후보
def gate_raw(c, gap, vE, vL):
    h = gap / max(vE, 1.0)
    g = float(np.clip((c['h_hi'] - h) / (c['h_hi'] - c['h_lo']), 0., 1.))
    if c['t_lo'] is not None and vE - vL > 0.1:
        ttc = gap / (vE - vL)
        g = max(g, float(np.clip((c['t_hi'] - ttc) / (c['t_hi'] - c['t_lo']), 0., 1.)))
    return g
def simulate(ev, cand, gap_off=0.0, jf=1.0, lag=0.35, act_t=0.4, cb=2.47, sd=11.6, dt=0.05):
    c = CANDS[cand]; m = M[ev.pair]
    w = m[(m.t >= ev.t_start - SIM_PRE) & (m.t <= ev.t_start + SIM_POST)].reset_index(drop=True)   # 시뮬 창: 이벤트 시작 -1 s ~ +9 s
    vE, aE = w.vEgo[0], w.aEgo[0]; gap = w.dRel[0] + gap_off
    prev_a = np.full(13, w.accels[0][0]); a_pl = w.accels[0][0]
    vLf = w.vLead[0]; g = None; out = []; warm = None
    for i in range(len(w)):
        r = w.iloc[i]; vL, aL, tau = r.vLead, r.aLeadK, r.aLeadTau
        vLf += (vL - vLf) * dt / LPF_TAU
        if c is None: gg = 1.0; tau_use, v_in = tau, vL
        else:
            graw = gate_raw(c, gap, vE, vL)
            g = graw if (g is None or graw > g) else g + (graw - g) * dt / TAU_G
            gg = g
            tau_use = gg * tau + (1 - gg) * TAU_TARGET if c['mode'] in ('tau', 'both') else tau
            v_in = gg * vL + (1 - gg) * vLf if c['mode'] in ('lpf', 'both') else vL
        xt, vt = R.process_lead(gap, v_in, aL, tau_use, vE)
        X, J = R.solve(vE, a_pl, R.obstacle(xt, vt, cb), r.tFollow, prev_a, jerk_factor=jf, cb=cb, sd=sd, warm=warm)
        warm = (X, J)
        a_cmd = float(np.interp(act_t, R.T, X[2])); a_pl = float(np.interp(dt, R.T, X[2]))
        prev_a = np.interp(R.T + dt, R.T, X[2])
        ttc = gap / (vE - vL) if vE - vL > 0.1 else np.inf
        out.append((r.t, vE * 3.6, vL * 3.6, gap, aE, a_cmd, gg, gap / max(vE, 1.0), ttc))
        aE += (a_cmd - aE) * dt / lag; gap += (vL - vE) * dt; vE = max(0.0, vE + aE * dt)
    return pd.DataFrame(out, columns=['t', 'vE_kph', 'vL_kph', 'gap', 'aE', 'aCmd', 'g', 'hw', 'ttc'])
def summary(d):
    return dict(aEmin=d.aE.min(), minGap=d.gap.min(), minHw=d.hw.min(), minTTC=d.ttc.min(), gMax=d.g.max(), gMean=d.g.mean())
if __name__ == '__main__':
    tag = sys.argv[1]; idxs = [int(x) for x in sys.argv[2].split(',')]
    offs = [float(x) for x in sys.argv[3].split(',')]; variants = sys.argv[4].split(',')
    res = {}
    for i in idxs:
        for off in offs:
            for v in variants:
                t0 = time.time(); d = simulate(E.loc[i], v, off); s = summary(d); res[(i, off, v)] = (d, s)
                print(f"#{i} off={off:+.0f} {v:4s}: aEmin={s['aEmin']:6.2f} minGap={s['minGap']:5.1f} minHw={s['minHw']:4.2f} "
                      f"minTTC={s['minTTC']:6.1f} gMax={s['gMax']:.2f} gMean={s['gMean']:.2f} ({time.time()-t0:.0f}s)", flush=True)
    pd.to_pickle(res, f'out/gate_{tag}.pkl')
