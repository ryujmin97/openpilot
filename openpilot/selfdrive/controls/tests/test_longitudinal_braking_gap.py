from copy import copy

import numpy as np
import pytest

from openpilot.selfdrive.controls.lib.longitudinal_braking_gap import BrakingGapState, braking_gap_reference, floor_ceiling


def update(state, **kwargs):
  args = {'enabled': True, 'track_id': 43, 'dt': .05, 'distance': 20., 'ego_speed': 15., 'ego_accel': -.5,
              'lead_speed': 14.5, 'lead_accel': -.5, 'relative_speed': -.5, 'base_tf': .6, 'stop_distance': 5., 'desired_distance': 17.}
  args.update(kwargs)
  return state.update(**args)


def test_distance_memory_survives_falling_speed_without_accumulating_each_frame():
  state = BrakingGapState()
  for _ in range(20):
    update(state)
  captured = state.floor
  for i in range(150):
    update(state, ego_speed=max(2., 15. - i * .08), lead_speed=max(1.5, 14.5 - i * .08), desired_distance=10.)
  assert 10. < state.floor < captured <= 20.
  assert 0. < state.margin < 10.


@pytest.mark.parametrize('change', [{'enabled': False}, {'track_id': 44}, {'distance': 100.}, {'lead_accel': float('nan')}])
def test_lost_replaced_or_jumped_track_cannot_inherit_distance_memory(change):
  state = BrakingGapState()
  for _ in range(20):
    update(state)
  assert state.margin > 0.
  assert update(state, **change) == 0.
  assert state.floor is None


def test_opening_and_constant_speed_do_not_create_braking_memory():
  for change in [{'relative_speed': .5}, {'ego_accel': 0.}, {'lead_accel': 0.}]:
    state = BrakingGapState()
    for _ in range(40):
      assert update(state, **change) == 0.


def test_prediction_does_not_mutate_live_state_and_matches_repeated_advances():
  state = BrakingGapState()
  for _ in range(30):
    update(state)
  before = vars(state).copy()
  t = np.arange(21) * .05
  actual = state.margins(t, np.full(21, 10.), np.full(21, 9.5), np.full(21, 10.), .6, 5.)
  assert vars(state) == before
  expected = [state.margin]
  for _ in range(20):
    state._advance(.05, 11., 10., 10., 9.5)
    expected.append(state.margin)
  np.testing.assert_allclose(actual, expected)


def relief(state, **changes):
  args = {'dt': .05, 'enabled': True, 'base_tf': 1.1, 'ego_speeds': np.full(13, 20.), 'lead_speeds': np.full(13, 19.),
              'lead_accel': -1., 'physical_gaps': np.full(13, 40.), 'danger_margins': np.full(13, 10.),
              'times': np.linspace(0, 10, 13), 'stop_distance': 5.}
  args.update(changes)
  return state.comfort_relief(**args)


def test_comfort_allowance_is_bounded_and_danger_withdraws_it_immediately():
  state = BrakingGapState()
  state.age, state.distance, state.relative_speed = 2., 40., -1.
  for _ in range(20):
    result = relief(state)
  np.testing.assert_allclose(result, 8.)
  assert not relief(state, danger_margins=np.full(13, -1.)).any()
  assert state.relief == 0.


@pytest.mark.parametrize('change', [{'base_tf': .45}, {'enabled': False}, {'lead_speeds': np.zeros(13)},
                                    {'physical_gaps': np.full(13, 10.)}, {'lead_accel': 0.}])
def test_short_gap_stopped_lead_and_invalid_eligibility_never_get_relief(change):
  state = BrakingGapState()
  state.age, state.distance, state.relative_speed = 2., 40., -1.
  assert not relief(state, **change).any()


def test_slack_does_not_move_physical_obstacles_or_relax_another_obstacle():
  obstacles = np.array([[50., 30., 100.], [20., 30., 19.]])
  original = obstacles.copy()
  result = braking_gap_reference(obstacles, np.array([[-5., 0.], [-5., -5.]]), np.array([20., 20.]))
  np.testing.assert_array_equal(obstacles, original)
  np.testing.assert_array_equal(result, 0.)


def test_stopped_pair_retains_distance_until_departure():
  state = BrakingGapState()
  for _ in range(20):
    update(state)
  captured = state.floor
  for _ in range(600):
    update(state, distance=20., ego_speed=0., ego_accel=0., lead_speed=0., lead_accel=0.,
           relative_speed=0., desired_distance=5.)
  assert state.floor == captured
  held = state.margin
  for _ in range(400):
    update(state, distance=20., ego_speed=0., ego_accel=0., lead_speed=1., lead_accel=.5,
           relative_speed=1., desired_distance=5.)
  assert state.margin < held * .02


@pytest.mark.parametrize('field', ['danger_margins', 'physical_gaps', 'ego_speeds'])
def test_nonfinite_prediction_withdraws_comfort_relief(field):
  state = BrakingGapState()
  state.age, state.distance, state.relative_speed = 2., 40., -1.
  relief(state)
  assert state.relief > 0.
  assert not relief(state, **{field: np.full(13, np.nan)}).any()


def test_capture_uses_the_same_ceiling_as_later_advances():
  state = BrakingGapState()
  for _ in range(20):
    update(state, distance=100., desired_distance=17.)
    if state.floor is not None:
      break
  assert state.floor == pytest.approx(floor_ceiling(5. + 15. * .6, 5., 15.), abs=.2)


def stop_approach(state, final_distance):
  # A far lead stopping at a signal: captured near cruise speed, then the ego slows faster than the 8 s relaxation.
  for _ in range(20):
    update(state, distance=100., desired_distance=17.)
  for i in range(400):
    speed = max(.31, 15. - i * .05)
    update(state, distance=100. - i * (100. - final_distance) / 400., ego_speed=speed,
           lead_speed=max(0., 14.5 - i * .1), lead_accel=-.5, desired_distance=5. + .6 * speed)
    yield speed


def test_distance_memory_cannot_outlive_the_speed_it_was_captured_at():
  state = BrakingGapState()
  for speed in stop_approach(state, 9.):
    assert state.floor <= floor_ceiling(5. + speed * .6, 5., speed) + 1e-9
  assert state.floor <= 5. + 2.5 * .31 + 1e-9
  assert state.margin < 1.


def test_prediction_applies_the_same_ceiling():
  state = BrakingGapState()
  for _ in range(20):
    update(state, distance=100., desired_distance=17.)
  times = np.linspace(0., 10., 21)
  speeds = np.linspace(15., .5, 21)
  lead = np.maximum(speeds - .5, 0.)
  desired = 5. + .6 * speeds
  predicted = state.margins(times, speeds, lead, desired, .6, 5.)
  unbounded = copy(state)
  for i in range(1, len(times)):
    unbounded._advance(times[i] - times[i - 1], 5. + speeds[i] * .6, desired[i], speeds[i], lead[i])
  assert predicted[-1] < unbounded.margin - 1.


def test_stopped_pair_still_holds_what_it_had_when_it_halted():
  state = BrakingGapState()
  for _ in stop_approach(state, 9.):
    pass
  halted = state.floor
  assert halted is not None
  for _ in range(600):
    update(state, distance=9., ego_speed=0., ego_accel=0., lead_speed=0., lead_accel=0., relative_speed=0.,
           desired_distance=5.)
  assert state.floor == halted
