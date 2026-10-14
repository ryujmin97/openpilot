#!/usr/bin/env python3
"""lane_check.py <rlog.zst> <t_from> <t_to> [route_offset=0]  (286cha, 앞 구간 기록에서 복원)
rlog 1개의 modelV2에서 leadsV3[0] 후보(prob, x, y)와 가까운 좌/우 차선(laneLines[1]/[2])의 y를 후보 x에서 보간해, 후보가 두 차선 사이 어디인지
(0 = 왼쪽 선, 1 = 오른쪽 선, 범위 밖이면 차선 밖)와 모델 경로(position) y, 선 확률을 약 0.1 s 간격으로 출력한다.
t_from/t_to는 세그먼트 로컬 시각(첫 carState 기준), route_offset은 route 시각 표시용 더하기(세그먼트 2는 60.021, 3은 119.991 등).
스키마 폴더는 환경변수 SCHEMA_DIR(기본 /tmp/schema, log.capnp car.capnp custom.capnp deprecated.capnp include/c++.capnp). `python3 -I`로 실행.
initData는 읽지 않는다. 의존: pycapnp zstandard numpy. 부호 해석(y 양수가 오른쪽)은 modeld 규약 기준이며 이 파일이 확인하지 않는다. 실차 검증 아님."""
import sys, os, numpy as np, capnp, zstandard

SCHEMA = os.environ.get('SCHEMA_DIR', '/tmp/schema')
capnp.remove_import_hook()
log = capnp.load(SCHEMA + '/log.capnp', imports=[SCHEMA, SCHEMA + '/include'])
path, a, b = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]); OFF = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0
data = zstandard.ZstdDecompressor().stream_reader(open(path, 'rb')).read()
t0 = None; last_t = -9
print(' local  route | lead: prob   x(m)  y(m) | lane L(y) R(y) @x  width | 위치(0=좌선,1=우선) | path y@x | 선 확률 L/R')
for ev in log.Event.read_multiple_bytes(data):
    w = ev.which()
    if w == 'initData': continue
    if t0 is None and w == 'carState': t0 = ev.logMonoTime
    if t0 is None or w != 'modelV2': continue
    t = (ev.logMonoTime - t0) * 1e-9
    if t < a or t > b or t - last_t < 0.095: continue
    mv = ev.modelV2
    if not len(mv.leadsV3) or not len(mv.leadsV3[0].x): continue
    l = mv.leadsV3[0]; x = float(l.x[0]); y = float(l.y[0]); pr = float(l.prob)
    ll = mv.laneLines

    def yat(line, xx):
        xs = np.array(list(line.x)); ys = np.array(list(line.y)); return float(np.interp(xx, xs, ys))
    yL = yat(ll[1], x); yR = yat(ll[2], x)
    py = yat(mv.position, x)
    frac = (y - yL) / (yR - yL) if abs(yR - yL) > 1e-3 else float('nan')
    pl = list(mv.laneLineProbs)
    print(f"{t:6.2f} {t+OFF:6.2f} |      {pr:4.2f} {x:5.1f} {y:+5.2f} |     {yL:+5.2f} {yR:+5.2f}      {abs(yR-yL):4.2f} |   {frac:5.2f}  {'(차선 안)' if 0<=frac<=1 else '(차선 밖)'} | {py:+5.2f} | {pl[1]:.2f}/{pl[2]:.2f}")
    last_t = t
