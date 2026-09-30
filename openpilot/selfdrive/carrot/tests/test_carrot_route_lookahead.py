from openpilot.selfdrive.carrot.carrot_man import (
  ROUTE_LOOKAHEAD_M,
  ROUTE_LOOKAHEAD_OFF_RAMP_M,
  ROUTE_LOOKAHEAD_HOLD_M,
  ROUTE_OFF_RAMP_TRIGGER_DIST_M,
  RouteLookaheadHold,
  route_lookahead_distance,
)


def test_off_ramp_guidance_uses_600m_lookahead():
  assert route_lookahead_distance("off ramp", 3, 500) == 600
  assert route_lookahead_distance("off ramp", 4, ROUTE_OFF_RAMP_TRIGGER_DIST_M) == ROUTE_LOOKAHEAD_OFF_RAMP_M


def test_other_guidance_keeps_300m_lookahead():
  assert route_lookahead_distance("off ramp", 4, ROUTE_OFF_RAMP_TRIGGER_DIST_M + 1) == ROUTE_LOOKAHEAD_M
  assert route_lookahead_distance("fork", 3, 200) == 300
  assert route_lookahead_distance("turn", 1, 100) == 300
  assert route_lookahead_distance("invalid", -1, 0) == 300
  assert route_lookahead_distance(None, -1, 0) == 300


def _drive(hold, base_m, v_ego, seconds, t0, dt=0.05):
  out = []
  t = t0
  for _ in range(int(round(seconds / dt))):
    t += dt
    out.append(hold.update(base_m, v_ego, t))
  return out, t


def test_hold_keeps_600m_for_300m_after_guidance_then_returns():
  hold = RouteLookaheadHold()
  out, t = _drive(hold, ROUTE_LOOKAHEAD_OFF_RAMP_M, 25.0, 2.0, 0.0)
  assert set(out) == {ROUTE_LOOKAHEAD_OFF_RAMP_M}
  # 25 m/s로 250 m 주행: 아직 유지(300 m 미만)
  out, t = _drive(hold, ROUTE_LOOKAHEAD_M, 25.0, 10.0, t)
  assert set(out) == {ROUTE_LOOKAHEAD_OFF_RAMP_M}
  # 300 m를 넘기면(추가 3 s) 300 m 복귀
  out, t = _drive(hold, ROUTE_LOOKAHEAD_M, 25.0, 3.0, t)
  assert out[-1] == ROUTE_LOOKAHEAD_M
  assert ROUTE_LOOKAHEAD_HOLD_M == 300


def test_hold_never_starts_without_off_ramp_and_reset_clears_it():
  hold = RouteLookaheadHold()
  out, t = _drive(hold, ROUTE_LOOKAHEAD_M, 25.0, 1.0, 0.0)
  assert set(out) == {ROUTE_LOOKAHEAD_M}
  _drive(hold, ROUTE_LOOKAHEAD_OFF_RAMP_M, 25.0, 0.5, t)
  hold.reset()
  out, _ = _drive(hold, ROUTE_LOOKAHEAD_M, 25.0, 0.5, 100.0)
  assert set(out) == {ROUTE_LOOKAHEAD_M}


def test_hold_does_not_shrink_while_stopped_and_ignores_time_jump():
  hold = RouteLookaheadHold()
  _drive(hold, ROUTE_LOOKAHEAD_OFF_RAMP_M, 25.0, 0.5, 0.0)
  out, t = _drive(hold, ROUTE_LOOKAHEAD_M, 0.0, 30.0, 1.0)
  assert set(out) == {ROUTE_LOOKAHEAD_OFF_RAMP_M}
  # 5초 공백이 있어도 한 번에 0.2초까지만 반영
  assert hold.update(ROUTE_LOOKAHEAD_M, 25.0, t + 5.0) == ROUTE_LOOKAHEAD_OFF_RAMP_M
