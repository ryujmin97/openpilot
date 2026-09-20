#!/usr/bin/env python3
"""108차 계속2: 보정된 폐루프 what-if (게이트 후보별). 실차 검증 아님, acados 실물 아님.
openloop108.py와 같은 재구성 규칙 + 폐루프: 리드(vLead/aLeadK/aLeadTau/status)는 로그 그대로 외생 입력,
리드 거리는 시뮬 자차 기준으로 적분, 자차는 1차 지연(lag=0.3 s, 로그 accelCmd->aEgo 적합값) 액추에이터.
planner 출력: a_cmd = interp(action_t=0.25 = LongActuatorDelay 0.2 + DT_MDL 0.05, T, a_solution) (로그 aTargetBase와 RMSE 0.024).
usage: python3 closedloop108.py <seg> <t_from> <t_to> <variant> [tag]   variant: none | M105 | M0.8/1.0 | M0.9/1.1
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, '../toolkit')
import mpc_replica as R
from openloop108 import DT, ALPHA, CN_T, ACCEL_MIN, GATE_T_LO, GATE_T_HI, GATE_TAU_G, GATE_TAU_TARGET, STOP_EQ_CB, lead_traj

CB, SD = 2.4, 7.0
ACT_T, LAG = 0.25, 0.3
VARS = {'none': None, 'M105': (1.0, 1.2), 'M0.8/1.0': (0.8, 1.0), 'M0.9/1.1': (0.9, 1.1)}

import os
J_MAX = float(os.environ.get('J_MAX', '999'))   # m/s^3, 999=비활성(무제한, 기존과 동일)


def gate_raw(gap, v_ego, v_lead, tf, m_lo, m_hi):
    d_comf = v_ego ** 2 / (2 * CB) + tf * v_ego + SD
    m = (gap + max(v_lead, 0.0) ** 2 / (2 * STOP_EQ_CB)) / max(0.8 * d_comf, 1e-3)
    g = float(np.clip((m_hi - m) / (m_hi - m_lo), 0., 1.))
    if v_ego - v_lead > 0.1:
        ttc = gap / (v_ego - v_lead)
        g = max(g, float(np.clip((GATE_T_HI - ttc) / (GATE_T_HI - GATE_T_LO), 0., 1.)))
    return g, m


def simulate(seg, t_from, t_to, variant):
    D = pd.read_pickle('out/ego2.pkl')
    cs, lp, rs = D['cs'], D['lp'], D['rs']
    c = cs[cs.seg == seg].sort_values('t').reset_index(drop=True)
    l = lp[lp.seg == seg].sort_values('t').reset_index(drop=True)
    r = rs[rs.seg == seg].sort_values('t').reset_index(drop=True)
    m = pd.merge_asof(l, r, on='t', direction='nearest', tolerance=0.01, suffixes=('', '_r')).dropna(subset=['dRel']).reset_index(drop=True)
    import os
    _sh = int(os.environ.get('RSHIFT', '0'))
    if _sh:
        _cols = ['status','dRel','vRel','vLead','aLeadK','vLeadK','aLeadTau','status2','dRel2','vRel2','vLead2','aLeadK2','aLeadTau2']
        m[_cols] = m[_cols].shift(_sh); m = m.dropna(subset=['dRel']).reset_index(drop=True)
    tseg0 = m.t.iloc[0]; m['ts'] = m.t - tseg0
    m['vE'] = np.interp(m.t, c.t, c.vEgo)
    m['aE'] = np.interp(m.t, c.t, pd.Series(c.aEgo.values).rolling(5, center=True, min_periods=1).median().values)
    accs = np.array([np.array(a, dtype=float) for a in m.accels])
    a_des = np.array([np.interp(DT, CN_T, a) for a in accs])
    gp = VARS[variant]
    # --- 시작 상태: t_from 직전까지 로그 기반 재구성(M105 기준 게이트) ---
    i0 = int(np.argmax(m.ts.values >= t_from))
    vf = float(m.vE.iloc[0]); g_state = [1.0, 1.0]
    for i in range(i0):
        vf = (1 - ALPHA) * vf + ALPHA * m.vE.iloc[i]
        ad_prev = a_des[i - 1] if i > 0 else a_des[0]
        row = m.iloc[i]
        for k, (st, d, vl) in enumerate(((row.status, row.dRel, row.vLead), (row.status2, row.dRel2, row.vLead2))):
            if not st: g_state[k] = 1.0; continue
            g_raw, _ = gate_raw(d, max(vf, 0), vl, row.tFollow, 1.0, 1.2)
            g_state[k] = g_raw if g_raw > g_state[k] else g_state[k] + (g_raw - g_state[k]) * DT / GATE_TAU_G
        vf = max(vf, 0.0) + DT * (a_des[i] + ad_prev) / 2.0
    # 자차/플래너 초기 상태
    vE = float(m.vE.iloc[i0]); aE = float(m.aE.iloc[i0]); a_pl = float(a_des[i0 - 1])
    gap = [float(m.dRel.iloc[i0]), float(m.dRel2.iloc[i0])]
    prev_a = np.interp(R.T + DT, R.T, np.interp(R.T, CN_T, accs[i0 - 1]))
    out = []; warm = None
    a_cmd_rl = float(np.interp(ACT_T, R.T, np.interp(R.T, CN_T, accs[i0 - 1])))  # rate-limiter 초기상태
    idx = [j for j in range(i0, len(m)) if m.ts.iloc[j] <= t_to]
    for j in idx:
        row = m.iloc[j]; tf = row.tFollow
        vf = (1 - ALPHA) * vf + ALPHA * vE; v0 = max(vf, 0.0)
        xs = []; gcur = 1.0
        for k, (st, vl, al, tau) in enumerate(((row.status, row.vLead, row.aLeadK, row.aLeadTau),
                                               (row.status2, row.vLead2, row.aLeadK2, row.aLeadTau2))):
            if not st: g_state[k] = 1.0; continue
            if gp is None: g = 1.0
            else:
                g_raw, _ = gate_raw(gap[k], v0, vl, tf, gp[0], gp[1])
                g = g_raw if g_raw > g_state[k] else g_state[k] + (g_raw - g_state[k]) * DT / GATE_TAU_G
            g_state[k] = g
            if k == 0: gcur = g
            tau_e = g * tau + (1 - g) * GATE_TAU_TARGET
            xt, vt = lead_traj(gap[k], vl, al, tau_e, v0)
            xs.append(xt + vt ** 2 / (2 * STOP_EQ_CB))
        if xs:
            xo = np.min(np.vstack(xs), axis=0)
            X, J = R.solve(v0, a_pl, xo, tf, prev_a, jerk_factor=1.0,
                           a_change=float(row.aChangeCost) if row.aChangeCost > 0 else 200., cb=CB, sd=SD, a_min=ACCEL_MIN, warm=warm)
            warm = (X, J); asol = X[2]
        else:
            asol = np.full(len(R.T), 0.0)   # 리드 없음 구간은 이 도구의 대상이 아님
        a_cmd = float(np.interp(ACT_T, R.T, asol))
        a_des_new = float(np.interp(DT, CN_T, np.interp(CN_T, R.T, asol)))
        vf = max(vf, 0.0) + DT * (a_des_new + a_pl) / 2.0
        a_pl = a_des_new; prev_a = np.interp(R.T + DT, R.T, asol)
        # 출력단 rate limiter: MPC의 내부 가정(게이트/tau/tf)은 전혀 안 건드리고, 최종 실행 명령(a_cmd)이
        # '더 세지는 방향'으로만 서서히 강화(J_MAX m/s^3), 완화(덜 브레이크)는 즉시 반영.
        # MPC의 다음 cycle 재계획(prev_a/warm)은 원래 asol 그대로 사용 -> 계획 자체는 안 바뀜, 실제 실행만 늦게 따라감.
        if J_MAX < 900:
            lo = a_cmd_rl - J_MAX * DT
            a_cmd_rl = a_cmd if a_cmd >= a_cmd_rl else max(a_cmd, lo)
        else:
            a_cmd_rl = a_cmd
        out.append(dict(ts=row.ts, vE=vE, aE=aE, a_cmd=a_cmd_rl, gap=gap[0], vL=row.vLead, g=gcur,
                        real_aE=row.aE, real_vE=row.vE, real_gap=row.dRel))
        aE += (a_cmd_rl - aE) * DT / LAG
        for k, vl in enumerate((row.vLead, row.vLead2)):
            gap[k] += (vl - vE) * DT
        vE = max(0.0, vE + aE * DT)
    return pd.DataFrame(out)


def summarize(d):
    hw = d.gap / np.maximum(d.vE, 1.0); ttc = np.where(d.vE - d.vL > 0.1, d.gap / np.maximum(d.vE - d.vL, 1e-3), 99.)
    return dict(aEmin=d.aE.min(), aCmdMin=d.a_cmd.min(), minGap=d.gap.min(), minHw=hw.min(), minTTC=float(np.min(ttc)), gMax=d.g.max(),
                vEend_kph=d.vE.iloc[-1] * 3.6, real_aEmin=d.real_aE.min(), real_vEend_kph=d.real_vE.iloc[-1] * 3.6, real_minGap=d.real_gap.min())


if __name__ == '__main__':
    seg = int(sys.argv[1]); t0 = float(sys.argv[2]); t1 = float(sys.argv[3]); var = sys.argv[4]; tag = sys.argv[5] if len(sys.argv) > 5 else f'{seg}'
    d = simulate(seg, t0, t1, var)
    d.to_pickle(f'out/cl108_{tag}_{var.replace("/", "-")}.pkl')
    s = summarize(d)
    print(f'{var:9s} ' + ' '.join(f'{k}={v:.2f}' for k, v in s.items()), flush=True)
