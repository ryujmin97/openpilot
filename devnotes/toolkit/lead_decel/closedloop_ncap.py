#!/usr/bin/env python3
"""109차(제안, 미확정): 필요 감속(실시간 causal TTC/차간거리) 기반 명령 상한(need-cap) what-if.
closedloop_jlim.py와 같은 재구성 규칙(openloop108의 x0/게이트/리드투사 그대로, 리드는 로그 외생 입력,
자차 1차 지연 lag=0.3 s, action_t=0.25). 차이는 딱 하나: MPC에 넘기는 하한 a_min을 고정 ACCEL_MIN(-4.0)
대신, 그 사이클의 실시간(=미래 정보 없이 현재 gap/vE/vL/tf만 사용) "필요 감속" a_need로 매 사이클
다시 계산해 씌운다. 게이트/tau/tf 등 MPC 내부 가정은 전혀 건드리지 않는다(closedloop_jlim의 출력단
저크 제한과 달리, 여기는 입력단 a_min 자체를 캡한다 -> MPC가 다음 계획도 이 캡 안에서 다시 푼다).

a_need 계산(현재 시점 값만 사용, 미래 리드 궤적 지식 없음 = causal). **주의(이번 세션 중 정정)**: 처음에는
목표 거리를 MPC 비용의 d_comf(v,tf,cb,sd)(=v^2/(2*cb)+tf*v+sd)의 NCAP_FRAC배로 뒀으나, 실차 로그 대조 결과
d_comf가 고속에서 desiredDistance 실측치(약 60 m)의 3배 이상(약 200 m)으로 나와 이 프로젝트의 d_comf는 "목표
차간거리"로 쓸 수 있는 값이 아니었다(자세한 진단은 WIP.md 109차 참고, 원인 미확인 채 폐기). 대신 needed_decel.py가
이미 쓰는 시간차(headway) 기준으로 바꿨다:
  vRel = vE - vL (양수면 접근 중)
  d_target = NCAP_HFLOOR * vL   (리드가 현재 속도로 계속 갈 때 도달할 매칭 속도 기준 시간차 하한, 초 단위)
  avail = gap - d_target
  avail<=0.1  -> a_need = 4.0(이미 임계선 침범/임박, 상한 없이 최대로 둠)
  vRel<=0.1   -> a_need = 0.0(접근 중 아님)
  그 외        -> a_need = vRel^2 / (2*avail)  (리드가 "현재 속도를 유지"한다는 최악 가정의 등속-접근 정지거리 공식.
                 리드가 실제로 더 감속하면 다음 사이클 gap이 더 좁아지고 vRel이 커져 a_need가 스스로 올라간다 =
                 사후(hindsight) 값이 아니라 매 사이클 재계산되는 실시간 값. needed_decel.py의 h플로어와 같은
                 개념이지만 거기는 미래 리드 궤적을 알고 푸는 사후값이고, 여기는 현재 값만 쓰는 실시간 근사값이다)
  a_min_eff = clip(-(a_need + NCAP_MARGIN), ACCEL_MIN, 0.0)   # ACCEL_MIN=-4.0 아래로는 절대 안 내려감
R.solve(..., a_min=a_min_eff)로 그 사이클의 a_min만 교체. NCAP_MARGIN(기본 0.6 m/s²)은 "현재 속도 유지"
가정의 불확실성(리드가 계속 감속할 가능성) 대비 여유. NCAP=0이면 캡 비활성(a_min_eff=ACCEL_MIN 고정,
closedloop_jlim의 J_MAX=999와 동일한 기준선).

usage(실제 이벤트 재생): python3 closedloop_ncap.py event <seg> <t_from> <t_to> <gate_variant> [tag]
  gate_variant: none | M105 | M0.8/1.0 | M0.9/1.1 (closedloop_jlim.VARS 그대로, need-cap과 독립적인 별개 축)
  환경변수 NCAP(0/1, 기본 1), NCAP_MARGIN(기본 0.6), NCAP_HFLOOR(기본 1.2, 초), RSHIFT
usage(연속 제동 스트레스): python3 closedloop_ncap.py stress <v0_kph> <gap0_m> <lead_decel> <gate_variant> [tag]
  예: python3 closedloop_ncap.py stress 94 60 -5 M105 s60   (자차/리드 94 km/h 정속 주행 중 리드가 -5 m/s²로
  정지할 때까지 계속 감속. 게이트/캡 조합별 minGap이 이 후보의 안전 여유를 결정한다.)
필요: event 모드는 out/ego2.pkl(ego_extract2.py) + ../schema + ../segs. stress 모드는 로그 불필요(합성 시나리오).
한계: mpc_replica(acados 실물 아님), 액추에이터 1차 지연 가정. 실차 검증 아님. a_need 공식은 "리드가 현재 속도를
유지"하는 최악 가정 하나뿐이며, 리드가 실제로 계속 감속하는 경우의 안전 여유는 반드시 stress 모드로 별도 확인.
"""
import sys, os, numpy as np, pandas as pd
sys.path.insert(0, '../toolkit')
import mpc_replica as R
from openloop108 import DT, ALPHA, CN_T, ACCEL_MIN, GATE_T_LO, GATE_T_HI, GATE_TAU_G, GATE_TAU_TARGET, STOP_EQ_CB, lead_traj

