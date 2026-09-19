#!/usr/bin/env python3
"""rlog.zst -> 시계열 pickle (carState, radarState.leadOne, longitudinalPlan).
사용: parse_lead_log.py <schema_dir> <seg_dir> <out.pkl>
  schema_dir: log.capnp/custom.capnp/deprecated.capnp/include/ + car.capnp 를 한 폴더에 모은 곳
              (로그를 기록한 커밋 기준으로 받을 것: tmux metadata.json의 git_commit)
  seg_dir   : '<route>--<n>/rlog.zst' 들이 든 폴더. n 순으로 읽음.
출력: {'cs':DataFrame, 'rs':DataFrame, 'lp':DataFrame} (t_abs=logMonoTime 초). 의존: pycapnp, zstandard, pandas
"""
import sys, os, io, glob, re
import capnp, zstandard, pandas as pd
schema_dir, seg_root, out = sys.argv[1:4]
capnp.remove_import_hook()
log = capnp.load(os.path.join(schema_dir, 'log.capnp'), imports=[schema_dir])
def segno(p): return int(re.search(r'--(\d+)$', os.path.dirname(p)).group(1))
files = sorted(glob.glob(os.path.join(seg_root, '*', 'rlog.zst')), key=segno)
rows = {'cs': [], 'rs': [], 'lp': []}
for f in files:
    n = segno(f)
    raw = zstandard.ZstdDecompressor().stream_reader(open(f, 'rb')).read()
    for ev in log.Event.read_multiple_bytes(raw):
        w = ev.which()
        if w not in ('carState', 'radarState', 'longitudinalPlan'):
            continue
        t = ev.logMonoTime * 1e-9
        if w == 'carState':
            c = ev.carState
            rows['cs'].append(dict(seg=n, t_abs=t, vEgo=c.vEgo, aEgo=c.aEgo))
        elif w == 'radarState':
            l = ev.radarState.leadOne
            rows['rs'].append(dict(seg=n, t_abs=t, status=l.status, dRel=l.dRel, vRel=l.vRel,
                                   vLead=l.vLead, vLeadK=l.vLeadK, aLeadK=l.aLeadK, aLeadTau=l.aLeadTau))
        else:
            p = ev.longitudinalPlan
            rows['lp'].append(dict(seg=n, t_abs=t, aTarget=p.aTarget, aTargetBase=p.aTargetBase,
                                   desiredDistance=p.desiredDistance, hasLead=p.hasLead, tFollow=p.tFollow,
                                   vTargetNow=p.vTargetNow, jTargetNow=p.jTargetNow,
                                   previewSec=p.leadPreviewSeconds, previewAccel=p.leadPreviewAccel,
                                   aChangeCost=p.aChangeCost, accels=list(p.accels), speeds=list(p.speeds), xState=p.xState, trafficState=p.trafficState))
    print(f'seg {n}: cs={len(rows["cs"])} rs={len(rows["rs"])} lp={len(rows["lp"])}', file=sys.stderr)
dfs = {k: pd.DataFrame(v) for k, v in rows.items()}
pd.to_pickle(dfs, out)
