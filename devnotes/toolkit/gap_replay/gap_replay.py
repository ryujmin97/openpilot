#!/usr/bin/env python3
"""longitudinal_gap_recovery.py 실차 로그 재생 (252cha).
extract <schema_dir> <segs_dir> <out.pkl> : <segs_dir>/*--<n>/rlog.zst -> longitudinalPlan 20Hz 프레임별 최신 상태 병합 + initData 파라미터
replay <plan.pkl> <new_gap.py> [<old_gap.py>] [--cb 2.5] : LeadGapState open-loop 재생, 로그 desiredDistance와 비교
가정/한계: v_ego=carState.vEgo, comfort_brake=--cb, lane_change_active=modelV2 laneChangeState!=off 근사, reset_state/force_slow_decel 로그 없음(experimentalMode False/longActive/gasPressed로 근사),
desiredDistance relief 무시, open-loop. 의존: pycapnp zstandard numpy pandas. 실차 검증 아님."""
import sys, os, glob, pickle, importlib.util, inspect
import numpy as np, pandas as pd
raw = lambda x: int(x.raw) if hasattr(x, 'raw') else int(x)

def extract(schema, segs, out):
    import capnp, zstandard
    capnp.remove_import_hook()
    log = capnp.load(schema + '/log.capnp', imports=[schema, schema + '/include'])
    paths = sorted(glob.glob(os.path.join(segs, '*', 'rlog.zst')), key=lambda p: int(os.path.basename(os.path.dirname(p)).split('--')[-1]))
    rows, params, t0 = [], {}, None
    st = dict(vEgo=np.nan, gas=False, lc=0, pers=-1, exp=False, longActive=False); lead = {}
    L = lambda l: dict(status=bool(l.status), radar=bool(l.radar), tid=int(l.radarTrackId), dRel=float(l.dRel), vRel=float(l.vRel), vLead=float(l.vLead))
    for sp in paths:
        data = zstandard.ZstdDecompressor().stream_reader(open(sp, 'rb')).read()
        for ev in log.Event.read_multiple_bytes(data):
            w = ev.which()
            if w == 'initData':
                if not params:
                    for e in ev.initData.params.entries:
                        try: params[e.key] = e.value.decode()
                        except Exception: params[e.key] = repr(e.value)
                    params['_gitCommit'] = ev.initData.gitCommit; params['_dirty'] = ev.initData.dirty
                continue
            if t0 is None and w == 'carState': t0 = ev.logMonoTime
            if t0 is None: continue
            t = (ev.logMonoTime - t0) * 1e-9
            if w == 'carState': st.update(vEgo=float(ev.carState.vEgo), gas=bool(ev.carState.gasPressed), brake=bool(ev.carState.brakePressed))
            elif w == 'selfdriveState': st.update(pers=raw(ev.selfdriveState.personality), exp=bool(ev.selfdriveState.experimentalMode))
            elif w == 'carControl': st.update(longActive=bool(ev.carControl.longActive))
            elif w == 'modelV2': st.update(lc=raw(ev.modelV2.meta.laneChangeState))
            elif w == 'radarState': lead = L(ev.radarState.leadOne)
            elif w == 'longitudinalPlan':
                p = ev.longitudinalPlan
                rows.append(dict(t=t, **st, **{'r_' + k: v for k, v in lead.items()}, tFollow=float(p.tFollow), desired=float(p.desiredDistance),
                                 aTarget=float(p.aTarget), myMode=int(p.myDrivingMode)))
    pickle.dump(dict(df=pd.DataFrame(rows), params=params), open(out, 'wb'))
    print(len(rows), 'plan frames, commit', params.get('_gitCommit'), 'dirty', params.get('_dirty'))

