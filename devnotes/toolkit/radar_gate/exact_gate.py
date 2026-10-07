#!/usr/bin/env python3
"""258cha: 670f72c의 비전 앞차 게이트를 실제 코드 함수로 프레임 단위 재생(open-loop)하고, 끄는 문턱/홀드 완화안을 비교한다.
usage: exact_gate.py <schema_dir> <repo_dir> <rlog.zst> [t_from:t_to ...]
  schema_dir: log.capnp, car.capnp, custom.capnp, deprecated.capnp, include/c++.capnp를 한 폴더에 모은 것(gate_replay.py와 같음)
  repo_dir: carrot-ryu(로그 기록 커밋) 체크아웃 루트. openpilot/selfdrive/carrot/radar_motion/predictor.py의
            project_to_model_path를 직접 import한다(sys.path에 repo_dir과 repo_dir/opendbc_repo를 넣어 실행).
재생 규칙(controller.py/primary.py 값, EnableRadarTracks 0 기준):
  vision = modelV2.leadsV3[0]: d_rel = x[0] - 1.52, y_rel = -y[0], d_rel <= 0.5이면 없음, prob = prob
  채택: prob >= 0.40이면 채택, 0.35 < prob이고 직전 채택이 있으면 최대 10프레임 유지(_update_vision_fallback)
  게이트(_central_vision_fallback_allowed): prob >= 0.40 이고 |project_to_model_path(modelV2.position, d_rel, y_rel).d_path| <= 1.0 m
  모드 -1은 게이트를 건너뛴다. 비전 후보는 radarState 직전의 최신 modelV2 값을 쓴다.
출력: 구간별 로그 present/모드0 재생/모드-1 재생/일치/끊김 횟수와 불일치 프레임, 레이더 없는 프레임 전체 일치율, 끊긴 첫 프레임,
  완화안(끄는 문턱 exit, 홀드 프레임 수) 비교표와 비전 후보 |dPath| 분포.
한계: open-loop, 레이더/SCC 앞차가 있는 프레임은 재생 대상이 아니다(비교는 leadOne.radar False 프레임 기준),
  완화안은 제어 거동이나 오감속 영향을 시뮬레이션하지 않는다. 실차 검증 아님."""
import sys, math
import numpy as np
import capnp, zstandard

RTC, MIN_P, HOLD_P, HOLD_N, GP, GD = 1.52, 0.40, 0.35, 10, 0.40, 1.0


def load(schema, repo, path):
    sys.path.insert(0, repo)
    sys.path.insert(0, repo + '/opendbc_repo')
    from openpilot.selfdrive.carrot.radar_motion.predictor import project_to_model_path
    capnp.remove_import_hook()
    log = capnp.load(schema + '/log.capnp', imports=[schema, schema + '/include'])
    data = zstandard.ZstdDecompressor().stream_reader(open(path, 'rb')).read()
    t0, fb, hold, lt, rows = None, None, 0, 0, []
    for ev in log.Event.read_multiple_bytes(data):
        w = ev.which()
        if w == 'initData':
            continue
        if t0 is None and w == 'carState':
            t0 = ev.logMonoTime
        if t0 is None:
            continue
        t = (ev.logMonoTime - t0) * 1e-9
        if w == 'liveTracks':
            lt = len(ev.liveTracks.points)
        elif w == 'modelV2':
            mv, v = ev.modelV2, None
            if len(mv.leadsV3) > 0:
                l = mv.leadsV3[0]
                if len(l.x) and len(l.y) and len(l.v) and l.x[0] - RTC > 0.5:
                    v = dict(p=float(l.prob), d=float(l.x[0] - RTC), y=-float(l.y[0]))
            if v and v['p'] >= MIN_P:
                fb, hold = v, 0
            elif v and v['p'] > HOLD_P and fb is not None and hold < HOLD_N:
                fb, hold = v, hold + 1
            else:
                fb, hold = None, 0
            if fb is not None:
                pth = tuple((float(x), float(y)) for x, y in zip(mv.position.x, mv.position.y)
                            if math.isfinite(x) and math.isfinite(y))
                fb = dict(fb)
                fb['dp'] = project_to_model_path(pth, fb['d'], fb['y']).d_path
        elif w == 'radarState':
            l = ev.radarState.leadOne
            ok = fb is not None and fb['p'] >= GP and abs(fb['dp']) <= GD
            rows.append(dict(t=t, st=bool(l.status), rad=bool(l.radar), trk=lt, fb=fb, m0=ok, m1=fb is not None))
    return rows


