#!/usr/bin/env python3
"""cl_replay.py (276cha, cl15.py 복원) 로그 앞차 궤적 투입 폐루프: 실제 acados LongitudinalMpc(HEAD) + 자차 1차 플랜트(로그 보정). 실차 검증 아님.
`lead_true(ts)`: 앞차 참값 궤적 추정. 119.0초 레이더(속도, 위치)에 고정하고 [T0,ts) 등속 16.4 m/s, [ts,119) 일정 감속, 119초 이후는 레이더 속도(0.3초 이동평균) 적분.
`run(ts, inputs, gate_off, vset)`: inputs='vision'이면 119.0초 전까지 로그의 비전 leadOne(dRel/vLead/aLeadK/aLeadTau, radar=False)을 그대로 넣고(거리는 참값 간격 + 로그 거리 오차),
  inputs='ideal'이면 참값 궤적을 레이더 앞차(radar=True)로 넣는다. gate_off=True는 `_gate_raw`를 g=1로 고정. 119.0초 이후는 둘 다 참값(레이더 인계).
고정 가정과 값(275cha/276cha 로그 0000049d 기준이라 다른 로그에는 맞게 바꿔야 한다): T0~T1=112~126초, 앞차 감속 전 속도 16.4 m/s, 인계 시각 119.0초,
  자차 플랜트 TAU=0.4/DELAY=0.0(plant_fit.py), 설정속도 vset=17.9 m/s(로그에서 읽을 수 없어 자차 속도로 가정, cruise_speed.py), TF는 로그 tFollow, stop_distance 7.0(로그 StopDistanceCarrot=700), comfort_brake 2.5.
주의(둘 다 276cha에 실제로 겪은 오류): (1) 로그 값 조회는 영차 유지(ZOH)여야 한다. 선형 보간은 앞차 끊김(status False, dRel 0) 구간에서 거리를 0 쪽으로 끌어 시뮬레이션이 실제보다 일찍 제동하는 가짜 결과를 만들었다.
  (2) 설정속도를 70 km/h로 두면 로그보다 약 0.5초 일찍 반응해 로그와 맞지 않았다.
사전 준비/환경변수는 ol_replay.py와 같다(PYTHONPATH, prep_base.sh, LR_PKL). 실행: python3 cl_replay.py (8런, 약 2~4분). 결과 cl_replay.pkl.
한계: 앞차 궤적은 추정, 레이더/비전 지연과 노이즈 없음, 앞차 1대, 플래너 리셋 램프/끼어들기 사전감속 없음."""
import sys, os, math, pickle
import numpy as np, pandas as pd
from types import SimpleNamespace as NS
sys.path.insert(0, os.environ.get('CL_SIM_DIR', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'cl_sim')))
from openpilot.selfdrive.controls.lib.longitudinal_mpc_lib import long_mpc as M
import cl_sim
D = pickle.load(open(os.environ.get('LR_PKL', 'log_lead.pkl'), 'rb')); rs, cs, lp = D['rs'], D['cs'], D['lp']
TAU, DELAY = 0.4, 0.0; DT = 0.05; T0, T1 = 112.0, 126.0
tc = cs.t.values; xe_c = np.concatenate([[0], np.cumsum(np.diff(tc) * cs.vEgo.values[1:])]); xego_log = lambda q: np.interp(q, tc, xe_c)
_ix = lambda q: int(np.clip(np.searchsorted(rs.t.values, q, side='right') - 1, 0, len(rs) - 1))
R = lambda c, q: rs[c].values[_ix(q)]  # 영차 유지(ZOH): 앞차 끊김 구간을 보간하면 거리가 0으로 끌려가는 오류가 생긴다


def lead_true(ts):
    """119.0초 레이더에 고정: [T0,ts) 등속 16.4, [ts,119) 일정 감속(119.0에 레이더 속도), 이후 레이더 속도(0.3초 이동평균) 적분"""
    tg = np.arange(T0 - 1, T1 + 1, 0.01); v = np.empty_like(tg); v0, v119 = 16.4, float(R('l1_vLead', 119.0)); a = (v119 - v0) / (119.0 - ts)
    vr = pd.Series(np.interp(tg, rs.t.values, np.where(rs.l1_radar.values, rs.l1_vLead.values, np.nan))).rolling(30, center=True, min_periods=1).mean().values
    for i, q in enumerate(tg):
        v[i] = v0 if q < ts else (v0 + a * (q - ts) if q < 119.0 else vr[i])
    v = np.clip(v, 0, None); x = np.concatenate([[0], np.cumsum(np.diff(tg) * v[1:])])
    k = np.abs(tg - 119.0).argmin(); x += xego_log(119.0) + float(R('l1_dRel', 119.0)) - x[k]
    return tg, x, v, a


