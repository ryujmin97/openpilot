import contextlib
import pytest
import itertools
from openpilot.common.parameterized import parameterized_class

from openpilot.cereal import log

from openpilot.selfdrive.controls.lib.longitudinal_mpc_lib.long_mpc import get_safe_obstacle_distance, get_stopped_equivalence_factor, get_T_FOLLOW
from openpilot.selfdrive.test.longitudinal_maneuvers import maneuver as maneuver_module
from openpilot.selfdrive.test.longitudinal_maneuvers.maneuver import Maneuver
from openpilot.selfdrive.test.longitudinal_maneuvers.plant import Plant


def desired_follow_distance(v_ego, v_lead, t_follow=None):
  if t_follow is None:
    t_follow = get_T_FOLLOW()
  return get_safe_obstacle_distance(v_ego, t_follow) - get_stopped_equivalence_factor(v_lead)

@contextlib.contextmanager
def record_planner_values(record):
  # Maneuver.evaluate()가 만드는 Plant가 마지막 스텝에서 실제로 쓴 값을 record에 남긴다.
  # (Plant는 evaluate() 안에서만 만들어져 밖으로 나오지 않으므로 maneuver.Plant를 잠시 교체)
  original_plant = maneuver_module.Plant

  class RecordingPlant(original_plant):
    def step(self, *args, **kwargs):
      out = super().step(*args, **kwargs)
      record.update(t_follow=self.planner.mpc.t_follow,
                    comfort_brake=self.carrot.comfort_brake,
                    stop_distance=self.carrot.stop_distance)
      return out

  maneuver_module.Plant = RecordingPlant
  try:
    yield
  finally:
    maneuver_module.Plant = original_plant

def run_following_distance_simulation(v_lead, t_end=100.0, e2e=False, personality=0, record=None):
  man = Maneuver(
    '',
    duration=t_end,
    initial_speed=float(v_lead),
    lead_relevancy=True,
    initial_distance_lead=100,
    speed_lead_values=[v_lead],
    breakpoints=[0.],
    e2e=e2e,
    personality=personality,
  )
  with record_planner_values({} if record is None else record):
    valid, output = man.evaluate()
  assert valid
  return output[-1,2] - output[-1,1]


@parameterized_class(("e2e", "personality", "speed"), itertools.product(
                      [True, False], # e2e
                      [log.LongitudinalPersonality.relaxed, # personality
                       log.LongitudinalPersonality.standard,
                       log.LongitudinalPersonality.aggressive],
                      [0,10,35])) # speed
class TestFollowingDistance:
  def test_following_distance(self):
    v_lead = float(self.speed)
    record = {}
    simulation_steady_state = run_following_distance_simulation(v_lead, e2e=self.e2e, personality=self.personality, record=record)
    # 기대값은 스톡 상수가 아니라 이 시뮬레이션에서 플래너(carrot)가 실제로 쓴 T/comfort_brake/stop_distance 기준.
    # 앞차 정지등가 항은 플래너와 동일하게 get_stopped_equivalence_factor(모듈 상수 COMFORT_BRAKE)를 쓴다.
    correct_steady_state = (get_safe_obstacle_distance(v_lead, record["t_follow"], record["comfort_brake"], record["stop_distance"])
                            - get_stopped_equivalence_factor(v_lead))
    err_ratio = 0.2 if self.e2e else 0.1
    abs_err_margin = 0.5 if v_lead > 0.0 else 1.15
    assert simulation_steady_state == pytest.approx(correct_steady_state, abs=err_ratio * correct_steady_state + abs_err_margin)