def load_mod(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m

def level_for(params, pers, mode):
    common = int(params.get('LeadAccelResponse', 0))
    v = int(params.get('LeadAccelResponseTF%d' % (pers + 1), -1)) if 0 <= pers <= 3 else -1
    lvl = int(min(5, max(0, common if v < 0 else v)))
    return max(0, min(lvl, {1: 2, 2: 3}.get(mode, 5)))

def run(df, params, mod, cb, sd):
    st = mod.LeadGapState(); takes_sd = 'stop_distance' in inspect.signature(st.update).parameters
    frames, last, out = 0, -1, []
    for r in df.itertuples():
        tid = int(r.r_tid) if (r.r_status and r.r_radar and r.r_tid >= 0) else -1
        if tid >= 0 and tid == last: frames += 1
        elif tid >= 0: last, frames = tid, 1
        else: last, frames = -1, 0
        elig = bool((not r.exp) and r.longActive and not r.gas and r.lc == 0 and frames >= 3 and r.r_status and r.r_radar)
        v, tf, vl = r.vEgo, r.tFollow, r.r_vLead
        base = v * v / (2 * cb) + tf * v + sd - vl * vl / (2 * cb)
        kw = dict(level=level_for(params, r.pers, r.myMode), track_id=r.r_tid if elig else -1, enabled=elig, dt=0.05, ego_speed=v,
                  lead_speed=vl if elig else 0.0, relative_speed=r.r_vRel if elig else 0.0, distance=r.r_dRel if elig else 0.0,
                  desired_distance=base, base_tf=tf)
        if takes_sd: kw['stop_distance'] = sd
        st.update(**kw)
        out.append((v * st.extra_tf * mod.entry_weight(st.strength), base, v * tf + sd, frames, elig))
    return pd.DataFrame(out, columns=['margin', 'base', 'ref', 'frames', 'elig'], index=df.index)

def replay(plan, new_py, old_py=None, cb=2.5):
    d = pickle.load(open(plan, 'rb')); df, params = d['df'], d['params']
    sd = float(params.get('StopDistanceCarrot', 700)) / 100.0
    x = df.join(run(df, params, load_mod(new_py, 'gnew'), cb, sd).add_prefix('n_'))
    if old_py: x = x.join(run(df, params, load_mod(old_py, 'gold'), cb, sd).add_prefix('o_'))
    print('commit', params.get('_gitCommit'), 'stop_distance', sd, 'cb', cb, 'plan frames', len(x), 'eligible', int(x.n_elig.sum()))
    Lf = x[x.r_status & (x.desired > 0) & (x.vEgo > 1)]
    for tag, p in (('NEW', 'n_'), ('OLD', 'o_')):
        if p + 'margin' not in Lf: continue
        pr = Lf[p + 'base'] + Lf[p + 'margin']; e = pr - Lf.desired
        print('%s fidelity n=%d mean %.3f MAE %.3f corr %.4f |e|<0.5 %.1f%%' % (tag, len(Lf), e.mean(), e.abs().mean(), np.corrcoef(pr, Lf.desired)[0, 1], 100 * (e.abs() < 0.5).mean()))
    E = x[x.r_status & (x.desired > 0) & (x.vEgo > 2) & x.n_elig].copy()
    E['ratio'] = E.r_dRel / E.n_ref; E['log_m'] = E.desired - E.n_base
    E['bin'] = pd.cut(E.ratio, [0, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.7, 2.0, 99]); g = E.groupby('bin', observed=True)
    tab = pd.DataFrame({'n': g.size(), 'log_m': g.log_m.mean(), 'NEW_m': g.n_margin.mean(), 'MAE_new': g.apply(lambda s: (s.n_margin - s.log_m).abs().mean())})
    if 'o_margin' in E:
        tab['OLD_m'] = g.o_margin.mean(); tab['MAE_old'] = g.apply(lambda s: (s.o_margin - s.log_m).abs().mean())
    print(tab.round(2).to_string())
    hi = E[E.ratio > 1.2]
    if len(hi):
        s = 'ratio>1.2 n=%d MAE new %.3f' % (len(hi), (hi.n_margin - hi.log_m).abs().mean())
        if 'o_margin' in hi: s += ' old %.3f' % (hi.o_margin - hi.log_m).abs().mean()
        print(s)
    return x

if __name__ == '__main__':
    a = sys.argv[1:]
    if len(a) == 4 and a[0] == 'extract': extract(a[1], a[2], a[3])
    elif len(a) >= 3 and a[0] == 'replay':
        cb = 2.5
        if '--cb' in a: i = a.index('--cb'); cb = float(a[i + 1]); del a[i:i + 2]
        replay(a[1], a[2], a[3] if len(a) > 3 else None, cb)
    else: print(__doc__); sys.exit(2)
