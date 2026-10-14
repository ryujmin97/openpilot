"""track_dump.py <schema_dir> <segs_dir> <t_from> <t_to> [max_d]   (288cha, 287cha 에서 저장 못 한 도구를 다시 씀)
route 초(첫 carState 기준 mono 초) 구간에서 liveTracks 의 모든 점(measured 여부 포함)과 자차 vEgo, 비전 후보(modelV2.leadsV3[0])의
d/y/v/prob 를 liveTracks 프레임마다 한 블록으로 출력한다. 점은 dRel < max_d(기본 40) 만, dRel 순.
점 필드: trackId dRel yRel vRel measured (스키마에 있는 필드만; 없으면 '-').  open-loop 로그 읽기 전용, 실차 검증 아님."""
import sys, glob, capnp, zstandard
SCHEMA, SEGS, T0, T1 = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
MAXD = float(sys.argv[5]) if len(sys.argv) > 5 else 40.0
capnp.remove_import_hook()
log = capnp.load(SCHEMA + '/log.capnp', imports=[SCHEMA, SCHEMA + '/include'])
evs = []
for d in sorted(glob.glob(SEGS + '/*/rlog.zst'), key=lambda p: int(p.rsplit('--', 1)[1].split('/')[0])):
    evs.extend(log.Event.read_multiple_bytes(zstandard.ZstdDecompressor().stream_reader(open(d, 'rb')).read()))
tb = next(e.logMonoTime for e in evs if e.which() == 'carState')
vego = None; vis = None
fl = lambda p, k: (('%.2f' % getattr(p, k)) if hasattr(p, k) else '-')
for e in evs:
    w = e.which(); rt = (e.logMonoTime - tb) * 1e-9
    if w == 'carState': vego = e.carState.vEgo
    elif w == 'modelV2':
        m = e.modelV2
        vis = None
        if len(m.leadsV3) > 0:
            L = m.leadsV3[0]; vis = (L.x[0] - 1.52, -L.y[0], L.v[0], L.prob)
    elif w == 'liveTracks' and T0 <= rt <= T1:
        pts = sorted([p for p in e.liveTracks.points if p.dRel < MAXD], key=lambda p: p.dRel)
        v = ('vis d=%.1f y_rel=%+.2f v=%.1f prob=%.2f' % vis) if vis else 'vis -'
        print('%.2f vEgo=%.2f | %s' % (rt, vego or 0, v))
        for p in pts:
            tid = getattr(p, 'trackId', '-')
            print('     id=%s d=%.1f y=%+.2f vRel=%+.2f meas=%s src=%s' % (
                tid, p.dRel, p.yRel, p.vRel, getattr(p, 'measured', '-'), getattr(p, 'source', getattr(p, 'radarSource', '-'))))
