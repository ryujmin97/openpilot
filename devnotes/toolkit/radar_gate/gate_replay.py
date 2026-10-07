#!/usr/bin/env python3
"""257cha: EnableRadarTracks 0 vs -1 중 '비전 앞차 게이트' 차이를 rlog 프레임 단위로 재생(open-loop, 근사).
usage: gate_replay.py <schema_dir> <rlog.zst> [t_from t_to]
  schema_dir: log.capnp, car.capnp, custom.capnp, deprecated.capnp, include/c++.capnp를 한 폴더에 모은 것
  (carrot-ryu openpilot/cereal/*.capnp + opendbc_repo/opendbc/car/car.capnp, 252차 gap_replay와 같은 방식).
재생 규칙(670f72c 기준, 상수는 primary.py/controller.py 값):
  vision_fallback: prob>=0.40이면 채택, 0.35<prob<0.40이면 직전 채택이 있을 때 최대 10프레임 유지(primary.py _update_vision_fallback)
  모드 0: vision_fallback이 있고 prob>=0.40 이고 |dPath|<=1.0 m일 때만 leadOne 허용(controller.py _central_vision_fallback_allowed)
  모드 -1: vision_fallback만 있으면 허용(vision_only_lead_allowed)
한계: dPath는 modelV2.position을 vision x에서 보간해 근사(실제는 project_to_model_path), SCC 점이 없다고 가정하지 않고
  로그 liveTracks 개수를 같이 출력만 한다(점이 있으면 이 재생은 해당 프레임에서 의미가 없다), 실차 검증 아님."""
import sys
import numpy as np
import capnp, zstandard

MIN_P, HOLD_P, HOLD_N = 0.40, 0.35, 10
GATE_P, GATE_DPATH = 0.40, 1.0


def load(schema, path):
    capnp.remove_import_hook()
    log = capnp.load(schema + '/log.capnp', imports=[schema, schema + '/include'])
    data = zstandard.ZstdDecompressor().stream_reader(open(path, 'rb')).read()
    t0, mv, ve, lt, rows = None, None, np.nan, 0, []
    for ev in log.Event.read_multiple_bytes(data):
        w = ev.which()
        if w == 'initData':
            continue
        if t0 is None and w == 'carState':
            t0 = ev.logMonoTime
        if w == 'carState':
            ve = float(ev.carState.vEgo)
        if t0 is None:
            continue
        t = (ev.logMonoTime - t0) * 1e-9
        if w == 'liveTracks':
            lt = len(ev.liveTracks.points)
        elif w == 'modelV2':
            mv = ev.modelV2
        elif w == 'radarState':
            l = ev.radarState.leadOne
            vis = None
            if mv is not None and len(mv.leadsV3) > 0 and len(mv.leadsV3[0].x) > 0:
                ld = mv.leadsV3[0]
                px, py = list(mv.position.x), list(mv.position.y)
                dp = ld.y[0] - float(np.interp(ld.x[0], px, py)) if px else np.nan
                vis = (float(ld.prob), float(ld.x[0]), float(dp), float(ld.v[0]))
            rows.append(dict(t=t, vego=ve, trk=lt, st=bool(l.status), rad=bool(l.radar),
                             dRel=float(l.dRel), vLead=float(l.vLead), vis=vis))
    return rows


def replay(rows):
    fb, hold = None, 0
    for r in rows:
        v = r['vis']
        if v and v[0] >= MIN_P:
            fb, hold = v, 0
        elif v and v[0] > HOLD_P and fb is not None and hold < HOLD_N:
            fb, hold = v, hold + 1
        else:
            fb, hold = None, 0
        r['m0'] = fb is not None and fb[0] >= GATE_P and abs(fb[2]) <= GATE_DPATH
        r['m1'] = fb is not None


def main(schema, path, a=8.0, b=10.85):
    rows = load(schema, path)
    replay(rows)
    n = len(rows)
    print(f"frames {n}, liveTracks 비어 있지 않은 프레임 {sum(1 for r in rows if r['trk'] > 0)}, "
          f"첫 비어 있지 않은 시각 {next((r['t'] for r in rows if r['trk'] > 0), None)}")
    print(f"leadOne.radar True 프레임 {sum(1 for r in rows if r['rad'])}")
    for lo, hi in ((0, a), (a, b), (b, rows[-1]['t'])):
        s = [r for r in rows if lo <= r['t'] <= hi]
        ag = sum(1 for r in s if r['st'] == r['m0'])
        print(f"{lo:.2f}-{hi:.2f}s n={len(s)} 로그 앞차 {sum(r['st'] for r in s)} 모드0 재생 {sum(r['m0'] for r in s)} "
              f"(로그와 일치 {ag}/{len(s)}) 모드-1 재생 {sum(r['m1'] for r in s)}")
    s = [r for r in rows if a <= r['t'] <= b]
    drops = lambda k: sum(1 for x, y in zip(s, s[1:]) if x[k] and not y[k])
    print(f"{a}-{b}s 앞차 끊김 횟수: 로그 {drops('st')} 모드0 재생 {drops('m0')} 모드-1 재생 {drops('m1')}")
    for k in ('st', 'm0', 'm1'):
        print(f"첫 앞차 시각 {k}: {next((r['t'] for r in rows if r[k]), None)}")
    print("로그에서 앞차가 끊긴 프레임의 비전 prob/dPath(끊김 첫 프레임만):")
    prev = None
    for r in s:
        if prev is not None and prev['st'] and not r['st']:
            v = r['vis']
            print(f"  t={r['t']:.2f} " + ("비전 없음" if v is None else f"prob={v[0]:.2f} dPath={v[2]:.2f} x={v[1]:.1f}"))
        prev = r


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(1)
    main(sys.argv[1], sys.argv[2], *(float(x) for x in sys.argv[3:5]))

