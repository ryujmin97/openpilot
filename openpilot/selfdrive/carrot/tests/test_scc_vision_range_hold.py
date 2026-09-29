"""A continuously tracked moving SCC lead survives noisy vision range."""

from types import SimpleNamespace

import pytest

from openpilot.selfdrive.carrot.radar_motion import controller as ctl


def _match(d_rel=62.0, v_lead=31.0, source="scc", track_id=0, d_path=0.2):
  point = SimpleNamespace(
    source=source, track_id=track_id, d_rel=d_rel, y_rel=0.0, v_rel=0.0,
    yv_rel=0.0, v_lead=v_lead, measured=True,
  )
  return SimpleNamespace(point=point, d_path=d_path)


def _vision(d_rel, x_std=7.0, velocity=20.0):
  return SimpleNamespace(
    d_rel=d_rel, y_rel=0.0, probability=0.97, velocity=velocity, x_std=x_std,
  )


@pytest.fixture
def controller(monkeypatch):
  monkeypatch.setattr(ctl, "_central_vision_fallback_allowed", lambda vision, path: True)
  return ctl.DPathRadarController(enable_radar_tracks=0)


def _decide(controller, match, vision, t):
  return controller._reject_farther_radar_match(match, vision, (), t)


def _warm(controller, n=3, t0=100.0, **kw):
  # Continuously accepted frames (vision agrees) establish the track.
  for i in range(n):
    assert _decide(controller, _match(**kw), _vision(60.0), t0 + i * 0.05) is False
  return t0 + n * 0.05


def test_scc_mismatch_beyond_old_limit_is_kept_when_tracked(controller):
  t = _warm(controller)
  # 62 m radar vs 53 m vision: 9 m > 8 m old limit, inside 2.5 sigma of xStd 7.
  assert _decide(controller, _match(), _vision(53.0), t) is False


def test_scc_mismatch_beyond_xstd_allowance_is_rejected(controller):
  t = _warm(controller)
  assert _decide(controller, _match(d_rel=75.0), _vision(53.0, x_std=3.0), t) is True


def test_scc_first_frame_without_history_is_rejected(controller):
  assert _decide(controller, _match(), _vision(53.0), 100.0) is True


def test_scc_new_track_id_is_rejected(controller):
  t = _warm(controller)
  assert _decide(controller, _match(track_id=1), _vision(53.0), t) is True


def test_scc_position_jump_is_rejected(controller):
  t = _warm(controller)
  assert _decide(controller, _match(d_rel=68.0), _vision(53.0), t) is True


def test_scc_time_gap_is_rejected(controller):
  t = _warm(controller)
  assert _decide(controller, _match(), _vision(53.0), t + 0.5) is True


def test_stopped_scc_lead_is_not_relaxed(controller):
  t = _warm(controller, v_lead=0.5)
  assert _decide(controller, _match(v_lead=0.5), _vision(53.0), t) is True


def test_gross_mismatch_is_rejected(controller):
  t = _warm(controller)
  assert _decide(controller, _match(d_rel=75.0), _vision(45.0, x_std=7.0), t) is True
