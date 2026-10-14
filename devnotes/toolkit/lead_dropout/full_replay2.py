#!/usr/bin/env python3
"""full_replay2.py <schema_dir> <repo_dir> <segs_dir>   (287cha, 이전 세션 full_replay2.py 를 이 세션에서 다시 쓴 판)
carrot-ryu 기록 커밋의 DPathRadarController 를 radard_dpath.DPathRadarD.update 와 같은 입력 구성으로
세그먼트들(<segs_dir>/<route>--<n>/rlog.zst, n 순서)에 이어서 재생한다(open-loop, 자차 거동 미반영).
  입력: model=modelV2(timestampEof 기준 시각), v_ego=carState.vEgo, radar_points=liveTracks.points,
        yaw=livePose(angularVelocityDevice, inputsOK, sensorsOK), radar_to_model_time_s=model_t-liveTracks_t
  컨트롤러 인자는 로그 안 CarParams/initData.params(EnableRadarTracks, EnableCornerRadar)에서 읽는다.
  비교: 매 radarState 프레임의 leadOne (status, radar) 를 직전 modelV2 재생 결과와 대조(route>=CMPFROM).
  route 시각 = 첫 세그먼트 첫 carState 기준 mono 초(세그먼트가 이어지므로 연속).
환경변수:
  DUMP="a:b"           route 초 구간의 프레임표 출력(재생 status/radar/dRel | 로그 | prob | 비전 d,y_rel | 레이더점)
  PROBFIX="a:b"        a~b 동안 비전 prob 가 PROBMIN(기본 0.45) 미만이면 PROBMIN 으로 올림
  FREEZE="a:b:src_t"   a~b 동안 비전 x/y 를 src_t 직전 마지막 값으로 고정
  YSHIFT="a:b:dy"      a~b 동안 비전 y 에 dy 를 더함(모델 y 부호 기준, y_rel = -y)
  CMPFROM=100          비교 시작 route 초(기본 100: 크루즈 시작 뒤)
  QUIET=1              비교 요약과 끊김 구간만 출력(DUMP 표 생략)
repo_dir 의 primary.py 를 고친 사본(src_cf)을 넘기면 그 코드로 재생한다. 한계: open-loop, 실차 검증 아님."""
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
        out = ctl.update(time_s=t_model, v_ego=float(cs.vEgo), radar_points=lt.points, model=mb,
                         yaw_rate_rad_s=yaw_rate(lp), radar_to_model_time_s=t_model - lt_t * 1e-9)
        lo = out.lead_one or {}
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
