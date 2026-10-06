#!/usr/bin/env python3
"""255cha: longitudinalPlan 20Hz 프레임마다 최신 상태 병합(252cha gap_replay.extract보다 필드 확장).
usage: ext2.py <schema_dir> <segs_dir> <out.pkl>"""
import sys, os, glob, pickle
import numpy as np, pandas as pd

raw = lambda x: int(x.raw) if hasattr(x, 'raw') else int(x)

def main(schema, segs, out):
    import capnp, zstandard
    capnp.remove_import_hook()
    log = capnp.load(schema + '/log.capnp', imports=[schema, schema + '/include'])
    paths = sorted(glob.glob(os.path.join(segs, '*', 'rlog.zst')),
                   key=lambda p: int(os.path.basename(os.path.dirname(p)).split('--')[-1]))
    rows, params, t0 = [], {}, None
    st = dict(vEgo=np.nan, aEgo=np.nan, gas=False, brake=False, standstill=False, vCruise=np.nan,
              longActive=False, accelCmd=np.nan, pers=-1, exp=False, enabled=False, lc=0)
    lead = dict(status=False, radar=False, tid=-1, dRel=np.nan, yRel=np.nan, vRel=np.nan, vLead=np.nan,
                aLeadK=np.nan, aLeadTau=np.nan, modelProb=np.nan)
    lead2 = False
    ev_count = {}
    for sp in paths:
        seg = int(os.path.basename(os.path.dirname(sp)).split('--')[-1])
        data = zstandard.ZstdDecompressor().stream_reader(open(sp, 'rb')).read()
        for ev in log.Event.read_multiple_bytes(data):
            w = ev.which()
            ev_count[w] = ev_count.get(w, 0) + 1
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
            if w == 'carState':
                c = ev.carState
                st.update(vEgo=float(c.vEgo), aEgo=float(c.aEgo), gas=bool(c.gasPressed), brake=bool(c.brakePressed),
                          standstill=bool(c.standstill), vCruise=float(c.vCruise))
            elif w == 'selfdriveState':
                s = ev.selfdriveState
                st.update(pers=raw(s.personality), exp=bool(s.experimentalMode), enabled=bool(s.enabled))
            elif w == 'carControl':
                cc = ev.carControl
                st.update(longActive=bool(cc.longActive), accelCmd=float(cc.actuators.accel))
            elif w == 'modelV2':
                st.update(lc=raw(ev.modelV2.meta.laneChangeState))
            elif w == 'radarState':
                l = ev.radarState.leadOne
                lead = dict(status=bool(l.status), radar=bool(l.radar), tid=int(l.radarTrackId), dRel=float(l.dRel),
                            yRel=float(l.yRel), vRel=float(l.vRel), vLead=float(l.vLead), aLeadK=float(l.aLeadK),
                            aLeadTau=float(l.aLeadTau), modelProb=float(l.modelProb))
                lead2 = bool(ev.radarState.leadTwo.status)
            elif w == 'longitudinalPlan':
                p = ev.longitudinalPlan
                rows.append(dict(t=t, seg=seg, **st, **{'r_' + k: v for k, v in lead.items()}, lead2=lead2,
                                 tFollow=float(p.tFollow), desired=float(p.desiredDistance), aTarget=float(p.aTarget),
                                 aTargetBase=float(p.aTargetBase), src=raw(p.longitudinalPlanSource),
                                 shouldStop=bool(p.shouldStop), hasLead=bool(p.hasLead), fcw=bool(p.fcw),
                                 jTarget=float(p.jTargetNow), xState=int(p.xState), vTargetNow=float(p.vTargetNow),
                                 cruiseTarget=float(p.cruiseTarget), allowThrottle=bool(p.allowThrottle),
                                 leadPrev=float(p.leadPreviewSeconds), aChangeCost=float(p.aChangeCost),
                                 myMode=int(p.myDrivingMode), a0=float(p.accels[0]) if len(p.accels) else np.nan,
                                 a5=float(p.accels[5]) if len(p.accels) > 5 else np.nan,
                                 a10=float(p.accels[10]) if len(p.accels) > 10 else np.nan))
    pickle.dump(dict(df=pd.DataFrame(rows), params=params, ev_count=ev_count), open(out, 'wb'))
    print(len(rows), 'plan frames, commit', params.get('_gitCommit'), 'dirty', params.get('_dirty'))
    print('events', {k: v for k, v in sorted(ev_count.items(), key=lambda kv: -kv[1])[:12]})

if __name__ == '__main__':
    main(*sys.argv[1:4])
