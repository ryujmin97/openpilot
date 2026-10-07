#!/usr/bin/env python3
"""259cha: carrot-ryu 1326f21 의 DPathRadarController._update_vision_central_gate 를 실제 코드 그대로 호출해
rlog 의 비전 앞차 후보에 radarState 프레임마다 재생하고, 670f72c(진입 1.0 m 단독 게이트) 결과와 비교한다(open-loop).
usage: release_replay.py <schema_dir> <repo_dir> <rlog.zst> [t_from:t_to ...]
  schema_dir: log.capnp, car.capnp, custom.capnp, deprecated.capnp, include/c++.capnp 를 한 폴더에 모은 것(exact_gate.py 와 같음)
  repo_dir:   1326f21 이상 carrot-ryu 체크아웃 루트(openpilot/selfdrive/carrot/radar_motion/*.py 와 opendbc_repo 가 import 경로에 필요)
  구간 기본값 8.0:10.85 40.9:45.1 (258cha 에서 끊김이 있던 두 장면)
후보 구성은 exact_gate.py 와 같다: d_rel = x[0]-1.52, y_rel = -y[0], 채택 prob>=0.40, 0.35 초과 최대 10프레임 유지,
radarState 직전의 최신 modelV2 값. 레이더 앞차(leadOne.radar True)가 있는 프레임은 실제 코드가 vision=None 으로 게이트 상태를 초기화하는
경로라 비교 대상에서 빼고 present 로 계산한다(레이더 인계 지점을 끊김으로 세지 않기 위함, 259cha 에서 한 번 잘못 센 뒤 고침).
출력: 336 프레임 일치 여부, 670f72c 규칙/1326f21 규칙 present 수와 증감, 구간·전체 끊김 횟수, 추가 present 프레임 목록(dRel/prob/dPath/비전 v/자차 속도/크루즈),
  레이더 인계 직전후 프레임, 홀드 중 prob<0.40 present 수.
한계: open-loop(자차 거동 반영 없음, 오감속 시뮬레이션 아님), 세그먼트 1개 분석, 레이더/SCC 앞차 프레임은 대상 아님. 실차 검증 아님."""
import sys, math, types
from collections import Counter
import capnp, zstandard

RTC, MIN_P, HOLD_P, HOLD_N = 1.52, 0.40, 0.35, 10