CB, SD = 2.4, 7.0
ACT_T, LAG = 0.25, 0.3
VARS = {'none': None, 'M105': (1.0, 1.2), 'M0.8/1.0': (0.8, 1.0), 'M0.9/1.1': (0.9, 1.1)}

NCAP_ON = os.environ.get('NCAP', '1') != '0'
NCAP_MARGIN = float(os.environ.get('NCAP_MARGIN', '0.6'))
NCAP_HFLOOR = float(os.environ.get('NCAP_HFLOOR', '1.2'))


def need_cap(gap, vE, vL, tf, cb=CB, sd=SD):
    """실시간(causal) 필요 감속 a_need(m/s^2, 양수) -> 이번 사이클 a_min_eff(음수). 미래 리드 궤적 지식 없음.
    목표 거리는 needed_decel.py와 같은 시간차(headway) 정의(NCAP_HFLOOR 초, 매칭 속도 vL 기준)를 쓴다."""
    if not NCAP_ON:
        return ACCEL_MIN, 0.0
    d_target = NCAP_HFLOOR * max(vL, 0.0)
    avail = gap - d_target
    vRel = vE - vL
    if avail <= 0.1:
        a_need = 4.0
    elif vRel <= 0.1:
        a_need = 0.0
    else:
        a_need = min(vRel ** 2 / (2 * avail), 4.0)
    a_min_eff = float(np.clip(-(a_need + NCAP_MARGIN), ACCEL_MIN, 0.0))
    return a_min_eff, a_need


def gate_raw(gap, v_ego, v_lead, tf, m_lo, m_hi):
    d_comf = v_ego ** 2 / (2 * CB) + tf * v_ego + SD
    m = (gap + max(v_lead, 0.0) ** 2 / (2 * STOP_EQ_CB)) / max(0.8 * d_comf, 1e-3)
    g = float(np.clip((m_hi - m) / (m_hi - m_lo), 0., 1.))
    if v_ego - v_lead > 0.1:
        ttc = gap / (v_ego - v_lead)
        g = max(g, float(np.clip((GATE_T_HI - ttc) / (GATE_T_HI - GATE_T_LO), 0., 1.)))
    return g, m


