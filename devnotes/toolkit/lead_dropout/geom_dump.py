#!/usr/bin/env python3
"""geom_dump.py <schema_dir> <repo_dir> <segs_dir>   (288cha, 287cha 에서 저장 못 한 도구를 다시 씀)
full_replay2.py 와 같은 재생에 VisionRadarMatcher 의 _match_* 메서드를 감싸 구간 안에서 어느 매처가 점을 돌려줬는지 찍는다.
  WRAP=a:b   route 초 구간(필수). 비전 후보의 d/prob/dPath(visdPath 줄)도 찍는다. 매 modelV2 프레임: 비전 d/y_rel, 레이더점 목록(id src d y vRel meas), 각 _match_* 반환(점 d/y/id 또는 None),
             최종 leadOne (status radar dRel).
  full_replay2.py 의 CMPFROM/QUIET/PROBFIX/FREEZE/YSHIFT 도 그대로 쓸 수 있다(QUIET=1 권장).
repo_dir 의 primary.py 를 고친 사본을 넘기면 그 코드로 재생한다. 한계: open-loop, 실차 검증 아님."""
import sys, os, glob, math, capnp, zstandard
SCHEMA, REPO, SEGS = sys.argv[1], sys.argv[2], sys.argv[3]
sys.path.insert(0, REPO); sys.path.insert(0, REPO + '/opendbc_repo')
from openpilot.selfdrive.carrot.radar_motion import DPathRadarController
from openpilot.selfdrive.carrot.radar_motion.coordinates import device_yaw_to_radar
capnp.remove_import_hook()
log = capnp.load(SCHEMA + '/log.capnp', imports=[SCHEMA, SCHEMA + '/include'])

def span(name, n):
    v = os.environ.get(name)
    return tuple(float(x) for x in v.split(':')[:n]) if v else None
PF = span('PROBFIX', 2); PMIN = float(os.environ.get('PROBMIN', '0.45'))
FZ = span('FREEZE', 3); YS = span('YSHIFT', 3); DU = span('DUMP', 2)
CMPFROM = float(os.environ.get('CMPFROM', '100')); QUIET = os.environ.get('QUIET')

def yaw_rate(lp):
    av = getattr(lp, 'angularVelocityDevice', None)
    if av is not None and bool(getattr(av, 'valid', False)) and bool(getattr(lp, 'inputsOK', False)) \
       and bool(getattr(lp, 'sensorsOK', False)):
        return device_yaw_to_radar(float(av.z))
    return 0.0

def load_events():
    out = []
    for d in sorted(glob.glob(SEGS + '/*/rlog.zst'), key=lambda p: int(p.rsplit('--', 1)[1].split('/')[0])):
        data = zstandard.ZstdDecompressor().stream_reader(open(d, 'rb')).read()
        out.extend(log.Event.read_multiple_bytes(data))
    return out

evs = load_events()
cp = ip = None
for e in evs:
    w = e.which()
    if w == 'carParams' and cp is None: cp = e.carParams
    if w == 'initData' and ip is None: ip = e.initData
    if cp is not None and ip is not None: break
prm = {x.key: bytes(x.value) for x in ip.params.entries}
geti = lambda k: int(prm.get(k, b'0') or b'0')
from openpilot.selfdrive.carrot.radar import effective_radar_track_mode
mode = effective_radar_track_mode(cp.brand, cp.radarUnavailable, geti('EnableRadarTracks'))
# radard_dpath 는 cereal 런타임(import openpilot.cereal)이 필요해 샌드박스에서 못 불러온다 -> corner_radar_enabled 를 줄여 쓴다.
# EnableCornerRadar > 0 인 로그는 CORNER_RADAR_FLAGS 마스크가 필요하므로 지원하지 않고 중단한다(000004a0 은 0).
if geti('EnableCornerRadar') > 0:
    sys.exit('EnableCornerRadar>0 로그는 이 도구가 지원하지 않는다(radard_dpath.corner_radar_enabled 필요)')
corner = False
ctl = DPathRadarController(prefer_corner_radar=corner,
    enable_radar_tracks=mode, cut_in_sensitivity=3, front_radar_measurement_delay_s=float(cp.radarDelay),
    production_live_tracks=True)


WR = span('WRAP', 2)
_now = [0.0]
if WR:
    import openpilot.selfdrive.carrot.radar_motion.primary as _P
    for _n in [n for n in dir(_P.VisionRadarMatcher) if n.startswith('_match_')]:
        def _mk(name, fn):
            def w(self, *a, **k):
                r = fn(self, *a, **k)
                if WR[0] <= _now[0] <= WR[1]:
                    pt = getattr(r, 'point', r) if r is not None else None
                    d = getattr(pt, 'd_rel', None)
                    print('     [%s] -> %s' % (name, 'None' if r is None else
                          ('pt d=%.1f y=%+.2f id=%s src=%s' % (d, getattr(pt, 'y_rel', 0), getattr(pt, 'track_id', '-'), getattr(pt, 'source', '-'))
                           if d is not None else type(r).__name__)))
                return r
            return w
        setattr(_P.VisionRadarMatcher, _n, _mk(_n, getattr(_P.VisionRadarMatcher, _n)))
    _orig_match = _P.VisionRadarMatcher.match
    def _match_wrap(self, model, points, path, *a, **k):
        if WR[0] <= _now[0] <= WR[1]:
            _v = _P.vision_lead_from_model(model)
            if _v is not None:
                _dp = _P.project_to_model_path(path, _v.d_rel, _v.y_rel).d_path
                print('     visdPath d=%.1f prob=%.2f dPath=%+.2f' % (_v.d_rel, _v.probability, _dp))
            else:
                print('     visdPath -')
        return _orig_match(self, model, points, path, *a, **k)
    _P.VisionRadarMatcher.match = _match_wrap

