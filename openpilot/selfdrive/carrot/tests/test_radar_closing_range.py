"""Qualified slower front-radar match (8212379): bounded exception, nearer regular match keeps priority."""
import pytest

from openpilot.selfdrive.carrot.radar_motion.controller import DPathRadarController
from openpilot.selfdrive.carrot.tests.test_radar_motion_predictor import Point, model_with_lead


@pytest.mark.parametrize('change', ['nominal', 'tentative', 'lateral', 'turn', 'range_jump', 'braking_vision', 'fast_radar', 'brief'])
def test_farther_slow_front_requires_continuous_motion_and_more_restrictive_kinematics(change):
  controller = DPathRadarController(enable_radar_tracks=1)
  qualified = False
  for i in range(12 if change != 'brief' else 4):
    t = i * .05
    d = 100. - 10. * t
    point = Point(46, d + (4. if change == 'range_jump' and i % 2 else 0.),
                  2. if change == 'lateral' else 0., v_rel=2. if change == 'fast_radar' else -10.,
                  trackState=1 if change == 'tentative' else 2)
    model = model_with_lead(d - 20., 0., 22., probability=.95)
    model.leadsV3[0].xStd = (12.,)
    if change == 'braking_vision':
      model.leadsV3[0].a = (-2.,)
    out = controller.update(t, 20., [point], model, yaw_rate_rad_s=.06 if change == 'turn' else 0.)
    qualified |= controller.primary_matcher.closing_range_match is not None
    if change == 'nominal' and i >= 6:
      assert out.lead_one['radarTrackId'] == 46
      assert out.lead_one['dRel'] == pytest.approx(d)
  assert qualified == (change == 'nominal')


def test_closing_range_exception_preserves_nearer_regular_match_and_expires_with_evidence():
  controller = DPathRadarController(enable_radar_tracks=1)
  for i in range(12):
    t = i * .05
    d = 100. - 10. * t
    model = model_with_lead(d - 20., 0., 22., probability=.95)
    model.leadsV3[0].xStd = (12.,)
    points = [Point(46, d, 0., v_rel=-10., trackState=2), Point(9, d - 20., 0., v_rel=2., trackState=2)]
    out = controller.update(t, 20., points, model)
    assert out.lead_one['radarTrackId'] == 9
  assert controller.primary_matcher.closing_range_match is not None
  model.leadsV3[0].a = (-2.,)
  controller.update(.6, 20., points, model)
  assert controller.primary_matcher.closing_range_match is None
