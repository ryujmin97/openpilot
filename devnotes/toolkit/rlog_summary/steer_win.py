"""조향/개입/활성/가속 명령/깜빡이 구간 출력(읽기 전용). 사용: python3 steer_win.py <rlog.zst> <t_from> <t_to> [step_s]
시각은 그 rlog의 첫 carState를 0으로 한 초. state/latActive/accel은 직전 메시지 값."""
import sys
from load import events
path, t0_, t1_ = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
step = float(sys.argv[4]) if len(sys.argv) > 4 else 0.25
base = None; state = '-'; lat = None; acc = 0.0; nxt = t0_
for e in events(path):
    w = e.which()
    if w == 'selfdriveState': state = str(e.selfdriveState.state)
    elif w == 'carControl':
        lat = e.carControl.latActive; acc = e.carControl.actuators.accel
    elif w == 'carState':
        if base is None: base = e.logMonoTime
        t = (e.logMonoTime - base) / 1e9
        if t > t1_: break
        if t >= nxt:
            c = e.carState
            print("t=%6.2f v=%5.1f ang=%+6.1f trq=%+6.0f pressed=%-5s L=%d R=%d gas=%d brk=%d state=%s lat=%s accel=%+.2f" % (
                t, c.vEgo, c.steeringAngleDeg, c.steeringTorque, c.steeringPressed, c.leftBlinker, c.rightBlinker, c.gasPressed, c.brakePressed, state, lat, acc))
            nxt = t + step
