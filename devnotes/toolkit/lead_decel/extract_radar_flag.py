#!/usr/bin/env python3
"""radarState.leadOne.radar / leadTwo.radar 플래그 추가 추출 (ego_extract2.py에 없는 필드). 사용: run/ 폴더에서 실행. 출력 out/radarflag.pkl"""
import glob, os, re, capnp, zstandard, pandas as pd
capnp.remove_import_hook()
log = capnp.load('../schema/log.capnp', imports=['../schema'])
def segno(p): return int(re.search(r'--(\d+)$', os.path.dirname(p)).group(1))
rows=[]
for f in sorted(glob.glob('../segs/*/rlog.zst'), key=segno):
    raw = zstandard.ZstdDecompressor().stream_reader(open(f,'rb')).read()
    for ev in log.Event.read_multiple_bytes(raw):
        if ev.which()=='radarState':
            r=ev.radarState; rows.append(dict(t_abs=ev.logMonoTime*1e-9, radar=r.leadOne.radar, radar2=r.leadTwo.radar))
pd.DataFrame(rows).to_pickle('out/radarflag.pkl'); print(len(rows))
