"""앞차 속도 프로파일 생성. mk(v0, tf, events): events=[(t_start, a, v_target), ...] 앞차가 t_start부터 가속도 a로 v_target까지."""
def ramp_profile(v0, events):
  def f(t):
    v = v0
    for (ts, a, vt) in events:
      if t < ts:
        break
      dur = abs(vt - v) / abs(a) if a != 0 else 0
      te = ts + dur
      if t < te:
        return v + a * (t - ts), a, True
      v = vt
    return v, 0.0, True
  return f


def mk(v0, tf, events, appear=None, present_from=0.0, gap_extra=0.0):
  prof = ramp_profile(v0, events)
  def lead(t):
    vl, al, _ = prof(t)
    return vl, al, t >= present_from
  d = dict(v0=v0, gap0=6.0 + v0 * tf + gap_extra, lead=lead)
  if appear:
    d['appear'] = appear
  return d