t_base = None
for e in evs:
    if e.which() == 'carState':
        t_base = e.logMonoTime; break
cs = lt = lp = None; lt_t = 0
last = None; fz_cache = {}; hist = []
rows = []; cmp_n = cmp_ok = 0; seq = []
if DU and not QUIET:
    print('route | rep st rad dRel | log st rad | prob(원->사용) | 비전 d y_rel(사용) | 레이더점 d y')
for e in evs:
    w = e.which(); rt = (e.logMonoTime - t_base) * 1e-9
    if w == 'carState': cs = e.carState
    elif w == 'liveTracks': lt = e.liveTracks; lt_t = e.logMonoTime
    elif w == 'livePose': lp = e.livePose
    elif w == 'modelV2':
        if cs is None or lt is None or lp is None: continue
        mb = e.modelV2.as_builder()
        p_raw = p_use = None; vis = None
        if len(mb.leadsV3) > 0:
            L = mb.leadsV3[0]; p_raw = float(L.prob)
            if FZ and FZ[0] <= rt <= FZ[1]:
                if 'v' not in fz_cache:
                    prev = [h for h in hist if h[0] < FZ[2]]
                    fz_cache['v'] = prev[-1][1:] if prev else None
                if fz_cache['v']:
                    L.x = [fz_cache['v'][0]] + list(L.x)[1:]; L.y = [fz_cache['v'][1]] + list(L.y)[1:]
            hist.append((rt, float(L.x[0]), float(L.y[0])))
            if PF and PF[0] <= rt <= PF[1] and L.prob < PMIN: L.prob = PMIN
            if YS and YS[0] <= rt <= YS[1]: L.y = [float(v) + YS[2] for v in L.y]
            p_use = float(L.prob); vis = (float(L.x[0]) - 1.52, -float(L.y[0]))
        t_model = float(mb.timestampEof if mb.timestampEof > 0 else e.logMonoTime) * 1e-9
        _now[0] = rt
        if WR and WR[0] <= rt <= WR[1]:
            _pp = [(p.dRel, p.yRel, getattr(p, 'trackId', '-'), getattr(p, 'source', getattr(p, 'radarSource', '-')), p.vRel, bool(getattr(p, 'measured', False))) for p in lt.points if p.dRel < 40]
            print('%.2f vEgo=%.2f vis=%s pts=%s' % (rt, cs.vEgo, ('d=%.1f y_rel=%+.2f' % vis) if vis else '-', ['id%s %s d=%.1f y=%+.2f vR=%+.1f m=%d' % (q[2], q[3], q[0], q[1], q[4], q[5]) for q in sorted(_pp)]))
        out = ctl.update(time_s=t_model, v_ego=float(cs.vEgo), radar_points=lt.points, model=mb,
                         yaw_rate_rad_s=yaw_rate(lp), radar_to_model_time_s=t_model - lt_t * 1e-9)
        lo = out.lead_one or {}
        if WR and WR[0] <= rt <= WR[1]: print('     leadOne st=%s radar=%s dRel=%.1f' % (lo.get('status'), lo.get('radar'), float(lo.get('dRel', 0.0))))
        last = (bool(lo.get('status', False)), bool(lo.get('radar', False)), float(lo.get('dRel', 0.0)), rt)
        if DU and DU[0] <= rt <= DU[1] and not QUIET:
            pts = [(abs(p.yRel), p.dRel, p.yRel) for p in lt.points if p.measured and p.dRel < 60]
            pt = min(pts)[1:] if pts else None
            seq.append((rt, last, p_raw, p_use, vis, pt))
    elif w == 'radarState' and last is not None:
        l1 = e.radarState.leadOne
        ls, lr = bool(l1.status), bool(l1.radar)
        rows.append((rt, last[0], last[1], ls, lr))
        if rt >= CMPFROM:
            cmp_n += 1; cmp_ok += (last[0], last[1]) == (ls, lr)
        if DU and DU[0] <= rt <= DU[1] and not QUIET and seq:
            r0, lv, pr, pu, vis, pt = seq[-1]
            print(' %.2f | %d %d %5.1f | %d %d | %s | %s | %s' % (
                rt, lv[0], lv[1], lv[2], ls, lr,
                ('%.2f->%.2f' % (pr, pu)) if pr is not None else '-',
                ('%.1f %+.2f' % vis) if vis else '-',
                ('%.1f/%+.2f' % pt) if pt else ''))
print('재생 %d, 비교(route>=%g) %d | (status,radar) 로그 일치 %d (%.2f%%)' % (
    len(rows), CMPFROM, cmp_n, cmp_ok, 100.0 * cmp_ok / max(cmp_n, 1)))
gaps = []; cur = None
for rt, s, r, ls, lr in rows:
    if rt < 90: continue
    if not s and cur is None: cur = [rt, rt]
    elif not s: cur[1] = rt
    elif cur: gaps.append(cur); cur = None
print('replay 끊김 구간(status False): ' + ', '.join('%.2f~%.2f' % tuple(g) for g in gaps))
