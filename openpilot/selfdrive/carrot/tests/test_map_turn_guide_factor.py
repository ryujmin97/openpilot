"""분기·톨게이트 안내 지점 route 반영비율(carrot_serv.map_turn_speed_factor) 단위 테스트.

carrot_serv 전체를 import하지 않고(cereal/capnp 불필요) ast로 상수와 함수만 실행한다.
"""

import ast
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "carrot_serv.py"
CONSTS = {"MAP_TURN_GUIDE_TURN_INFOS", "MAP_TURN_GUIDE_FACTOR", "MAP_TURN_GUIDE_NEAR_M", "MAP_TURN_GUIDE_FAR_M"}


def _load():
  tree = ast.parse(SRC.read_text(encoding="utf-8"))
  nodes = [n for n in tree.body if isinstance(n, ast.Assign)
           and any(isinstance(t, ast.Name) and t.id in CONSTS for t in n.targets)]
  nodes += [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "map_turn_speed_factor"]
  assert len(nodes) == len(CONSTS) + 1
  ns = {}
  exec(compile(ast.Module(body=nodes, type_ignores=[]), str(SRC), "exec"), ns)
  return ns


NS = _load()
F = NS["map_turn_speed_factor"]
GUIDE = NS["MAP_TURN_GUIDE_FACTOR"]
NEAR = NS["MAP_TURN_GUIDE_NEAR_M"]
FAR = NS["MAP_TURN_GUIDE_FAR_M"]
BASE = 1.35


@pytest.mark.parametrize("info", [-1, None, 0, 1, 2, 5, 7])
def test_other_guidance_keeps_base(info):
  for dist in (-20, 0, NEAR - 1, (NEAR + FAR) / 2, FAR + 1):
    assert F(BASE, info, dist) == BASE


@pytest.mark.parametrize("info", [3, 4, 6])
def test_fork_and_toll_lower_factor_near_the_point(info):
  assert F(BASE, info, FAR) == BASE
  assert F(BASE, info, FAR + 500) == BASE
  assert F(BASE, info, NEAR) == GUIDE
  assert F(BASE, info, 50) == GUIDE
  assert F(BASE, info, -30) == GUIDE  # 안내 지점 통과 직후(xDistToTurn -50까지 유지)에도 낮은 배율 유지


def test_linear_ramp_is_continuous_and_monotonic():
  mid = (NEAR + FAR) / 2
  assert F(BASE, 4, mid) == pytest.approx((BASE + GUIDE) / 2)
  prev = F(BASE, 4, NEAR)
  for dist in range(int(NEAR), int(FAR) + 1, 5):
    cur = F(BASE, 4, dist)
    assert GUIDE - 1e-9 <= cur <= BASE + 1e-9
    assert cur >= prev - 1e-9  # 멀어질수록 배율이 커진다(가까울수록 작아진다)
    prev = cur


@pytest.mark.parametrize("base", [0.5, 0.9, GUIDE])
def test_never_raises_factor_above_base(base):
  for dist in (-10, NEAR, (NEAR + FAR) / 2, FAR, FAR + 100):
    assert F(base, 6, dist) <= base + 1e-12
    assert F(base, 6, dist) == pytest.approx(base)  # base <= GUIDE이면 항상 base


def test_route_speed_uses_helper_with_navi_state():
  """update_navi()가 이 함수를 xTurnInfo/xDistToTurn과 함께 호출하는지 확인(배선 검증)."""
  src = SRC.read_text(encoding="utf-8")
  assert src.count("map_turn_speed_factor(self.mapTurnSpeedFactor, self.xTurnInfo, self.xDistToTurn)") == 1
  assert "route_speed = max(route_speed * route_factor, self.autoCurveSpeedLowerLimit)" in src
  # 주석 처리된 옛 줄(#speed_n_sources...)을 제외하고 배율 직접 곱셈이 남지 않았는지
  live = [ln for ln in src.splitlines() if "route_speed * self.mapTurnSpeedFactor" in ln and not ln.lstrip().startswith("#")]
  assert live == []
