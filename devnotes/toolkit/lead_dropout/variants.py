#!/usr/bin/env python3
"""variants.py <schema_dir> <repo_dir> <segs_dir> [ev_from:ev_to=97.90:99.09]  (286cha, 앞 구간 기록에서 복원)
1326f21 이상 carrot-ryu의 비전 앞차 중앙 차선 게이트(진입 prob 0.40 + |dPath| 1.0 m, 유지 중 prob 이상이면 해제 대역 이내이거나 유예 프레임)를
변형 파라미터로 오프라인 재생하는 open-loop 비교표. 입력은 연속 세그먼트 폴더(<segs_dir>/*--<n>/rlog.zst, 번호순 route 시각)이고,
세그먼트별 route 오프셋은 각 세그먼트 첫 carState 시각에서 계산한다(000004a0은 0 / 60.021 / 119.991).
변형 V0..V5(현행, 유지 prob 0.35, 해제 대역 2.5/4.0 m, 유예 10프레임 등)마다 출력: 로그 leadOne.status와 일치하는 프레임 수(레이더 앞차 없는 프레임 중),
크루즈 중 0.25 s 이상 끊김 목록, ev 구간 present 비율, 로그보다 늘어난 present(크루즈 중)의 프레임 수/최대 |dPath|/최소 dRel.
중요: 게이트는 실제 controller.py가 아니라 이 파일 안의 재구현이다(V0가 레이더 앞차 없는 프레임에서 로그와 전부 일치하는지로 구현을 확인한다).
실제 코드 호출은 radar_gate/release_replay.py를 쓴다. dPath는 repo의 실제 radar_motion/predictor.py `project_to_model_path`를 import한다
(<repo_dir>에 openpilot/selfdrive/carrot/radar_motion/*.py와 opendbc_repo 필요). `python3 -I`로 실행(PYTHONPATH 무시, sys.path는 파일 안에서 넣는다).
후보 구성은 release_replay.py와 같다(d_rel = x[0]-1.52, y_rel = -y[0], 채택 prob 0.40, 0.35 초과 최대 10프레임 유지, 직전 modelV2).
한계: open-loop(자차 거동, 오감속 미시뮬레이션), 옆 차선 오감속 위험은 평가하지 않는다. 의존: pycapnp zstandard numpy. 실차 검증 아님."""
import sys, math, types, glob
import numpy as np, capnp, zstandard

RTC, MIN_P, HOLD_P, HOLD_N = 1.52, 0.40, 0.35, 10

def seg_no(p): return int(p.split('/')[-2].split('--')[-1])

def main():
    schema, repo, segs = sys.argv[1], sys.argv[2], sys.argv[3]
    ev_a, ev_b = map(float, (sys.argv[4] if len(sys.argv) > 4 else '97.90:99.09').split(':'))
    sys.path.insert(0, repo); sys.path.insert(0, repo + '/opendbc_repo')
    from openpilot.selfdrive.carrot.radar_motion.predictor import project_to_model_path
    capnp.remove_import_hook()
    log = capnp.load(schema + '/log.capnp', imports=[schema, schema + '/include'])
    paths = sorted(glob.glob(segs + '/*/rlog.zst'), key=seg_no)

    def read(sp):
        return zstandard.ZstdDecompressor().stream_reader(open(sp, 'rb')).read()

    def first_car_state(data):
        for ev in log.Event.read_multiple_bytes(data):
            if ev.which() == 'carState': return ev.logMonoTime

    def collect(data, off):
        t0 = None; fb = None; hold = 0; mv_last = None; cs = (None, None); fr = []
        for ev in log.Event.read_multiple_bytes(data):
            w = ev.which()
            if w == 'initData': continue
            if t0 is None and w == 'carState': t0 = ev.logMonoTime
            if t0 is None: continue
            t = (ev.logMonoTime - t0) * 1e-9
            if w == 'carState': cs = (float(ev.carState.vEgo), bool(ev.carState.cruiseState.enabled))
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
                dp = None
                if fb is not None and mv_last: dp = abs(project_to_model_path(mv_last, fb.d_rel, fb.y_rel).d_path)
                fr.append(dict(t=t + off, rad=bool(l.radar), st=bool(l.status), fb=fb, dp=dp, ve=cs[0], cr=cs[1]))
        return fr

    def run(fr, rel_band, hold_frames, hold_p):
        active = False; nrel = 0; out = []
        for r in fr:
            v = r['fb']
            if r['rad']: v = None
            if v is None: active = False; nrel = 0; out.append(False); continue
            if v.probability >= MIN_P and r['dp'] is not None and r['dp'] <= 1.0:
                active = True; nrel = 0; out.append(True); continue
            if active and v.probability >= hold_p and r['dp'] is not None:
                if r['dp'] <= rel_band: nrel = 0; out.append(True); continue
                if nrel < hold_frames: nrel += 1; out.append(True); continue
            active = False; nrel = 0; out.append(False)
        return out

    datas = [read(p) for p in paths]
    base = first_car_state(datas[0])
    frames = []
    for p, data in zip(paths, datas):
        off = (first_car_state(data) - base) * 1e-9
        print(f'seg {seg_no(p)} route 오프셋 {off:.3f}')
        frames += collect(data, off)
    print('radarState 프레임', len(frames))
    V = [('V0 현행(1.0/1.5 m, 3프레임, 유지 prob 0.40)', 1.5, 3, 0.40),
         ('V1 유지 prob 0.35', 1.5, 3, 0.35),
         ('V2 해제 대역 2.5 m', 2.5, 3, 0.40),
         ('V3 해제 대역 2.5 m + prob 0.35', 2.5, 3, 0.35),
         ('V4 해제 대역 4.0 m + prob 0.35', 4.0, 3, 0.35),
         ('V5 대역 1.5 m + 유예 10프레임 + prob 0.35', 1.5, 10, 0.35)]
    for name, rb, hf, hp in V:
        pres = run(frames, rb, hf, hp)
        newp = [p or f['rad'] for p, f in zip(pres, frames)]
        nr = [i for i, f in enumerate(frames) if not f['rad']]
        match = sum(pres[i] == frames[i]['st'] for i in nr)
        cr = [f['cr'] for f in frames]; T = [f['t'] for f in frames]
        gaps = []; i = 0
        while i < len(newp):
            if not newp[i] and i > 0 and newp[i - 1] and cr[i]:
                j = i
                while j < len(newp) and not newp[j]: j += 1
                if j < len(newp) and (j - i) * 0.05 >= 0.25: gaps.append((round(T[i], 2), round((j - i) * 0.05, 2)))
                i = j
            else: i += 1
        ev = [k for k, f in enumerate(frames) if ev_a <= f['t'] <= ev_b]
        cov = sum(newp[k] for k in ev) / len(ev) if ev else float('nan')
        extra = [i for i in nr if pres[i] and not frames[i]['st'] and frames[i]['cr']]
        mxd = max((frames[i]['dp'] for i in extra), default=0); mnd = min((frames[i]['fb'].d_rel for i in extra), default=0)
        print(f"{name}\n   로그 일치(레이더 앞차 없는 프레임) {match}/{len(nr)} | 크루즈 중 0.25s+ 끊김 {len(gaps)}건 {gaps} | {ev_a}~{ev_b}초 present 비율 {cov:.2f} | 로그보다 늘어난 present(크루즈 중) {len(extra)}프레임, 최대|dPath| {mxd:.2f} m, 최소dRel {mnd:.1f} m")

main()