def run(ts, inputs='vision', gate_off=False, vset=17.9):
    tg, xl, vl, aL = lead_true(ts); X = lambda q: np.interp(q, tg, xl); V = lambda q: np.interp(q, tg, vl)
    err = lambda q: float(R('l1_dRel', q)) - (X(q) - xego_log(q))
    orig = M.LongitudinalMpc.__dict__['_gate_raw']
    if gate_off:
        raw = orig.__func__; M.LongitudinalMpc._gate_raw = staticmethod(lambda *a, **k: (1.0, raw(*a, **k)[1]))
    try:
        mpc = M.LongitudinalMpc(dt=DT); mpc.mode = 'acc'; mpc.reset(); mpc.prev_a = np.zeros(M.N + 1)
        v = float(np.interp(T0, tc, cs.vEgo)); xe = float(xego_log(T0)); a_act = float(np.interp(T0, cs.t, cs.aEgo)); a_des = 0.0
        q = [a_des] * int(round(DELAY / DT)); z = lambda: np.zeros(M.N + 1); out = []; reset = True; lt = 0
        TF = lambda qq: float(lp.tFollow.values[int(np.clip(np.searchsorted(lp.t.values, qq, side='right') - 1, 0, len(lp) - 1))]) or 1.6
        for k in range(int((T1 - T0) / DT)):
            t = T0 + k * DT; vis = (t < 119.0) and inputs == 'vision'
            gap = float(X(t) - xe); st = bool(R('l1_status', t)) if (t < 119.0 and inputs == 'vision') else True
            if t < ts and inputs == 'ideal':
                st = bool(R('l1_status', t))
            if vis:
                d_in = gap + err(t); v_in = float(R('l1_vLead', t)); a_in = float(R('l1_aLeadK', t)); tau_in = float(R('l1_aLeadTau', t)); radar = False; tid = -1
            else:
                d_in = gap; v_in = float(V(t)); radar = True; tid = 0
                if inputs == 'ideal' and t < 119.0:
                    a_in = aL if t >= ts else 0.0; tau_in = 0.3
                else:
                    a_in = float(R('l1_aLeadK', t)); tau_in = float(R('l1_aLeadTau', t))
            l1 = NS(status=st, radar=radar, radarTrackId=tid, dRel=d_in, vRel=v_in - v, vLead=v_in, aLeadK=a_in, aLeadTau=tau_in, modelProb=.95, cutOutTime=0., cutOutConfidence=0.) if st else cl_sim.lead_ns(False, 0, 0, v, 0, -1)
            lt = lt + 1 if (st and radar) else 0
            rsx = NS(leadOne=l1, leadTwo=cl_sim.lead_ns(False, 0, 0, v, 0, -1)); carrot = cl_sim.mk_carrot(tf=TF(t), sd=7.0, vcruise=vset)
            mpc.set_accel_limits(-3.5, 1.5); mpc.set_cur_state(v, a_des)
            mpc.update(carrot, reset, rsx, vset, z(), z(), z(), z(), prev_accel_constraint=True, jerk_factor=1., a_change_cost_starting=10.,
                       lead_accel_response_enabled=False, lead_gap_enabled=True, lead_track_frames=(lt, 0), measured_a_ego=a_act, cutout_relief_enabled=True)
            reset = False; a_des = float(np.interp(DT, np.array(M.T_IDXS), mpc.a_solution)); q.append(a_des); cmd = q.pop(0)
            a_act += (cmd - a_act) * (1 - math.exp(-DT / TAU)); v = max(0., v + a_act * DT); xe += v * DT
            out.append((t, v, a_act, a_des, gap, float(V(t)), int(mpc.solution_status != 0)))
        return pd.DataFrame(out, columns='t v a a_des gap vl bad'.split())
    finally:
        M.LongitudinalMpc._gate_raw = orig


def summ(df, name):
    f = lambda th: (lambda s: float(s.t.iloc[0]) if len(s) else float('nan'))(df[(df.t >= 116) & (df.a <= th)])
    at = lambda q, c: float(df[c].iloc[(df.t - q).abs().argmin()])
    w = df[df.t >= 117]
    return dict(name=name, t_a05=f(-0.5), t_a10=f(-1.0), t_a20=f(-2.0), a118=at(118, 'a'), a1185=at(118.5, 'a'), a119=at(119, 'a'), a120=at(120, 'a'), amin=float(df.a.min()),
                gap_min=float(w.gap.min()), v_at_gapmin=float(w.v.iloc[w.gap.argmin()]), v121=at(121, 'v'), v_end=float(df.v.iloc[-1]), bad=int(df.bad.sum()) if 'bad' in df else 0)


def log_row():
    """로그 실제 거동 행(aEgo 0.5초 이동평균, 실제 앞차 거리)"""
    ae = pd.DataFrame(dict(t=cs.t, a=pd.Series(cs.aEgo).rolling(10, center=True, min_periods=1).mean(), v=cs.vEgo)); ae = ae[(ae.t >= T0) & (ae.t <= T1)]
    g = pd.DataFrame(dict(t=np.arange(T0, T1, DT))); g['a'] = np.interp(g.t, ae.t, ae.a); g['v'] = np.interp(g.t, ae.t, ae.v)
    g['gap'] = np.interp(g.t, rs.t, np.where(rs.l1_status, rs.l1_dRel, np.nan))
    return summ(g, 'LOG(actual)')


if __name__ == '__main__':
    rows = [log_row()]; res = {}
    for ts in (116.1, 116.8):
        for inp in ('vision', 'ideal'):
            for go in (False, True):
                nm = 'ts%.1f_%s_%s' % (ts, inp, 'gateoff' if go else 'gate'); d = run(ts, inp, go); res[nm] = d; rows.append(summ(d, nm)); print(nm, flush=True)
    pickle.dump(res, open('cl_replay.pkl', 'wb'))
    pd.set_option('display.width', 250); print(pd.DataFrame(rows).round(2).to_string(index=False))
