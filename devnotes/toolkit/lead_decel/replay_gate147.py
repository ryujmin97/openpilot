#!/usr/bin/env python3
"""147cha 감속 프리뷰 게이트(PREVIEW_GATE_M_LO/HI=1.05/1.25 + TTC 6/12) 실로그 재생 검증 (149차).

실행 코드를 그대로 재사용한다(재구현 없음):
  - longitudinal_preview.py (SHA 고정, 순수 파이썬): get_lead_preview_request/rate_limit_preview/clip_preview_offset/apply_preview_target
  - long_mpc.py: ast로 상수 + get_safe_obstacle_distance + get_stopped_equivalence_factor + LongitudinalMpc._gate_raw만 추출해 exec
사용: python3 replay_gate147.py <run_dir> <src_old_dir> <src_new_dir> [cb] [sd]
  run_dir: out/ego2.pkl(ego_extract2.py) + out/radarflag.pkl(extract_radar_flag.py) 있는 곳
  src_old/new: 8e8b0d1a(로그 기록 커밋)/c0a01658(147차) 의 longitudinal_preview.py, long_mpc.py 사본
출력: <run_dir>/out/replay147.pkl (20Hz 표본 단위 DataFrame)
한계: MPC 궤적(accels)은 로그값 고정 -> 프리뷰는 플래너에서 궤적 '읽는 시점(action_t)'만 바꾸므로 a_target 재구성은 정확하지만
      자차 거동이 바뀐 뒤의 폐루프(간격/리드 상대속도 변화)는 재현하지 않는다(open-loop). 실차 검증 아님.
"""
import sys, ast, importlib.util, numpy as np, pandas as pd

run, src_old, src_new = sys.argv[1:4]
CB = float(sys.argv[4]) if len(sys.argv) > 4 else 2.4
SD = float(sys.argv[5]) if len(sys.argv) > 5 else 7.0
import os
PB_LO, PB_HI = (float(x) for x in os.environ.get('PBAND', '1.05,1.25').split(','))   # 밴드 스윕용(기본=147차 값)
TAG = os.environ.get('TAG', '')

def load_mod(path, name):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m; spec.loader.exec_module(m); return m

def load_gate(path):
    """long_mpc.py에서 게이트 관련 원문만 추출해 exec (import 의존성 회피)."""
    tree = ast.parse(open(path, encoding='utf-8').read())
    want_assign = {'LEAD_DANGER_FACTOR','COMFORT_BRAKE','STOP_DISTANCE','GATE_M_LO','GATE_T_LO','PREVIEW_GATE_M_LO'}
    keep = []
    for n in tree.body:
        if isinstance(n, ast.Assign):
            names = set()
            for t in n.targets:
                if isinstance(t, ast.Name): names.add(t.id)
                elif isinstance(t, ast.Tuple): names |= {e.id for e in t.elts if isinstance(e, ast.Name)}
            if names & want_assign: keep.append(n)
        elif isinstance(n, ast.FunctionDef) and n.name in ('get_stopped_equivalence_factor', 'get_safe_obstacle_distance'):
            keep.append(n)
        elif isinstance(n, ast.ClassDef) and n.name == 'LongitudinalMpc':
            for b in n.body:
                if isinstance(b, ast.FunctionDef) and b.name == '_gate_raw':
                    b.decorator_list = []; keep.append(b)
    ns = {'np': np}
    exec(compile(ast.Module(body=keep, type_ignores=[]), path, 'exec'), ns)
    return ns

old_prev = load_mod(f'{src_old}/longitudinal_preview.py', 'prev_old')
new_prev = load_mod(f'{src_new}/longitudinal_preview.py', 'prev_new')
new_gate = load_gate(f'{src_new}/long_mpc.py')
old_gate = load_gate(f'{src_old}/long_mpc.py')
MODE = next(iter(new_prev.MODE_TUNING))

D = pd.read_pickle(f'{run}/out/ego2.pkl'); cs, lp, rs = D['cs'], D['lp'].reset_index(drop=True), D['rs']
rf = pd.read_pickle(f'{run}/out/radarflag.pkl')
def latest(df, t): return np.searchsorted(df.t_abs.values, t, side='right') - 1
ics = latest(cs, lp.t_abs.values); irs = latest(rs, lp.t_abs.values); irf = latest(rf, lp.t_abs.values)
ok = (ics >= 0) & (irs >= 0) & (irf >= 0)
T_IDX = np.array([10.0 * (i / 32) ** 2 for i in range(17)])

def a_target_from_accels(accels, action_t):
    """get_accel_from_plan(drive_helpers, 8e8b0d1a) 동일식: a=2*(v(T)-v0)/T-a0, v는 로그 accels 적분으로 재구성(속도궤적 미로깅)."""
    a = np.asarray(accels, float)
    if len(a) != 17: return np.nan
    v = np.concatenate([[0.0], np.cumsum(0.5 * (a[1:] + a[:-1]) * np.diff(T_IDX))])
    return 2 * (np.interp(action_t, T_IDX, v) - 0.0) / action_t - a[0]

