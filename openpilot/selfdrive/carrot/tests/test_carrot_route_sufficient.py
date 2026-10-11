import math
from types import SimpleNamespace

import pytest

from openpilot.selfdrive.carrot import carrot_man
from openpilot.selfdrive.carrot.carrot_man import (
  CarrotMan,
  ROUTE_FREEZE_MAX_CYCLES,
  ROUTE_LOOKAHEAD_M,
  ROUTE_LOOKAHEAD_OFF_RAMP_M,
  ROUTE_PATH_COVER_MARGIN_M,
  haversine,
  route_path_covers_lookahead,
)

# 핵심 발견 73(267차): route 충분 판정을 원본 점 개수에서 경로가 덮는 길이로 바꾸고,
# freeze가 만료되면 낡은 navi_route_speed_filt를 지운다.

LON = 127.0
LAT0 = 37.0
M_PER_DEG_LAT = math.radians(1.0) * 6371000  # haversine과 같은 지구 반경


def _north(meters, lat0=LAT0):
  return (LON, lat0 + meters / M_PER_DEG_LAT)


def _path(*distances_m):
  return [_north(d) for d in distances_m]


def test_path_length_helper_matches_haversine_scale():
  p = _path(0, 300)
  assert haversine(p[0][0], p[0][1], p[1][0], p[1][1]) == pytest.approx(300.0, abs=0.01)


def test_two_point_path_covering_lookahead_is_sufficient():
  # 직선 고속도로에서 꼭짓점이 300 m보다 멀면 창 안 점이 2개뿐이다(예전 판정은 4개 미만이라 부족).
  assert route_path_covers_lookahead(_path(0, 300), ROUTE_LOOKAHEAD_M)
  assert route_path_covers_lookahead(_path(0, 150, 300), ROUTE_LOOKAHEAD_M)


def test_short_or_degenerate_path_is_insufficient():
  assert not route_path_covers_lookahead([], ROUTE_LOOKAHEAD_M)
  assert not route_path_covers_lookahead(_path(0), ROUTE_LOOKAHEAD_M)
  assert not route_path_covers_lookahead(_path(0, 100), ROUTE_LOOKAHEAD_M)
  assert not route_path_covers_lookahead(_path(0, 100, 200, 290), ROUTE_LOOKAHEAD_M)


def test_margin_boundary():
  edge = ROUTE_LOOKAHEAD_M - ROUTE_PATH_COVER_MARGIN_M
  assert route_path_covers_lookahead(_path(0, edge + 0.5), ROUTE_LOOKAHEAD_M)
  assert not route_path_covers_lookahead(_path(0, edge - 0.5), ROUTE_LOOKAHEAD_M)


def test_off_ramp_lookahead_needs_longer_cover():
  assert not route_path_covers_lookahead(_path(0, 300), ROUTE_LOOKAHEAD_OFF_RAMP_M)
  assert route_path_covers_lookahead(_path(0, 300, 600), ROUTE_LOOKAHEAD_OFF_RAMP_M)


needs_shapely = pytest.mark.skipif(not carrot_man.SHAPELY_AVAILABLE, reason="shapely 없음")


class _Params:
  def get_bool(self, key):
    assert key == "IsOnroad"
    return True


def _polyline(spacing_m=437.0, count=24):
  return [_north(i * spacing_m) for i in range(count)]


def _man(polyline, v_cruise=120.0, v_ego=27.3):
  man = CarrotMan.__new__(CarrotMan)
  man.params = _Params()
  man.navi_points = polyline
  man.navi_points_start_index = 0
  man.navi_points_active = True
  man.navd_active = True
  man.navi_route_speed_filt = None
  man.route_insufficient_cycles = 0
  man.route_lookahead_hold = carrot_man.RouteLookaheadHold()
  man.active_carrot_last = 2
  man.carrot_serv = SimpleNamespace(
    active_carrot=2,
    vpPosPointLon=LON,
    vpPosPointLat=LAT0,
    bearing=0.0,
    nRoadLimitSpeed=100,
    autoNaviSpeedDecelRate=1.5,
    autoNaviSpeedCtrlEnd=7.0,
    navType=None,
    xTurnInfo=-1,
    xDistToTurn=0,
  )
  man.sm = {"carState": SimpleNamespace(vEgo=v_ego, vCruise=v_cruise)}
  return man


def _place(man, meters_along):
  lon, lat = _north(meters_along)
  man.carrot_serv.vpPosPointLon = lon
  man.carrot_serv.vpPosPointLat = lat
  man.navi_points_start_index = 0


@needs_shapely
def test_sparse_straight_highway_is_sufficient_and_not_frozen():
  man = _man(_polyline())
  man.navi_route_speed_filt = 60.5
  # 꼭짓점 사이 어느 위치든 300 m 창은 경로 안에 있고, 점은 2~3개뿐이다.
  for meters in (10.0, 150.0, 400.0, 1000.0, 3000.0):
    _place(man, meters)
    man.route_insufficient_cycles = 7
    man.navi_route_speed_filt = None
    _, _, out_speed = man.carrot_navi_route()
    assert man.route_insufficient_cycles == 0
    assert man.navi_route_speed_filt == out_speed
    assert out_speed >= 100


@needs_shapely
def test_route_end_keeps_filt_until_freeze_expires():
  man = _man(_polyline())
  end = 23 * 437.0
  _place(man, end - 100.0)  # 남은 경로 100 m: 전방 300 m를 못 덮는다
  man.navi_route_speed_filt = 60.5
  _, _, out_speed = man.carrot_navi_route()
  assert man.route_insufficient_cycles == 1
  assert out_speed == 60.5
  assert man.navi_route_speed_filt == 60.5


@needs_shapely
def test_expired_freeze_clears_stale_filt_and_next_sufficient_cycle_is_not_slewed():
  man = _man(_polyline())
  end = 23 * 437.0
  _place(man, end - 100.0)
  man.navi_route_speed_filt = 60.5
  man.route_insufficient_cycles = ROUTE_FREEZE_MAX_CYCLES  # 다음 사이클에 만료
  _, _, out_speed = man.carrot_navi_route()
  assert out_speed == 120.0  # 만료되면 vCruise로 대체
  assert man.navi_route_speed_filt is None

  # 점이 다시 충분해지면 낡은 값(60.5) 기준 +1 km/h 슬루 없이 원시 값이 그대로 나온다.
  _place(man, 1000.0)
  _, _, out_speed = man.carrot_navi_route()
  assert man.route_insufficient_cycles == 0
  assert out_speed >= 100
  assert out_speed > 60.5 + 1.0
  assert man.navi_route_speed_filt == out_speed


@needs_shapely
def test_no_filt_falls_back_to_vcruise_while_insufficient():
  man = _man(_polyline())
  _place(man, 23 * 437.0 - 100.0)
  _, _, out_speed = man.carrot_navi_route()
  assert out_speed == 120.0
  assert man.navi_route_speed_filt is None
