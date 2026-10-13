#!/usr/bin/env python3
"""ol_replay.py (276cha, 275cha/276cha 로그 0000049d 분석의 ol15.py를 복원) 앞차 게이트 열린 루프 재생.
extract_log.py가 만든 pkl(환경변수 LR_PKL, 기본 ./log_lead.pkl)의 leadOne/leadTwo와 자차 속도(vEgo, aEgo)를 실제
acados `LongitudinalMpc`(HEAD)에 프레임마다 넣고, 게이트(`_gate_raw`)를 그대로 둔 출력(hd)과 g=1 강제 출력(goff)을 로그 aTarget과 비교한다.
자차 응답은 로그값이라 폐루프가 아니다. 설정속도 기본 70 km/h(`vset`), TF는 로그 tFollow.
사전 준비: toolkit `pytest_ci_setup.sh` -> `cl_sim/prep_base.sh HEAD~N`(cl_sim이 기준선 모듈을 임포트한다. 쓴 뒤 long_mpc_base110.py 삭제)
-> export PYTHONPATH=/home/claude/repo:/home/claude/repo/opendbc_repo. 실행: python3 ol_replay.py [t0 t1] (기본 110 125). 결과 ol_replay.pkl.
스태틱메서드 교체 주의: `M.LongitudinalMpc._gate_raw`는 `__dict__['_gate_raw'].__func__`로 꺼내야 한다(클래스 속성으로 읽으면 바운드 해제 문제로 TypeError).
실차 검증 아님."""
import sys, os, pickle
import numpy as np, pandas as pd
from types import SimpleNamespace as NS
sys.path.insert(0, os.environ.get('CL_SIM_DIR', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'cl_sim')))
from openpilot.selfdrive.controls.lib.longitudinal_mpc_lib import long_mpc as M
import cl_sim
D = pickle.load(open(os.environ.get('LR_PKL', 'log_lead.pkl'), 'rb'))
rs, cs, lp = D['rs'], D['cs'], D['lp']


def frames(t0, t1):
    m = rs[(rs.t >= t0) & (rs.t <= t1)].reset_index(drop=True)
    for name, df, cols in (('c', cs, ['vEgo', 'aEgo']), ('p', lp, ['aTarget', 'desired', 'tFollow'])):
        x = pd.merge_asof(m[['t']], df.sort_values('t'), on='t')
        for c in cols:
            m[c] = x[c].values
    return m


def lead(r, k):
    if not r[k + '_status']:
        return NS(status=False, radar=False, radarTrackId=-1, dRel=0., vRel=0., vLead=0., aLeadK=0., aLeadTau=0., modelProb=0., cutOutTime=0., cutOutConfidence=0.)
    return NS(status=True, radar=bool(r[k + '_radar']), radarTrackId=int(r[k + '_tid']), dRel=r[k + '_dRel'], vRel=r[k + '_vRel'], vLead=r[k + '_vLead'],
              aLeadK=r[k + '_aLeadK'], aLeadTau=r[k + '_aLeadTau'], modelProb=r[k + '_prob'], cutOutTime=0., cutOutConfidence=0.)


def run(m, gate_off=False, vset=70 / 3.6, leadfn=None, aovr=None):
    orig = M.LongitudinalMpc.__dict__['_gate_raw']
    if gate_off:
        raw = orig.__func__
        M.LongitudinalMpc._gate_raw = staticmethod(lambda *a, **k: (1.0, raw(*a, **k)[1]))
    try:
        mpc = M.LongitudinalMpc(dt=0.05); mpc.mode = 'acc'; mpc.reset(); mpc.prev_a = np.zeros(M.N + 1)
        z = lambda: np.zeros(M.N + 1); out = []; lt = [0, 0]; reset = True; a_prev = 0.0
        for i, r in m.iterrows():
            l1 = (leadfn or lead)(r, 'l1'); l2 = lead(r, 'l2')
            carrot = cl_sim.mk_carrot(tf=float(r.tFollow) if r.tFollow > 0 else 1.6, vcruise=vset)
            rsx = NS(leadOne=l1, leadTwo=l2)
            lt = [lt[0] + 1 if (l1.status and l1.radar) else 0, 0]
            mpc.set_accel_limits(-3.5, 1.5); mpc.set_cur_state(float(r.vEgo), float(r.aEgo) if aovr is None else a_prev)
            mpc.update(carrot, reset, rsx, vset, z(), z(), z(), z(), prev_accel_constraint=True, jerk_factor=1., a_change_cost_starting=10.,
                       lead_accel_response_enabled=False, lead_gap_enabled=True, lead_track_frames=tuple(lt), measured_a_ego=float(r.aEgo), cutout_relief_enabled=True)
            reset = False
            a = float(np.interp(0.05, np.array(M.T_IDXS), mpc.a_solution)); a_prev = a
            out.append(a)
        return np.array(out)
    finally:
        M.LongitudinalMpc._gate_raw = orig


def gate_trace(m):
    """HEAD 재생 중 leadOne 게이트 상태 g(`_gate_g[0]`)를 프레임별로 기록해 반환."""
    gs = []
    orig = M.LongitudinalMpc.process_lead

    def pl(self, lead_, idx):
        r = orig(self, lead_, idx)
        if idx == 0:
            gs.append(self._gate_g[0])
        return r
    M.LongitudinalMpc.process_lead = pl
    try:
        run(m)
    finally:
        M.LongitudinalMpc.process_lead = orig
    return np.array(gs)


if __name__ == '__main__':
    t0, t1 = (float(sys.argv[1]), float(sys.argv[2])) if len(sys.argv) >= 3 else (110., 125.)
    m = frames(t0, t1)
    H = run(m); G = run(m, gate_off=True)
    m['hd'] = H; m['goff'] = G
    pd.set_option('display.width', 200)
    sel = m.iloc[::5]
    print(sel[['t', 'vEgo', 'l1_radar', 'aTarget', 'hd', 'goff']].round(2).to_string(index=False))
    print('max|head-gateoff|: %.3f at t=%.1f' % (float(np.abs(m.hd - m.goff).max()), float(m.t[np.abs(m.hd - m.goff).idxmax()])))
    print('min a: log %.2f head %.2f gateoff %.2f' % (m.aTarget.min(), H.min(), G.min()))
    g = gate_trace(m); print('gate g<0.99 frames:', int((g < 0.99).sum()), 'of', len(g))
    m.to_pickle('ol_replay.pkl')