rows = []
cur_old = cur_g1 = cur_new = cur_oldm = 0.0   # 각 체인의 self.lead_preview
for k in range(len(lp)):
    if not ok[k]: continue
    p = lp.iloc[k]; c = cs.iloc[ics[k]]; r = rs.iloc[irs[k]]; flag = bool(rf.radar.iloc[irf[k]])
    action_t = float(p.leadPreviewActionTime - p.leadPreviewSeconds)   # base action_t (로그 역산)
    enabled = (p.source != 'e2e') and (not c.gas) and (not c.brake)    # planner: mpc.mode=='acc' and not gas/brake (reset_state는 미로깅)
    gated = bool(enabled and r.status and flag and r.radarTrackId >= 0)
    tf = float(p.tFollow)
    g_new, m_new = new_gate['_gate_raw'](r.dRel, c.vEgo, r.vLead, tf, CB, SD, m_lo=PB_LO, m_hi=PB_HI)
    g_old, m_old = old_gate['_gate_raw'](r.dRel, c.vEgo, r.vLead, tf, CB, SD)   # 기존 GATE_M 0.8/1.0 (raw, 시정수 필터 전)
    g_new_f = g_new if gated else 1.0
    # --- 체인: A=로그 기록 커밋 코드(old, 게이트 없음), B=새 코드 gate=1(동치 검증), C=새 코드 gate=g_new, D=참고: 새 코드 + 기존 GATE_M raw g_old
    def chain(prev_mod, cur, **kw):
        req = prev_mod.get_lead_preview_request(MODE, lead_status=gated, a_lead=r.aLeadK, a_ego=c.aEgo, **kw)
        if enabled:
            rl = prev_mod.rate_limit_preview(req.offset_s, cur)
            cur = prev_mod.clip_preview_offset(action_t, rl)
        else:
            cur = 0.0
        return req, cur
    reqA, cur_old = chain(old_prev, cur_old)
    reqB, cur_g1 = chain(new_prev, cur_g1, gate=1.0)
    reqC, cur_new = chain(new_prev, cur_new, gate=g_new_f)
    reqD, cur_oldm = chain(new_prev, cur_oldm, gate=(g_old if gated else 1.0))
    def out_a(cur):
        base = a_target_from_accels(p.accels, action_t)
        prev_t = a_target_from_accels(p.accels, action_t + cur) if enabled else base
        return base, float(new_prev.apply_preview_target(base, prev_t, MODE)) if enabled else base
    base_a, aA = out_a(cur_old); _, aC = out_a(cur_new); _, aD = out_a(cur_oldm)
    rows.append(dict(t=p.t, seg=p.seg, source=p.source, enabled=enabled, gated=gated, dRel=r.dRel, vRel=r.vRel, vLead=r.vLead, vEgo=c.vEgo, aEgo=c.aEgo, aLeadK=r.aLeadK,
                     tf=tf, m_new=m_new, m_old=m_old, g_new=g_new_f, g_oldraw=(g_old if gated else 1.0),
                     sig_base=reqB.lead_accel_signal, off_req_base=reqA.offset_s, off_req_B=reqB.offset_s, off_req_new=reqC.offset_s,
                     prev_log=p.leadPreviewSeconds, prev_A=cur_old, prev_B=cur_g1, prev_new=cur_new, prev_oldgate=cur_oldm,
                     aBase_est=base_a, aBase_log=p.aTargetBase, aTarget_log=p.aTarget, aOut_A=aA, aOut_new=aC, aOut_oldgate=aD,
                     action_t=action_t))
R = pd.DataFrame(rows); R.to_pickle(f'{run}/out/replay147{TAG}.pkl')
print('rows', len(R), 'gated', int(R.gated.sum()), f'CB={CB} SD={SD} MODE={MODE}')
print('[동치] 새 코드 gate=1 vs 기록커밋 코드: 최대 |prev_A-prev_B| =', float(np.abs(R.prev_A - R.prev_B).max()))
print('[재현] 기록 leadPreviewSeconds vs 재생(A): mean|err|=%.4f  95%%=%.4f  max=%.4f  (log 활성 %.1f%% / 재생 %.1f%%)' % (
    np.abs(R.prev_A - R.prev_log).mean(), np.abs(R.prev_A - R.prev_log).quantile(.95), np.abs(R.prev_A - R.prev_log).max(), 100*(R.prev_log>0).mean(), 100*(R.prev_A>0).mean()))
e = (R.aBase_est - R.aBase_log).abs(); print('[a_target 재구성] aTargetBase 재구성 vs 로그: mean|err|=%.3f 95%%=%.3f max=%.3f' % (e.mean(), e.quantile(.95), e.max()))
e2 = (R.aOut_A - R.aTarget_log).abs(); e2 = e2[R.source.isin(['lead0','lead1','cruise'])]; print('[a_target 재구성] 프리뷰 적용 후 vs 로그 aTarget(acc 모드): mean|err|=%.3f 95%%=%.3f' % (e2.mean(), e2.quantile(.95)))