def simulate_event(seg, t_from, t_to, variant):
    D = pd.read_pickle('out/ego2.pkl')
    cs, lp, rs = D['cs'], D['lp'], D['rs']
    c = cs[cs.seg == seg].sort_values('t').reset_index(drop=True)
    l = lp[lp.seg == seg].sort_values('t').reset_index(drop=True)
    r = rs[rs.seg == seg].sort_values('t').reset_index(drop=True)
    m = pd.merge_asof(l, r, on='t', direction='nearest', tolerance=0.01, suffixes=('', '_r')).dropna(subset=['dRel']).reset_index(drop=True)
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
    vE = float(m.vE.iloc[i0]); aE = float(m.aE.iloc[i0]); a_pl = float(a_des[i0 - 1])
    gap = [float(m.dRel.iloc[i0]), float(m.dRel2.iloc[i0])]
    prev_a = np.interp(R.T + DT, R.T, np.interp(R.T, CN_T, accs[i0 - 1]))
    out = []; warm = None
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
        a_min_eff, a_need = need_cap(gap[0], v0, row.vLead, tf)
        a_min_used = min(a_min_eff, a_pl)  # X[2,0]==a_pl가 초기 등식제약이라 bound(a_min<=a<=a_max)가 이를 배제하면 IPOPT Infeasible
        if xs:
            xo = np.min(np.vstack(xs), axis=0)
            X, J = R.solve(v0, a_pl, xo, tf, prev_a, jerk_factor=1.0,
                           a_change=float(row.aChangeCost) if row.aChangeCost > 0 else 200., cb=CB, sd=SD, a_min=a_min_used, warm=warm)
            warm = (X, J); asol = X[2]
        else:
            asol = np.full(len(R.T), 0.0)
        a_cmd = float(np.interp(ACT_T, R.T, asol))
        a_des_new = float(np.interp(DT, CN_T, np.interp(CN_T, R.T, asol)))
        vf = max(vf, 0.0) + DT * (a_des_new + a_pl) / 2.0
        a_pl = a_des_new; prev_a = np.interp(R.T + DT, R.T, asol)
        out.append(dict(ts=row.ts, vE=vE, aE=aE, a_cmd=a_cmd, gap=gap[0], vL=row.vLead, g=gcur, a_min_eff=a_min_eff, a_need=a_need,
                        real_aE=row.aE, real_vE=row.vE, real_gap=row.dRel))
        aE += (a_cmd - aE) * DT / LAG
        for k, vl in enumerate((row.vLead, row.vLead2)):
            gap[k] += (vl - vE) * DT
        vE = max(0.0, vE + aE * DT)
    return pd.DataFrame(out)


