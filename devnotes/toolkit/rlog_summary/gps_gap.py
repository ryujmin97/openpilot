"""gpsLocation 개수와 1.5초 넘는 공백(읽기 전용). 사용: python3 gps_gap.py <rlog.zst> [...]
시각은 각 rlog의 첫 carState를 0으로 한 초. 공백 원인(터널 등 환경/장치)은 가르지 못한다."""
import sys
from load import events
for path in sys.argv[1:]:
    base = None; ts = []; n_ext = 0
    for e in events(path):
        w = e.which()
        if w == 'carState' and base is None: base = e.logMonoTime
        elif w == 'gpsLocation' and base is not None: ts.append((e.logMonoTime - base) / 1e9)
        elif w == 'gpsLocationExternal': n_ext += 1
    gaps = [(a, b) for a, b in zip(ts, ts[1:]) if b - a > 1.5]
    print(path.split('/')[-2], "gpsLocation=%d gpsLocationExternal=%d first=%.1f last=%.1f gaps(>1.5s)=%s" % (
        len(ts), n_ext, ts[0] if ts else -1, ts[-1] if ts else -1, ["%.1f~%.1f(%.1fs)" % (a, b, b - a) for a, b in gaps]))