def drops(s, k):
    return sum(1 for a, b in zip(s, s[1:]) if a[k] and not b[k])


def variant(rows, exit_, hold_n):
    on, h, out = False, 0, []
    for r in rows:
        f, ok = r['fb'], False
        if f is not None and f['p'] >= GP:
            ok = abs(f['dp']) <= (exit_ if on else GD)
        if ok:
            on, h = True, 0
        elif on and f is not None and h < hold_n:
            h, ok = h + 1, True
        else:
            on, h = False, 0
        out.append(ok)
    return out


def main(schema, repo, path, wins):
    rows = load(schema, repo, path)
    print(f"radarState frames {len(rows)}")
    for lo, hi in wins:
        s = [r for r in rows if lo <= r['t'] <= hi]
        mism = [r for r in s if r['st'] != r['m0']]
        print(f"{lo}-{hi}s n={len(s)} 로그 present {sum(r['st'] for r in s)} 모드0 재생 {sum(r['m0'] for r in s)} "
              f"모드-1 재생 {sum(r['m1'] for r in s)} 일치 {len(s) - len(mism)}/{len(s)} "
              f"끊김 로그 {drops(s, 'st')} 모드0 {drops(s, 'm0')} 모드-1 {drops(s, 'm1')}")
        for r in mism[:12]:
            f = r['fb']
            print(f"  불일치 t={r['t']:.2f} 로그 {r['st']} 재생 {r['m0']} " +
                  ("비전 없음" if f is None else f"prob={f['p']:.2f} dPath={f['dp']:.2f}"))
    nr = [r for r in rows if not r['rad']]
    print(f"레이더 앞차 없는 프레임 {len(nr)} 중 모드0 재생 일치 {sum(r['st'] == r['m0'] for r in nr)}")
    print("로그에서 앞차가 끊긴 첫 프레임(비전 후보 prob/dPath/dRel):")
    for a, b in zip(rows, rows[1:]):
        if a['st'] and not b['st']:
            f = b['fb']
            print(f"  t={b['t']:.2f} liveTracks={b['trk']} 모드0 재생 {b['m0']} " +
                  ("비전 없음" if f is None else f"prob={f['p']:.2f} dPath={f['dp']:.2f} dRel={f['d']:.1f}"))
    w = [i for i, r in enumerate(rows) if any(lo <= r['t'] <= hi for lo, hi in wins)]
    idx = [i for i, r in enumerate(rows) if not r['rad']]
    print("완화안(진입 1.0 m 고정, exit=끄는 문턱 m, hold=게이트 실패 뒤 비전 후보가 남아 있으면 유지할 프레임):")
    for name, ex, hn in (("현재", 1.0, 0), ("exit1.2", 1.2, 0), ("exit1.5", 1.5, 0), ("exit1.8", 1.8, 0),
                         ("hold3", 1.0, 3), ("hold6", 1.0, 6), ("exit1.5+hold3", 1.5, 3)):
        m = variant(rows, ex, hn)
        dw = sum(1 for i in w if i + 1 < len(rows) and m[i] and not m[i + 1])
        add = [i for i in idx if m[i] and not rows[i]['m0']]
        dps = [abs(rows[i]['fb']['dp']) for i in add if rows[i]['fb']]
        near = sum(1 for i in add if rows[i]['fb'] and rows[i]['fb']['d'] < 15)
        print(f"  {name:14s} 구간 내 끊김 {dw:2d} 레이더 없는 프레임 present {sum(m[i] for i in idx):3d} (+{len(add)}) "
              f"추가 프레임 최대 |dPath| {max(dps) if dps else 0:.2f} 15 m 미만 {near}")
    dp = [abs(rows[i]['fb']['dp']) for i in idx if rows[i]['fb'] is not None and rows[i]['fb']['p'] >= GP]
    print(f"레이더 없는 비전 후보 {len(dp)}프레임 |dPath| <=1.0 {sum(d <= 1.0 for d in dp)} 1.0~1.5 {sum(1.0 < d <= 1.5 for d in dp)} "
          f"1.5~2.0 {sum(1.5 < d <= 2.0 for d in dp)} >2.0 {sum(d > 2.0 for d in dp)}")


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)
    wins = [tuple(float(x) for x in a.split(':')) for a in sys.argv[4:]] or [(8.0, 10.85), (40.9, 45.1)]
    main(sys.argv[1], sys.argv[2], sys.argv[3], wins)
