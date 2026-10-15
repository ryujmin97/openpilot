"""leadOne 구간 출력(읽기 전용). 사용: python3 lead_win.py <rlog.zst> <t_from> <t_to> [step_s]
시각은 그 rlog의 첫 carState를 0으로 한 초. radar False면 비전 단독(carrot-ryu 스키마)."""
import sys
from load import events
path, t0_, t1_ = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
step = float(sys.argv[4]) if len(sys.argv) > 4 else 0.25
base = None; vego = 0.0; rows = []
for e in events(path):
    w = e.which()
    if w == 'carState':
        if base is None: base = e.logMonoTime
        vego = e.carState.vEgo
    elif w == 'radarState' and base is not None:
        t = (e.logMonoTime - base) / 1e9
        if t0_ <= t <= t1_:
            l = e.radarState.leadOne
            rows.append((t, vego, l.status, l.dRel, l.yRel, l.vRel, l.radar))
best = min((r for r in rows if r[2]), key=lambda r: r[3], default=None)
if best:
    print("min dRel(status True): t=%.2f vEgo=%.1f dRel=%.1f yRel=%.2f vRel=%+.2f radar=%s" % (best[0], best[1], best[3], best[4], best[5], best[6]))
else:
    print("no status-True leadOne in window")
nxt = t0_
for r in rows:
    if r[0] >= nxt:
        print("t=%6.2f status=%-5s dRel=%6.1f yRel=%+5.2f vRel=%+5.2f radar=%s" % (r[0], r[2], r[3], r[4], r[5], r[6]))
        nxt = r[0] + step
