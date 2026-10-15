"""모델 차선 상태 구간 출력(읽기 전용). 사용: python3 lane_win.py <rlog.zst> <t_from> <t_to> [step_s]
시각은 그 rlog의 첫 carState를 0으로 한 초. modelV2 meta의 laneChangeState/Direction, 차선 폭(L/R), 변경 가능(AL/AR),
laneLines 안쪽 두 줄(index 1,2)의 첫 점 y와 확률, 중간값 mid=(yL+yR)/2를 step 간격으로 출력한다."""
import sys
from load import events
path, t0_, t1_ = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
step = float(sys.argv[4]) if len(sys.argv) > 4 else 0.5
base = None; nxt = t0_
for e in events(path):
    w = e.which()
    if w == 'carState' and base is None: base = e.logMonoTime
    if w != 'modelV2' or base is None: continue
    t = (e.logMonoTime - base) / 1e9
    if t > t1_: break
    if t < nxt: continue
    m = e.modelV2; mt = m.meta; ll = m.laneLines; pr = m.laneLineProbs
    yl = ll[1].y[0] if len(ll) > 2 and len(ll[1].y) else float('nan')
    yr = ll[2].y[0] if len(ll) > 2 and len(ll[2].y) else float('nan')
    print("t=%6.2f lcs=%s dir=%s wL=%.1f wR=%.1f AL=%d AR=%d yL=%+.2f yR=%+.2f pL=%.2f pR=%.2f mid=%+.2f" % (
        t, mt.laneChangeState, mt.laneChangeDirection, mt.laneWidthLeft, mt.laneWidthRight,
        mt.laneChangeAvailableLeft, mt.laneChangeAvailableRight, yl, yr,
        pr[1] if len(pr) > 2 else -1, pr[2] if len(pr) > 2 else -1, (yl + yr) / 2))
    nxt = t + step
