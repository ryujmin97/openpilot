#!/usr/bin/env python3
"""260cha: carrot-ryu 1326f21 의 DPathRadarController._update_vision_central_gate 를 실제 코드로 rlog 여러 개에 재생해,
레이더 앞차(leadOne.radar True)가 없는 radarState 프레임 중 cruiseState.enabled 인 프레임만 세그먼트별로 집계한다
(n=레이더 앞차 없는 프레임, cr=그중 크루즈 작동, cand_cr=비전 후보 있음, old_cr/new_cr=670f72c/1326f21 규칙 present,
 extra_cr=새로 present, blocked_cr=후보가 있는데 새 규칙도 차단, slower_blocked=차단된 후보 중 비전 v 가 자차보다 1 m/s 이상 느림,
 minblk=차단된 후보의 최소 |dPath|).
usage: margin_scan.py <schema_dir> <repo_dir> <rlog.zst> [<rlog.zst> ...]   (release_replay.py 와 같은 schema_dir/repo_dir)
한계: open-loop, 후보가 옆 차선인지 자차 차선인지는 판정하지 않는다. 차단 사유(prob 인지 dPath 인지)는 구분하지 않는다. 실차 검증 아님."""
import sys, math, types
import capnp, zstandard
RTC, MIN_P, HOLD_P, HOLD_N = 1.52, 0.40, 0.35, 10
schema, repo = sys.argv[1], sys.argv[2]
sys.path.insert(0, repo); sys.path.insert(0, repo + '/opendbc_repo')
from openpilot.selfdrive.carrot.radar_motion import controller as C
from openpilot.selfdrive.carrot.radar_motion.predictor import project_to_model_path
capnp.remove_import_hook()
log = capnp.load(schema + '/log.capnp', imports=[schema, schema + '/include'])
tot = dict(n=0, cruise=0, cand=0, cand_cr=0, old_cr=0, new_cr=0, extra_cr=0, blocked_cr=0)
band = {}
for path in sys.argv[3:]:
    data = zstandard.ZstdDecompressor().stream_reader(open(path, 'rb')).read()
    host = types.SimpleNamespace(_vision_central_gate_active=False, _vision_central_gate_release_frames=0)
    host._reset_vision_central_gate = lambda: C.DPathRadarController._reset_vision_central_gate(host)
    upd = lambda v, p: C.DPathRadarController._update_vision_central_gate(host, v, p)
    fb, hold, mv_last, cs, t0 = None, 0, None, (0, False), None
    seg = dict(n=0, cr=0, cand_cr=0, old_cr=0, new_cr=0, extra_cr=0, blocked_cr=0, slower_blocked=0, minblk=None)
    for ev in log.Event.read_multiple_bytes(data):
        w = ev.which()
        if w == 'initData': continue
        if w == 'carState': cs = (float(ev.carState.vEgo), bool(ev.carState.cruiseState.enabled))
        if w == 'modelV2':
            mv = ev.modelV2; v = None
            if len(mv.leadsV3) > 0:
                l = mv.leadsV3[0]
                if len(l.x) and len(l.y) and len(l.v) and l.x[0] - RTC > 0.5:
                    v = types.SimpleNamespace(probability=float(l.prob), d_rel=float(l.x[0]-RTC), y_rel=-float(l.y[0]), v=float(l.v[0]))
            if v and v.probability >= MIN_P: fb, hold = v, 0
            elif v and v.probability > HOLD_P and fb is not None and hold < HOLD_N: fb, hold = v, hold+1
            else: fb, hold = None, 0
            mv_last = tuple((float(x), float(y)) for x, y in zip(mv.position.x, mv.position.y) if math.isfinite(x) and math.isfinite(y))
        elif w == 'radarState':
            rad = bool(ev.radarState.leadOne.radar)
            old = fb is not None and C._central_vision_fallback_allowed(fb, mv_last or ())
            new = upd(None if rad else fb, mv_last or ())
            if rad: continue
            seg['n'] += 1
            if not cs[1]: continue
            seg['cr'] += 1
            if fb is not None: seg['cand_cr'] += 1
            seg['old_cr'] += bool(old); seg['new_cr'] += bool(new)
            seg['extra_cr'] += bool(new and not old)
            if fb is not None and not new:
                seg['blocked_cr'] += 1
                dp = abs(project_to_model_path(mv_last, fb.d_rel, fb.y_rel).d_path) if mv_last else 99
                seg['minblk'] = dp if seg['minblk'] is None else min(seg['minblk'], dp)
                if fb.v < cs[0] - 1.0: seg['slower_blocked'] += 1
    print(path.split('/')[-2].split('--')[-1].rjust(3), {k: (round(v,2) if isinstance(v,float) else v) for k, v in seg.items()})
