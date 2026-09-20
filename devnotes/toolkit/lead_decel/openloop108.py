#!/usr/bin/env python3
"""108차 계속2: 플래너 내부 상태(x0, 게이트 g)를 로그에서 재구성한 open-loop 단발 검증.
폴더 배치: ../toolkit(mpc_replica.py), out/ego2.pkl(ego_extract2.py). 실차 검증 아님(로그 대조).
재구성 근거(67b0aa9 코드):
 - x0[2] = a_desired = interp(0.05, CONTROL_N_T_IDX, 직전 cycle의 longitudinalPlan.accels)
 - x0[1] = v_desired_filter.x : x=(1-a)x+a*vEgo (a=0.05/2.05), 이후 x += 0.05*(a_des+a_des_prev)/2
 - prev_a = interp(T+0.05, T, 직전 cycle a_solution)  (accels는 0~2.5s만 기록, a_change 가중치는 2s까지라 영향 없음)
 - 게이트 g: long_mpc._gate_raw / process_lead 그대로(GATE_M 1.0/1.2, GATE_T 6/12, 하강 시정수 1s)
 - a_min = ACCEL_MIN = -4.0, a_change = 로그 aChangeCost
usage: python3 openloop108.py <seg> <t_from> <t_to> [tag]
"""
import sys, os, numpy as np, pandas as pd
sys.path.insert(0, '../toolkit')
import mpc_replica as R

DT = 0.05
ALPHA = DT / (2.0 + DT)
CN_T = np.array([10.0 * ((i / 32) ** 2) for i in range(17)])   # ModelConstants.T_IDXS[:17]
ACCEL_MIN = -4.0
GATE_M_LO, GATE_M_HI, GATE_T_LO, GATE_T_HI, GATE_TAU_G, GATE_TAU_TARGET = 1.0, 1.2, 6.0, 12.0, 1.0, 1.5
STOP_EQ_CB = 2.5   # get_stopped_equivalence_factor는 항상 COMFORT_BRAKE=2.5 (사용자 튜닝값 무관)


def gate_raw(gap, v_ego, v_lead, tf, cb, sd):
    d_comf = v_ego ** 2 / (2 * cb) + tf * v_ego + sd
    m = (gap + max(v_lead, 0.0) ** 2 / (2 * STOP_EQ_CB)) / max(0.8 * d_comf, 1e-3)
    g = float(np.clip((GATE_M_HI - m) / (GATE_M_HI - GATE_M_LO), 0., 1.))
    if v_ego - v_lead > 0.1:
        ttc = gap / (v_ego - v_lead)
        g = max(g, float(np.clip((GATE_T_HI - ttc) / (GATE_T_HI - GATE_T_LO), 0., 1.)))
    return g, m


def lead_traj(dRel, vLead, aLeadK, tau, v_ego):
    """long_mpc.process_lead 후반부(클립 + extrapolate_lead). STOP_EQ_CB 사용은 obstacle()에서."""
    min_x = ((v_ego + vLead) / 2) * (v_ego - vLead) / (-ACCEL_MIN * 2)
    x = float(np.clip(dRel, min_x, 1e8)); v = float(np.clip(vLead, 0.0, 1e8)); a = float(np.clip(aLeadK, -10., 5.))
    return R.extrapolate_lead(x, v, a, tau)


