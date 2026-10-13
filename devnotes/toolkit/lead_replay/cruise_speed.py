#!/usr/bin/env python3
"""cruise_speed.py <schema_dir> <segs_dir> [t ...] (276cha, cr15.py 복원) carState.cruiseState.speed/enabled를 지정 시각(기본 112 114 116 118 120)에 출력.
275cha/276cha 로그에서는 cruiseState.speed가 0 m/s라(enabled=1) 로그에서 설정속도를 읽을 수 없었다. 그래서 설정속도를 자차 속도 17.9 m/s로 가정했다.
(longitudinalPlan에는 cruiseTarget 등이 있으나 표시속도 기준이라 vCluRatio만큼 다르다, HANDOFF 주의사항.) `python3 -I`로 실행. 결과 cruise_speed.pkl. 실차 검증 아님."""
import sys, glob, pickle
import numpy as np, capnp, zstandard
schema, segs_dir = sys.argv[1], sys.argv[2]
times = [float(x) for x in sys.argv[3:]] or [112, 114, 116, 118, 120]
capnp.remove_import_hook()
log = capnp.load(schema + '/log.capnp', imports=[schema, schema + '/include'])
segs = sorted(glob.glob(segs_dir + '/*/rlog.zst'), key=lambda p: int(p.split('/')[-2].split('--')[-1]))
t0 = None; rows = []
for sp in segs:
    for ev in log.Event.read_multiple_bytes(zstandard.ZstdDecompressor().stream_reader(open(sp, 'rb')).read()):
        w = ev.which()
        if t0 is None:
            if w == 'carState':
                t0 = ev.logMonoTime
            else:
                continue
        if w == 'carState':
            rows.append(((ev.logMonoTime - t0) * 1e-9, float(ev.carState.cruiseState.speed), bool(ev.carState.cruiseState.enabled)))
a = np.array(rows); pickle.dump(a, open('cruise_speed.pkl', 'wb'))
for q in times:
    k = np.abs(a[:, 0] - q).argmin(); print(q, 'cruiseState.speed %.2f m/s (%.0f km/h) enabled=%d' % (a[k, 1], a[k, 1] * 3.6, a[k, 2]))