def simulate_stress(v0_kph, gap0, lead_decel, variant, dt=DT, t_max=30.0):
    """합성 시나리오: 자차/리드 모두 v0_kph 정속 주행 중 t=0부터 리드가 lead_decel(m/s^2, 음수)로 정지까지 계속 감속.
    리드의 실제(ground-truth) 궤적은 상수 감속이며, MPC에 넘기는 aLeadK/aLeadTau도 매 사이클 리드의 '현재' 순간
    가속도(감속 중 lead_decel, 정지 후 0)를 그대로 쓴다(레이더가 순간값을 정확히 본다는 가정, tau=1.2는 로그 중앙값
    근방). tf=1.6, cb/sd=params_backup 보정값. 자차 1차 지연 lag=0.3 s, action_t=0.25(closedloop108/jlim과 동일).
    """
    v0 = v0_kph / 3.6
    tf = 1.6
    tau_lead = 1.2
    gp = VARS[variant]
    vE = v0; aE = 0.0; a_pl = 0.0
    gap = gap0
    vL = v0
    prev_a = np.zeros(len(R.T))
    warm = None
    g_state = 1.0
    n = int(t_max / dt)
    out = []
    for i in range(n):
        # 리드 ground-truth 갱신(이번 사이클 vL은 지난 사이클 상태 사용, 다음에 적용)
        aL_true = lead_decel if vL > 0.05 else 0.0
        v0f = max(vE, 0.0)  # 필터 생략(합성 시나리오는 정속 시작이라 v_desired_filter가 이미 수렴한 상태로 취급)
        if gp is None:
            g = 1.0
        else:
            g_raw, _ = gate_raw(gap, v0f, vL, tf, gp[0], gp[1])
            g = g_raw if g_raw > g_state else g_state + (g_raw - g_state) * dt / GATE_TAU_G
        g_state = g
        tau_e = g * tau_lead + (1 - g) * GATE_TAU_TARGET
        xt, vt = lead_traj(gap, vL, aL_true, tau_e, v0f)
        xo = xt + vt ** 2 / (2 * STOP_EQ_CB)
        a_min_eff, a_need = need_cap(gap, v0f, vL, tf)
        a_min_used = min(a_min_eff, a_pl)  # event 모드와 동일: X[2,0]==a_pl 등식제약이 bound(a_min<=a<=a_max)와 충돌해 IPOPT Infeasible을 피하기 위함(109차 계속 리뷰 지적, 이번 세션 수정)
        X, J = R.solve(v0f, a_pl, xo, tf, prev_a, jerk_factor=1.0, a_change=200., cb=CB, sd=SD, a_min=a_min_used, warm=warm)
        warm = (X, J); asol = X[2]
        a_cmd = float(np.interp(ACT_T, R.T, asol))
        a_pl = float(np.interp(dt, R.T, asol))
        prev_a = np.interp(R.T + dt, R.T, asol)
        ttc = gap / (vE - vL) if vE - vL > 0.1 else 99.0
        out.append(dict(t=i * dt, vE=vE, vL=vL, gap=gap, aE=aE, a_cmd=a_cmd, g=g_state, a_min_eff=a_min_eff, a_need=a_need, ttc=ttc))
        aE += (a_cmd - aE) * dt / LAG
        gap += (vL - vE) * dt
        vE = max(0.0, vE + aE * dt)
        vL = max(0.0, vL + aL_true * dt)
    return pd.DataFrame(out)


def summarize_event(d):
    hw = d.gap / np.maximum(d.vE, 1.0); ttc = np.where(d.vE - d.vL > 0.1, d.gap / np.maximum(d.vE - d.vL, 1e-3), 99.)
    return dict(aEmin=d.aE.min(), aCmdMin=d.a_cmd.min(), minGap=d.gap.min(), minHw=hw.min(), minTTC=float(np.min(ttc)),
                gMax=d.g.max(), aNeedMax=d.a_need.max(), aMinEffMin=d.a_min_eff.min(),
                vEend_kph=d.vE.iloc[-1] * 3.6, real_aEmin=d.real_aE.min())


def summarize_stress(d):
    return dict(aEmin=d.aE.min(), aCmdMin=d.a_cmd.min(), minGap=d.gap.min(), minTTC=d.ttc.min(),
                gMax=d.g.max(), aNeedMax=d.a_need.max(), aMinEffMin=d.a_min_eff.min())


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'event':
        seg = int(sys.argv[2]); t0 = float(sys.argv[3]); t1 = float(sys.argv[4]); var = sys.argv[5]
        tag = sys.argv[6] if len(sys.argv) > 6 else f'{seg}'
        d = simulate_event(seg, t0, t1, var)
        d.to_pickle(f'out/ncap_ev_{tag}_{var.replace("/", "-")}.pkl')
        s = summarize_event(d)
        print(f'{var:9s} ' + ' '.join(f'{k}={v:.2f}' for k, v in s.items()), flush=True)
    elif mode == 'stress':
        v0k = float(sys.argv[2]); gap0 = float(sys.argv[3]); ldec = float(sys.argv[4]); var = sys.argv[5]
        tag = sys.argv[6] if len(sys.argv) > 6 else 's'
        d = simulate_stress(v0k, gap0, ldec, var)
        d.to_pickle(f'out/ncap_st_{tag}_{var.replace("/", "-")}.pkl')
        s = summarize_stress(d)
        print(f'{var:9s} ' + ' '.join(f'{k}={v:.2f}' for k, v in s.items()), flush=True)
    else:
        print('usage: closedloop_ncap.py event|stress ...', file=sys.stderr); sys.exit(1)