def run(seg, t_from, t_to, variants):
    D = pd.read_pickle('out/ego2.pkl')
    cs, lp, rs, sw = D['cs'], D['lp'], D['rs'], D['sw']
    c = cs[cs.seg == seg].sort_values('t').reset_index(drop=True)
    l = lp[lp.seg == seg].sort_values('t').reset_index(drop=True)
    r = rs[rs.seg == seg].sort_values('t').reset_index(drop=True)
    m = pd.merge_asof(l, r, on='t', direction='nearest', tolerance=0.01, suffixes=('', '_r')).dropna(subset=['dRel']).reset_index(drop=True)
    import os
    _sh = int(os.environ.get('RSHIFT', '0'))
    if _sh:
        _cols = ['status','dRel','vRel','vLead','aLeadK','vLeadK','aLeadTau','status2','dRel2','vRel2','vLead2','aLeadK2','aLeadTau2']
        m[_cols] = m[_cols].shift(_sh); m = m.dropna(subset=['dRel']).reset_index(drop=True)
    tseg0 = m.t.iloc[0]
    m['ts'] = m.t - tseg0            # 세그먼트 내 상대 시간
    m['vE'] = np.interp(m.t, c.t, c.vEgo)
    accs = np.array([np.array(a, dtype=float) for a in m.accels])
    a_des = np.array([np.interp(DT, CN_T, a) for a in accs])          # 그 cycle의 a_desired(다음 cycle의 x0[2])
    # v_desired_filter 재구성 (초기값은 첫 vEgo, 수 초 지나면 수렴)
    vf = float(m.vE.iloc[0]); v0s = np.zeros(len(m)); a0s = np.zeros(len(m))
    for i in range(len(m)):
        vf = (1 - ALPHA) * vf + ALPHA * m.vE.iloc[i]
        v0s[i] = max(vf, 0.0)
        a0s[i] = a_des[i - 1] if i > 0 else a_des[0]
        ad_prev = a_des[i - 1] if i > 0 else a_des[0]
        vf = max(vf, 0.0) + DT * (a_des[i] + ad_prev) / 2.0
    m['v0'] = v0s; m['a0'] = a0s
    # 게이트 재구성(각 variant의 cb/sd로 별도) + swaglog 대조
    out = []
    for vname, (cb, sd, use_gate, tf_scale) in variants.items():
        g_state = [1.0, 1.0]; gs0 = np.zeros(len(m)); rows = []
        for i in range(len(m)):
            row = m.iloc[i]; v0 = row.v0; tf = row.tFollow * tf_scale
            xs = []
            for k, (st, d, vl, al, tau) in enumerate(((row.status, row.dRel, row.vLead, row.aLeadK, row.aLeadTau),
                                                       (row.status2, row.dRel2, row.vLead2, row.aLeadK2, row.aLeadTau2))):
                if not st:
                    g_state[k] = 1.0; continue
                g_raw, _ = gate_raw(d, v0, vl, tf, cb, sd)
                g = g_raw if g_raw > g_state[k] else g_state[k] + (g_raw - g_state[k]) * DT / GATE_TAU_G
                g_state[k] = g
                tau_e = g * tau + (1 - g) * GATE_TAU_TARGET if use_gate else tau
                xt, vt = lead_traj(d, vl, al, tau_e, v0)
                xs.append(xt + vt ** 2 / (2 * STOP_EQ_CB))       # obstacle: 리드 정지환산은 cb=2.5 고정
            gs0[i] = g_state[0]
            if not (t_from <= row.ts <= t_to) or not xs or i == 0:
                continue
            xo = np.min(np.vstack(xs), axis=0)
            prev_a = np.interp(R.T + DT, R.T, np.interp(R.T, CN_T, accs[i - 1]))
            try:
                X, J = R.solve(v0, row.a0, xo, tf, prev_a, jerk_factor=1.0, a_change=float(row.aChangeCost) if row.aChangeCost > 0 else 200.,
                               cb=cb, sd=sd, a_min=ACCEL_MIN)
                pred17 = np.interp(CN_T, R.T, X[2]); real17 = accs[i]
                rows.append(dict(variant=vname, ts=row.ts, v0=v0, a0=row.a0, g=g_state[0], pred_first=float(np.interp(DT, CN_T, pred17)),
                                 real_first=float(a_des[i]), pred_min=float(pred17.min()), real_min=float(real17.min()),
                                 rmse=float(np.sqrt(np.mean((pred17 - real17) ** 2)))))
            except Exception as e:
                rows.append(dict(variant=vname, ts=row.ts, err=str(e)[:40]))
        m['g_' + vname] = gs0
        out.append(pd.DataFrame(rows))
    # swaglog g 대조
    s = sw[(sw.seg == seg) & (sw.idx == 0)].copy(); s['ts'] = s.t - tseg0
    gcmp = []
    for _, sr in s.iterrows():
        if not (t_from - 1 <= sr.ts <= t_to + 1): continue
        j = int(np.argmin(np.abs(m.ts.values - sr.ts)))
        gcmp.append(dict(ts=round(sr.ts, 2), g_swaglog=sr.g, **{('g_' + v): round(m['g_' + v].iloc[j], 2) for v in variants}))
    return pd.concat(out, ignore_index=True), pd.DataFrame(gcmp)


if __name__ == '__main__':
    seg = int(sys.argv[1]); t0 = float(sys.argv[2]); t1 = float(sys.argv[3]); tag = sys.argv[4] if len(sys.argv) > 4 else f'{seg}'
    variants = {
        'P':      (2.4, 7.0, True, 1.0),     # params_backup.json 값(comfortBrake 2.4, StopDistanceCarrot 700), 게이트 재구성
        'Pnogate': (2.4, 7.0, False, 1.0),   # 같은 값, 게이트 무시(기존 toolkit 방식)
        'Old':    (2.47, 11.6, True, 1.0),   # 107차 역산값
    }
    if os.environ.get('ONLYP'): variants = {'P': variants['P']}
    res, gcmp = run(seg, t0, t1, variants)
    res.to_pickle(f'out/ol108_{tag}.pkl')
    pd.set_option('display.width', 200)
    print('== swaglog g 대조 =='); print(gcmp.to_string(index=False))
    ok = res.dropna(subset=['rmse'])
    print('== variant별 요약 (cycle 수, RMSE 평균, 첫 스텝 |오차| 평균/최대, 최솟값 오차 평균) ==')
    for v, d in ok.groupby('variant'):
        e1 = (d.pred_first - d.real_first).abs(); em = d.pred_min - d.real_min
        print(f'{v:8s} n={len(d):3d} rmse={d.rmse.mean():.3f} first|e|={e1.mean():.3f}/{e1.max():.3f} min_err(mean)={em.mean():+.3f} fails={res[res.variant==v].shape[0]-len(d)}')
