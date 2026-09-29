from openpilot.selfdrive.carrot.carrot_man import (
  ROUTE_LOOKAHEAD_M,
  ROUTE_LOOKAHEAD_OFF_RAMP_M,
  ROUTE_OFF_RAMP_TRIGGER_DIST_M,
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