def main():
    schema, repo, path = sys.argv[1], sys.argv[2], sys.argv[3]
    spans = [tuple(map(float, a.split(':'))) for a in sys.argv[4:]] or [(8.0, 10.85), (40.9, 45.1)]
    sys.path.insert(0, repo); sys.path.insert(0, repo + '/opendbc_repo')
    from openpilot.selfdrive.carrot.radar_motion import controller as C
    from openpilot.selfdrive.carrot.radar_motion.predictor import project_to_model_path
    capnp.remove_import_hook()
    log = capnp.load(schema + '/log.capnp', imports=[schema, schema + '/include'])
    data = zstandard.ZstdDecompressor().stream_reader(open(path, 'rb')).read()
    host = types.SimpleNamespace(_vision_central_gate_active=False, _vision_central_gate_release_frames=0)
    host._reset_vision_central_gate = lambda: C.DPathRadarController._reset_vision_central_gate(host)
    upd = lambda v, p: C.DPathRadarController._update_vision_central_gate(host, v, p)
    t0, fb, hold, lt, mv_last, rows, cs = None, None, 0, 0, None, [], (None, None)
    for ev in log.Event.read_multiple_bytes(data):
        w = ev.which()
        if w == 'initData': continue
        if t0 is None and w == 'carState': t0 = ev.logMonoTime
        if t0 is None: continue
        t = (ev.logMonoTime - t0) * 1e-9
        if w == 'carState': cs = (float(ev.carState.vEgo), bool(ev.carState.cruiseState.enabled))
        if w == 'liveTracks': lt = len(ev.liveTracks.points)
        elif w == 'modelV2':
            mv = ev.modelV2; v = None
            if len(mv.leadsV3) > 0:
                l = mv.leadsV3[0]
                if len(l.x) and len(l.y) and len(l.v) and l.x[0] - RTC > 0.5:
                    v = types.SimpleNamespace(probability=float(l.prob), d_rel=float(l.x[0] - RTC), y_rel=-float(l.y[0]), v=float(l.v[0]))
            if v and v.probability >= MIN_P: fb, hold = v, 0
            elif v and v.probability > HOLD_P and fb is not None and hold < HOLD_N: fb, hold = v, hold + 1
            else: fb, hold = None, 0
            mv_last = tuple((float(x), float(y)) for x, y in zip(mv.position.x, mv.position.y) if math.isfinite(x) and math.isfinite(y))
        elif w == 'radarState':
            l = ev.radarState.leadOne
            rad = bool(l.radar)
            old = fb is not None and C._central_vision_fallback_allowed(fb, mv_last or ())
            # 레이더 앞차가 있는 프레임은 primary_match 경로: 실제 코드는 gate에 vision=None을 넘겨 상태를 초기화한다
            new = upd(None if rad else fb, mv_last or ())
            dp = project_to_model_path(mv_last, fb.d_rel, fb.y_rel).d_path if (fb is not None and mv_last) else None
            rows.append(dict(t=t, st=bool(l.status), rad=rad, trk=lt, fb=fb, dp=dp, old=old, new=new, ve=cs[0], cr=cs[1], oldp=old or rad, newp=new or rad))
    print('radarState frames', len(rows))
    nr = [r for r in rows if not r['rad']]
    print('레이더 앞차 없는 프레임', len(nr), '/ 로그 present(leadOne.status)', sum(r['st'] for r in nr))
    print('  670f72c 규칙 재생 == 로그 status:', sum(r['old'] == r['st'] for r in nr), '/', len(nr))
    print('  1326f21 신규 게이트 present', sum(r['new'] for r in nr), ' 670f72c 규칙 present', sum(r['old'] for r in nr))
    print('  신규가 old보다 늘린 프레임', sum(r['new'] and not r['old'] for r in nr), ' 줄인 프레임', sum(r['old'] and not r['new'] for r in nr))
    def drops(rs, k): return sum(1 for a, b in zip(rs, rs[1:]) if a[k] and not b[k])
    for a, b in spans:
        s = [r for r in rows if a <= r['t'] <= b]
        print(f'{a}-{b}s n={len(s)} 로그 끊김 {drops(s,"st")} 670f72c재생 끊김 {drops(s,"oldp")} 1326f21재생 끊김 {drops(s,"newp")} (레이더 앞차 프레임은 present로 계산)')
    ex = [r for r in nr if r['new'] and not r['old']]
    print('추가 present 프레임', len(ex), ' dRel<15m', sum(r['fb'].d_rel < 15 for r in ex), ' dRel<20m', sum(r['fb'].d_rel < 20 for r in ex),
          ' 최대|dPath| %.2f' % max((abs(r['dp']) for r in ex), default=0), ' 최소dRel %.1f' % min((r['fb'].d_rel for r in ex), default=0))
    print('추가 프레임 중 cruiseState.enabled True', sum(r['cr'] for r in ex), ' 그중 dRel<15m', sum(r['cr'] and r['fb'].d_rel < 15 for r in ex), ' | dRel<15m 전체', sum(r['fb'].d_rel < 15 for r in ex))
    print('추가 프레임 시각대:', Counter(int(r['t']) for r in ex))
    print('추가 프레임 목록(t, dRel, prob, dPath, 비전v):')
    for r in ex: print('  t=%.2f dRel=%.1f p=%.2f dPath=%+.2f v=%.1f vEgo=%.1f cruise=%s' % (r['t'], r['fb'].d_rel, r['fb'].probability, r['dp'], r['fb'].v, r['ve'], r['cr']))
    print('전체 60초 끊김(레이더 포함 present): 로그', drops(rows,'st'), '670f72c재생', drops(rows,'oldp'), '1326f21재생', drops(rows,'newp'))
    print('1326f21 재생에서 남은 끊김(직전 present -> absent) 프레임 전후:')
    for i,(x,y) in enumerate(zip(rows,rows[1:])):
        if x['newp'] and not y['newp'] and any(a<=y['t']<=b for a,b in spans):
            for r in rows[max(0,i-2):i+4]:
                f=r['fb']
                print('  t=%.2f rad=%s trk=%d new=%s old=%s log=%s %s' % (r['t'], r['rad'], r['trk'], r['new'], r['old'], r['st'],
                      ('p=%.2f dRel=%.1f dPath=%+.2f' % (f.probability, f.d_rel, r['dp'])) if f else 'no vision'))
            print('  --')
    # 해제 홀드가 prob<0.40에서 끊기는지(실제 코드) 확인
    print('hold 중 prob<0.40 프레임에서 new True:', sum(r['new'] and r['fb'] is not None and r['fb'].probability < 0.40 for r in nr))
main()
