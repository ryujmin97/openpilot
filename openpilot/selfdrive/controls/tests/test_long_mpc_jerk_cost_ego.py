import json
import re
from pathlib import Path

import pytest

from openpilot.selfdrive.carrot.carrot_functions import jerk_cost_ego_from_param
from openpilot.selfdrive.controls.lib.longitudinal_mpc_lib.long_mpc import J_EGO_COST, LongitudinalMpc

OPENPILOT = Path(__file__).resolve().parents[3]
SETTINGS = json.loads((OPENPILOT / "selfdrive" / "carrot_settings.json").read_text(encoding="utf-8"))
PARAMS_KEYS = (OPENPILOT / "common" / "params_keys.h").read_text(encoding="utf-8")
CARROT_FUNCTIONS = (OPENPILOT / "selfdrive" / "carrot" / "carrot_functions.py").read_text(encoding="utf-8")


class _FakeMpc:
  def __init__(self, mode='acc'):
    self.mode = mode
    self.cost_weights = None

  def set_cost_weights(self, cost_weights, constraint_cost_weights):
    self.cost_weights = list(cost_weights)


def _jerk_weight(mode='acc', **kwargs):
  fake = _FakeMpc(mode)
  LongitudinalMpc.set_weights(fake, True, **kwargs)
  return fake.cost_weights[-1]


def _setting():
  return next(p for p in SETTINGS["params"] if p["name"] == "JerkCostEgo")


def test_default_matches_everywhere():
  assert re.search(r'\{"JerkCostEgo", \{PERSISTENT, INT, "12"\}\}', PARAMS_KEYS)
  assert _setting()["default"] == 12
  assert float(J_EGO_COST) == 12.0
  assert re.search(r'self\.jerkCostEgo = 12\.0\b', CARROT_FUNCTIONS)


def test_setting_range_and_menu_placement():
  setting = _setting()
  assert (setting["min"], setting["max"], setting["unit"]) == (5, 20, 1)
  assert setting.get("risk") == "medium"
  driving = next(category for category in SETTINGS["menu"] if category["id"] == "DRIVING")
  cruise = next(group for group in driving["groups"] if group["id"] == "CRUISE")
  longtune = next(group for group in cruise["groups"] if group["id"] == "CRUISE_LONGTUNE")
  assert "JerkCostEgo" in longtune["params"]


def test_without_argument_the_jerk_weight_is_unchanged():
  assert _jerk_weight(jerk_factor=0.7) == pytest.approx(0.7 * J_EGO_COST)


@pytest.mark.parametrize("value", (5, 8, 12, 16, 20))
def test_jerk_weight_scales_with_the_setting(value):
  assert _jerk_weight(jerk_factor=0.7, j_ego_cost=value) == pytest.approx(0.7 * value)
  assert _jerk_weight(jerk_factor=1.0, jerk_cost_factor=0.5, j_ego_cost=value) == pytest.approx(0.5 * value)


@pytest.mark.parametrize("value,expected", ((-3, 5.0), (0, 5.0), (4.9, 5.0), (20.1, 20.0), (99, 20.0)))
def test_out_of_range_values_are_clipped(value, expected):
  assert _jerk_weight(jerk_factor=1.0, j_ego_cost=value) == pytest.approx(expected)


def test_blended_mode_ignores_the_setting():
  assert _jerk_weight('blended', j_ego_cost=20) == _jerk_weight('blended', j_ego_cost=5) == 1.0


@pytest.mark.parametrize("stored,expected", ((0, 12.0), (-1, 12.0), (3, 5.0), (5, 5.0), (7, 7.0), (20, 20.0), (25, 20.0)))
def test_stored_value_is_read_with_default_for_unset_and_clip(stored, expected):
  assert jerk_cost_ego_from_param(stored) == expected
