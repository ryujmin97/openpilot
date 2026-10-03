import ast
import importlib.util
import sys
import time as stdlib_time
import types
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace

import pytest


HUD_RENDERER_PATH = Path(__file__).parents[1] / "onroad" / "hud_renderer.py"


@pytest.fixture
def hud_module(monkeypatch):
  @dataclass(frozen=True)
  class Color:
    r: int
    g: int
    b: int
    a: int

  @dataclass
  class Rectangle:
    x: float
    y: float
    width: float
    height: float

  @dataclass
  class Vector2:
    x: float
    y: float

  raylib = types.ModuleType("pyray")
  raylib.Color = Color
  raylib.Rectangle = Rectangle
  raylib.Vector2 = Vector2
  raylib.WHITE = Color(255, 255, 255, 255)
  raylib.BLACK = Color(0, 0, 0, 255)
  raylib.BLANK = Color(0, 0, 0, 0)
  raylib.GREEN = Color(0, 255, 0, 255)
  raylib.YELLOW = Color(255, 255, 0, 255)
  for name in (
    "draw_line_ex",
    "draw_rectangle_gradient_v",
    "draw_rectangle_rounded",
    "draw_rectangle_rounded_lines_ex",
    "draw_text_ex",
    "draw_texture_pro",
  ):
    setattr(raylib, name, lambda *args, **kwargs: None)

  class FakeExpButton:
    def __init__(self, *args):
      self.is_pressed = False

    def render(self, rect):
      pass

  class FakeRecordButton(FakeExpButton):
    def set_blink_phase(self, phase):
      pass

  class Widget:
    def __init__(self):
      pass

  fake_ui_state = SimpleNamespace(
    params=None,
    sm=None,
    started_frame=0,
    status=0,
    is_metric=True,
    usbgpu_present=False,
    usbgpu_compiled=False,
    usbgpu_compile_pending=False,
    usbgpu_loading=False,
    usbgpu_active=False,
    usbgpu_startup_failed=False,
  )
  gui_app = SimpleNamespace(
    font=lambda weight: ("font", weight),
    texture=lambda path: ("texture", path),
  )

  stubs = {
    "pyray": raylib,
    "openpilot.common.constants": SimpleNamespace(
      CV=SimpleNamespace(MS_TO_KPH=3.6, MS_TO_MPH=2.2369362920544),
    ),
    "openpilot.selfdrive.ui.onroad.exp_button": SimpleNamespace(ExpButton=FakeExpButton),
    # screenshot_button -> screenshot_capture.py evaluates `rl.Image` at import time, which this fake pyray lacks.
    "openpilot.selfdrive.ui.onroad.screenshot_button": SimpleNamespace(ScreenshotButton=FakeExpButton),
    "openpilot.selfdrive.ui.onroad.record_button": SimpleNamespace(RecordButton=FakeRecordButton),
    "openpilot.system.hardware.usbgpu": SimpleNamespace(
      usbgpu_badge_state=lambda compiled, loading, active, failed, compile_pending=False: (
        "error" if failed else "loading" if loading else "compile_pending" if compile_pending
        else "active" if active else "ready" if compiled else "not_compiled"
      ),
    ),
    "openpilot.selfdrive.ui.ui_state": SimpleNamespace(
      ui_state=fake_ui_state,
      UIStatus=SimpleNamespace(ENGAGED=1, DISENGAGED=2, OVERRIDE=3),
    ),
    "openpilot.system.ui.lib.application": SimpleNamespace(
      gui_app=gui_app,
      FontWeight=SimpleNamespace(SEMI_BOLD=1, BOLD=2, MEDIUM=3, DISPLAY=4),
    ),
    "openpilot.system.ui.lib.multilang": SimpleNamespace(tr=lambda text: text),
    "openpilot.system.ui.lib.text_measure": SimpleNamespace(
      measure_text_cached=lambda font, text, size: Vector2(len(text) * size, size),
    ),
    "openpilot.system.ui.lib.text_draw": SimpleNamespace(draw_text_ui_style=lambda *args, **kwargs: None),
    "openpilot.system.ui.widgets": SimpleNamespace(Widget=Widget),
  }
  for name, stub in stubs.items():
    monkeypatch.setitem(sys.modules, name, stub)

  module_name = f"_test_carrot_hud_renderer_{id(fake_ui_state)}"
  spec = importlib.util.spec_from_file_location(module_name, HUD_RENDERER_PATH)
  assert spec is not None and spec.loader is not None
  module = importlib.util.module_from_spec(spec)
  monkeypatch.setitem(sys.modules, module_name, module)
  spec.loader.exec_module(module)
  return module, fake_ui_state


class FakeParams:
  def __init__(self, values, failures=None):
    self.values = values
    self.failures = dict(failures or {})
    self.calls = []

  def get_int(self, key):
    self.calls.append(key)
    if self.failures.get(key, 0) > 0:
      self.failures[key] -= 1
      raise RuntimeError(f"failed to read {key}")
    return self.values[key]


def make_param_renderer(module, *, next_refresh=0.0):
  renderer = object.__new__(module.HudRenderer)
  renderer._hud_params_next_refresh_time = next_refresh
  renderer._show_device_state = 91
  renderer._show_date_time = 92
  renderer._show_tpms = 93
  renderer._show_plot_mode = 94
  renderer._longitudinal_personality = 95
  return renderer


def test_direct_hud_param_reads_are_isolated_to_refresh():
  tree = ast.parse(HUD_RENDERER_PATH.read_text(encoding="utf-8"))
  reads = []

  for function in (node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)):
    for call in (node for node in ast.walk(function) if isinstance(node, ast.Call)):
      func = call.func
      if (
        isinstance(func, ast.Attribute)
        and func.attr == "get_int"
        and isinstance(func.value, ast.Attribute)
        and func.value.attr == "params"
        and isinstance(func.value.value, ast.Name)
        and func.value.value.id == "ui_state"
      ):
        assert len(call.args) == 1 and isinstance(call.args[0], ast.Constant)
        reads.append((function.name, call.args[0].value))

  assert reads == [
    ("_refresh_hud_params", "ShowDeviceState"),
    ("_refresh_hud_params", "ShowDateTime"),
    ("_refresh_hud_params", "ShowTpms"),
    ("_refresh_hud_params", "ShowPlotMode"),
    ("_refresh_hud_params", "LongitudinalPersonality"),
  ]


def test_hud_renderer_has_no_subsection_profiling():
  tree = ast.parse(HUD_RENDERER_PATH.read_text(encoding="utf-8"))

  assert not any(
    isinstance(node, ast.ClassDef) and node.name == "HudRenderTimings"
    for node in ast.walk(tree)
  )
  assert not any(
    isinstance(node, ast.Call)
    and isinstance(node.func, ast.Attribute)
    and node.func.attr == "monotonic_ns"
    for node in ast.walk(tree)
  )


def test_initial_cruise_gap_preserves_legacy_fallback(hud_module):
  module, _ = hud_module

  renderer = module.HudRenderer()

  assert renderer._longitudinal_personality == 7
  assert renderer._get_cruise_gap() == 8


def test_hud_params_are_refreshed_once_per_interval(hud_module):
  module, fake_ui_state = hud_module
  params = FakeParams({
    "ShowDeviceState": 1,
    "ShowDateTime": 2,
    "ShowTpms": 3,
    "ShowPlotMode": 4,
    "LongitudinalPersonality": 4,
  })
  fake_ui_state.params = params
  renderer = make_param_renderer(module)

  renderer._refresh_hud_params(0.0)
  assert (
    renderer._show_device_state,
    renderer._show_date_time,
    renderer._show_tpms,
    renderer._show_plot_mode,
    renderer._longitudinal_personality,
  ) == (1, 2, 3, 4, 4)
  assert renderer._hud_params_next_refresh_time == 1.0
  assert params.calls == [
    "ShowDeviceState",
    "ShowDateTime",
    "ShowTpms",
    "ShowPlotMode",
    "LongitudinalPersonality",
  ]

  renderer._refresh_hud_params(0.999)
  assert len(params.calls) == 5

  renderer._refresh_hud_params(1.0)
  assert len(params.calls) == 10
  assert renderer._hud_params_next_refresh_time == 2.0


def test_show_param_failure_keeps_complete_snapshot_and_retries(hud_module):
  module, fake_ui_state = hud_module
  params = FakeParams({
    "ShowDeviceState": 1,
    "ShowDateTime": 2,
    "ShowTpms": 3,
    "ShowPlotMode": 4,
    "LongitudinalPersonality": 4,
  }, failures={"ShowDateTime": 1})
  fake_ui_state.params = params
  renderer = make_param_renderer(module)

  renderer._refresh_hud_params(0.0)

  assert (
    renderer._show_device_state,
    renderer._show_date_time,
    renderer._show_tpms,
    renderer._show_plot_mode,
    renderer._longitudinal_personality,
  ) == (91, 92, 93, 94, 95)
  assert renderer._hud_params_next_refresh_time == 0.0
  assert params.calls == ["ShowDeviceState", "ShowDateTime"]

  renderer._refresh_hud_params(0.1)
  assert (
    renderer._show_device_state,
    renderer._show_date_time,
    renderer._show_tpms,
    renderer._show_plot_mode,
    renderer._longitudinal_personality,
  ) == (1, 2, 3, 4, 4)
  assert renderer._hud_params_next_refresh_time == pytest.approx(1.1)


def test_personality_failure_uses_gap_eight_and_retries_next_frame(hud_module):
  module, fake_ui_state = hud_module
  params = FakeParams({
    "ShowDeviceState": 1,
    "ShowDateTime": 2,
    "ShowTpms": 3,
    "ShowPlotMode": 4,
    "LongitudinalPersonality": 4,
  }, failures={"LongitudinalPersonality": 1})
  fake_ui_state.params = params
  renderer = make_param_renderer(module)

  renderer._refresh_hud_params(0.0)

  assert (renderer._show_device_state, renderer._show_date_time, renderer._show_tpms, renderer._show_plot_mode) == (1, 2, 3, 4)
  assert renderer._get_cruise_gap() == 8
  assert renderer._hud_params_next_refresh_time == 0.0

  renderer._refresh_hud_params(0.1)
  assert renderer._get_cruise_gap() == 5
  assert renderer._hud_params_next_refresh_time == pytest.approx(1.1)
  assert params.calls.count("LongitudinalPersonality") == 2


def test_speed_limit_snapshot_reads_submaster_once(hud_module):
  module, fake_ui_state = hud_module
  carrot_man = SimpleNamespace(xSpdLimit="80", xSignType=2.0, nRoadLimitSpeed=90)

  class CountingSubMaster:
    def __init__(self):
      self.calls = 0

    def __getitem__(self, key):
      assert key == "carrotMan"
      self.calls += 1
      if self.calls > 1:
        raise AssertionError("carrotMan was read more than once")
      return carrot_man

  fake_ui_state.sm = CountingSubMaster()
  renderer = object.__new__(module.HudRenderer)

  assert renderer._get_speed_limit_info() == (80, 2, 90)
  assert fake_ui_state.sm.calls == 1


def test_speed_panel_reuses_one_snapshot(hud_module, monkeypatch):
  module, _ = hud_module
  renderer = object.__new__(module.HudRenderer)
  renderer._blink_timer = 15
  renderer._disp_timer = 63
  speed_limit_info = (80, 2, 90)
  snapshots = []
  calls = []

  monkeypatch.setattr(renderer, "_get_speed_limit_info", lambda: calls.append("snapshot") or speed_limit_info)
  monkeypatch.setattr(renderer, "_draw_carrot_main_background", lambda bx, by, info: (calls.append("background"), snapshots.append(info)))
  monkeypatch.setattr(renderer, "_draw_carrot_traffic_light", lambda bx, by: calls.append("traffic"))
  monkeypatch.setattr(renderer, "_draw_carrot_speed_panel", lambda bx, by: calls.append("speed"))
  monkeypatch.setattr(renderer, "_draw_carrot_lower_status", lambda bx, by: calls.append("status"))
  monkeypatch.setattr(renderer, "_draw_carrot_speed_limit_box", lambda bx, by, info: (calls.append("limit"), snapshots.append(info)))
  monkeypatch.setattr(renderer, "_draw_carrot_device_state", lambda bx, by: calls.append("device"))
  monkeypatch.setattr(renderer, "_draw_turn_info_hud", lambda rect: calls.append("navigation"))

  renderer._draw_set_speed_carrot(module.rl.Rectangle(10, 20, 1000, 600))

  assert calls == ["snapshot", "background", "traffic", "speed", "status", "limit", "device", "navigation"]
  assert snapshots[0] is speed_limit_info
  assert snapshots[1] is speed_limit_info
  assert renderer._blink_timer == 0
  assert renderer._disp_timer == 0


def test_device_info_updates_only_on_first_frame_or_new_service_frame(hud_module, monkeypatch):
  module, fake_ui_state = hud_module
  renderer = object.__new__(module.HudRenderer)
  renderer._device_info_loaded = False
  renderer._device_info_recv_frames = (-1, -1)
  renderer.is_cruise_set = True
  renderer.set_speed = 10
  renderer.speed = 20
  fake_ui_state.started_frame = 2
  fake_ui_state.sm = SimpleNamespace(
    recv_frame={"carState": 1, "deviceState": 10, "peripheralState": 20},
  )
  refreshes = []

  def update_device_info():
    refreshes.append(True)
    renderer._device_info_loaded = True

  monkeypatch.setattr(renderer, "_update_device_info", update_device_info)

  renderer._update_state()
  assert len(refreshes) == 1

  renderer._update_state()
  assert len(refreshes) == 1

  fake_ui_state.sm.recv_frame["deviceState"] = 11
  renderer._update_state()
  assert len(refreshes) == 2

  fake_ui_state.sm.recv_frame["peripheralState"] = 21
  renderer._update_state()
  assert len(refreshes) == 3


def test_device_display_cache_follows_service_receive_frames(hud_module):
  module, fake_ui_state = hud_module
  renderer = object.__new__(module.HudRenderer)
  renderer._device_info_loaded = False
  renderer._device_info_recv_frames = (-1, -1)
  renderer.is_cruise_set = True
  renderer.set_speed = 10
  renderer.speed = 20
  device_state = SimpleNamespace(
    freeSpacePercent=55.0,
    memoryUsagePercent=20,
    cpuTempC=[40.0, 42.0],
    cpuUsagePercent=[10.0, 20.0],
  )
  peripheral_state = SimpleNamespace(voltage=12_500)

  class FakeSubMaster(dict):
    pass

  sm = FakeSubMaster(deviceState=device_state, peripheralState=peripheral_state)
  sm.recv_frame = {"carState": 1, "deviceState": 10, "peripheralState": 20}
  fake_ui_state.started_frame = 2
  fake_ui_state.sm = sm

  renderer._update_state()
  assert renderer._device_info_recv_frames == (10, 20)
  assert (
    renderer._cpu_temp_text,
    renderer._memory_usage_text,
    renderer._disk_usage_text,
    renderer._voltage_text,
  ) == ("41°C", "20%", "45%", "12.5V")

  device_state.cpuTempC = [50.0]
  device_state.memoryUsagePercent = 30
  device_state.freeSpacePercent = 40.0
  peripheral_state.voltage = 13_250
  renderer._update_state()
  assert (
    renderer._cpu_temp_text,
    renderer._memory_usage_text,
    renderer._disk_usage_text,
    renderer._voltage_text,
  ) == ("41°C", "20%", "45%", "12.5V")

  sm.recv_frame["deviceState"] = 11
  renderer._update_state()
  assert renderer._device_info_recv_frames == (11, 20)
  assert (
    renderer._cpu_temp_text,
    renderer._memory_usage_text,
    renderer._disk_usage_text,
    renderer._voltage_text,
  ) == ("50°C", "30%", "60%", "13.2V")


def test_incomplete_device_info_is_retried(hud_module):
  module, fake_ui_state = hud_module
  renderer = object.__new__(module.HudRenderer)
  device_state = SimpleNamespace(
    freeSpacePercent=55.0,
    memoryUsagePercent=20,
    cpuUsagePercent=[10.0, 20.0],
  )
  peripheral_state = SimpleNamespace(voltage=12_500)
  fake_ui_state.sm = {
    "deviceState": device_state,
    "peripheralState": peripheral_state,
  }

  renderer._update_device_info()
  assert renderer._device_info_loaded is False

  device_state.cpuTempC = [40.0, 42.0]
  renderer._update_device_info()
  assert renderer._device_info_loaded is True
  assert renderer._cpu_temp == pytest.approx(41.0)
  assert renderer._cpu_usage == pytest.approx(15.0)
  assert renderer._voltage == pytest.approx(12.5)
  assert renderer._cpu_temp_text == "41°C"
  assert renderer._memory_usage_text == "20%"
  assert renderer._disk_usage_text == "45%"
  assert renderer._voltage_text == "12.5V"


def test_round_box_reuses_scratch_rectangle_without_changing_draw_geometry(hud_module, monkeypatch):
  module, _ = hud_module
  renderer = object.__new__(module.HudRenderer)
  renderer._round_box_rect = module.rl.Rectangle(0, 0, 0, 0)
  fill_color = module.rl.Color(1, 2, 3, 4)
  line_color = module.rl.Color(5, 6, 7, 8)
  calls = []

  def snapshot(kind, rect, *args):
    calls.append((kind, id(rect), (rect.x, rect.y, rect.width, rect.height), args))

  monkeypatch.setattr(module.rl, "draw_rectangle_rounded", lambda rect, *args: snapshot("fill", rect, *args))
  monkeypatch.setattr(module.rl, "draw_rectangle_rounded_lines_ex", lambda rect, *args: snapshot("line", rect, *args))

  renderer._draw_round_box(1, 2, 3, 4, fill_color, line_color, 0.25, 8, 2)
  renderer._draw_round_box(5, 6, 7, 8, fill_color, line_color, 0.5, 4, 3)

  assert [call[0] for call in calls] == ["fill", "line", "fill", "line"]
  assert len({call[1] for call in calls}) == 1
  assert [call[2] for call in calls] == [
    (1.0, 2.0, 3.0, 4.0),
    (1.0, 2.0, 3.0, 4.0),
    (5.0, 6.0, 7.0, 8.0),
    (5.0, 6.0, 7.0, 8.0),
  ]
  assert calls[0][3] == (0.25, 8, fill_color)
  assert calls[1][3] == (0.25, 8, 2.0, line_color)
  assert calls[2][3] == (0.5, 4, fill_color)
  assert calls[3][3] == (0.5, 4, 3.0, line_color)


@pytest.mark.parametrize(("value", "expected_text", "expected_color_name"), (
  (4.9, "  -", "WHITE_220"),
  (5.0, "5", "TPMS_LOW"),
  (5.1, "5", "TPMS_LOW"),
  (30.9, "31", "TPMS_LOW"),
  (31.0, "31", "WHITE_220"),
  (31.1, "31", "WHITE_220"),
  (59.9, "60", "WHITE_220"),
  (60.0, "60", "WHITE_220"),
  (60.1, "  -", "WHITE_220"),
))
def test_tpms_legacy_display_boundaries(hud_module, value, expected_text, expected_color_name):
  module, _ = hud_module
  renderer = object.__new__(module.HudRenderer)

  assert renderer._get_tpms_text(value) == expected_text
  assert renderer._get_tpms_color(value) == getattr(module.COLORS, expected_color_name)


@pytest.mark.parametrize(("show_tpms", "expected_y"), (
  (0, []),
  (1, [180]),
  (2, [675]),
  (3, [180, 675]),
))
def test_tpms_position_follows_show_tpms(hud_module, monkeypatch, show_tpms, expected_y):
  module, fake_ui_state = hud_module
  renderer = object.__new__(module.HudRenderer)
  renderer._show_tpms = show_tpms
  fake_ui_state.sm = {
    "carState": SimpleNamespace(tpms=SimpleNamespace(fl=31, fr=32, rl=33, rr=34)),
  }
  calls = []
  monkeypatch.setattr(renderer, "_draw_tpms_values", lambda bx, by, dw, *values: calls.append((bx, by, dw, values)))

  renderer._draw_tpms(module.rl.Rectangle(10, 50, 1000, 750))

  assert [call[1] for call in calls] == expected_y
  assert all(call[0] == 885 and call[2] == 80 for call in calls)
  assert all(call[3] == (31.0, 32.0, 33.0, 34.0) for call in calls)


def test_date_text_formats_only_when_second_key_changes(hud_module, monkeypatch):
  module, _ = hud_module
  renderer = object.__new__(module.HudRenderer)
  renderer._show_date_time = 1
  renderer._date_time_minute_key = None
  renderer._date_time_text = ""
  renderer._date_text = ""
  renderer._font_display = object()
  moments = iter((
    stdlib_time.struct_time((2026, 7, 16, 12, 1, 1, 3, 197, 0)),
    stdlib_time.struct_time((2026, 7, 16, 12, 1, 1, 3, 197, 0)),
    stdlib_time.struct_time((2026, 7, 16, 12, 1, 2, 3, 197, 0)),
    stdlib_time.struct_time((2026, 7, 16, 13, 2, 0, 3, 197, 0)),
  ))
  localtime_calls = []
  strftime_calls = []
  draw_calls = []

  def fake_localtime():
    localtime_calls.append(True)
    return next(moments)

  def fake_strftime(fmt, now):
    strftime_calls.append((fmt, now.tm_hour, now.tm_min, now.tm_sec))
    return f"{fmt}:{now.tm_hour:02d}:{now.tm_min:02d}"

  monkeypatch.setattr(module.time, "localtime", fake_localtime)
  monkeypatch.setattr(module.time, "strftime", fake_strftime)
  monkeypatch.setattr(module, "draw_text_ui_style", lambda *args, **kwargs: draw_calls.append((args, kwargs)))
  rect = module.rl.Rectangle(0, 0, 1000, 600)

  for _ in range(4):
    renderer._draw_date_time(rect)

  assert len(localtime_calls) == 4
  assert len(strftime_calls) == 6
  assert strftime_calls == [
    ("%H:%M:%S", 12, 1, 1), ("%m-%d", 12, 1, 1),
    ("%H:%M:%S", 12, 1, 2), ("%m-%d", 12, 1, 2),
    ("%H:%M:%S", 13, 2, 0), ("%m-%d", 13, 2, 0),
  ]
  assert len(draw_calls) == 8
  assert renderer._date_time_minute_key == (2026, 197, 13, 2, 0, 0)
  assert renderer._date_text.endswith(f"({module.WEEKDAYS_KO[4]})")

  renderer._show_date_time = 0
  monkeypatch.setattr(module.time, "localtime", lambda: pytest.fail("hidden date HUD read the clock"))
  renderer._draw_date_time(rect)
  assert len(draw_calls) == 8


def test_render_draws_each_hud_section_in_order(hud_module, monkeypatch):
  module, _ = hud_module
  renderer = object.__new__(module.HudRenderer)
  renderer.is_cruise_available = False
  renderer._show_plot_mode = 6
  renderer._font_display = object()
  calls = []

  renderer._blink_timer = 0
  renderer._exp_button = SimpleNamespace(render=lambda rect: calls.append("button"))
  renderer._screenshot_button = SimpleNamespace(render=lambda rect: calls.append("screenshot"))
  renderer._record_button = SimpleNamespace(
    set_blink_phase=lambda phase: calls.append(("blink", phase)),
    render=lambda rect: calls.append("record"),
  )
  renderer._plot_renderer = SimpleNamespace(
    draw=lambda rect, font, mode: calls.append(("plot", mode)),
  )
  monkeypatch.setattr(renderer, "_refresh_hud_params", lambda now: calls.append(("params", now)))
  monkeypatch.setattr(renderer, "_draw_date_time", lambda rect: calls.append("date"))
  monkeypatch.setattr(renderer, "_draw_tpms", lambda rect: calls.append("tpms"))
  monkeypatch.setattr(renderer, "_draw_egpu_badge", lambda rect: calls.append("egpu"))
  monkeypatch.setattr(renderer, "_draw_cruise_speed_animation", lambda rect: calls.append("animation"))
  monkeypatch.setattr(module.rl, "draw_rectangle_gradient_v", lambda *args: calls.append("header"))
  monkeypatch.setattr(module.time, "monotonic", lambda: 12.5)

  renderer._render(module.rl.Rectangle(0, 0, 1000, 600))

  assert calls == [
    ("params", 12.5),
    "header",
    "button",
    "screenshot",
    ("blink", True),
    "record",
    ("plot", 6),
    "date",
    "tpms",
    "egpu",
    "animation",
  ]


def test_vehicle_navigation_profile_does_not_force_speed_with_cruise_off(hud_module):
  module, _ = hud_module
  sm = {
    "longitudinalPlan": SimpleNamespace(cruiseTarget=0.0),
    "carrotMan": SimpleNamespace(
      vehicleNaviActive=True,
      vehicleNaviSpeed=105,
      desiredSpeed=105,
      desiredSource="hda_section",
    ),
  }

  override = module.SetSpeedOverride().compute(sm, set_speed_kph=105)

  assert not override.active
  assert override.speed_kph == 105
  assert override.label == "MAX"
  assert override.speed_color_mode == 0
  assert not override.force_persist


def test_hud_sections_are_timed_under_ui_hud_component(hud_module, monkeypatch):
  module, _ = hud_module
  events = []

  class RecordingTiming:
    def __init__(self, component):
      events.append(("component", component))

    def start(self):
      events.append("start")

    def call(self, name, callback, *args):
      events.append(name)
      return callback(*args)

    def finish(self):
      events.append("finish")

  monkeypatch.setattr(module, "RenderDiagnostics", RecordingTiming)
  renderer = object.__new__(module.HudRenderer)
  renderer.is_cruise_available = False
  renderer._show_plot_mode = 0
  renderer._font_display = object()
  renderer._blink_timer = 0
  renderer._exp_button = SimpleNamespace(render=lambda rect: None)
  renderer._screenshot_button = SimpleNamespace(render=lambda rect: None)
  renderer._record_button = SimpleNamespace(set_blink_phase=lambda phase: None, render=lambda rect: None)
  renderer._plot_renderer = SimpleNamespace(draw=lambda rect, font, mode: None)
  monkeypatch.setattr(renderer, "_refresh_hud_params", lambda now: None)
  monkeypatch.setattr(renderer, "_draw_date_time", lambda rect: None)
  monkeypatch.setattr(renderer, "_draw_tpms", lambda rect: events.append("tpms_body"))
  monkeypatch.setattr(renderer, "_draw_egpu_badge", lambda rect: events.append("egpu_body"))
  monkeypatch.setattr(renderer, "_draw_cruise_speed_animation", lambda rect: None)
  monkeypatch.setattr(module.rl, "draw_rectangle_gradient_v", lambda *args: None)

  renderer._render(module.rl.Rectangle(0, 0, 1000, 600))

  assert events == [
    ("component", "uiHud"),
    "start",
    "params",
    "header",
    "exp_button",
    "screenshot_button",
    "record_button",
    "plot",
    "date_time",
    "tpms",
    "tpms_body",
    "egpu_body",
    "cruise_anim",
    "finish",
  ]


def test_set_speed_sections_are_timed_in_draw_order(hud_module, monkeypatch):
  module, _ = hud_module
  events = []

  class RecordingTiming:
    def __init__(self, component):
      pass

    def call(self, name, callback, *args):
      events.append(name)
      return callback(*args)

  monkeypatch.setattr(module, "RenderDiagnostics", RecordingTiming)
  renderer = object.__new__(module.HudRenderer)
  renderer._blink_timer = 0
  renderer._disp_timer = 0
  snapshot = (80, 2, 90)
  seen = []
  monkeypatch.setattr(renderer, "_get_speed_limit_info", lambda: snapshot)
  monkeypatch.setattr(renderer, "_draw_carrot_main_background", lambda bx, by, info: seen.append(info))
  monkeypatch.setattr(renderer, "_draw_carrot_traffic_light", lambda bx, by: None)
  monkeypatch.setattr(renderer, "_draw_carrot_speed_panel", lambda bx, by: None)
  monkeypatch.setattr(renderer, "_draw_carrot_lower_status", lambda bx, by: None)
  monkeypatch.setattr(renderer, "_draw_carrot_speed_limit_box", lambda bx, by, info: seen.append(info))
  monkeypatch.setattr(renderer, "_draw_carrot_device_state", lambda bx, by: None)
  monkeypatch.setattr(renderer, "_draw_turn_info_hud", lambda rect: None)

  renderer._draw_set_speed_carrot(module.rl.Rectangle(10, 20, 1000, 600))

  assert events == [
    "speed_limit_info",
    "main_bg",
    "traffic_light",
    "speed_panel",
    "lower_status",
    "speed_limit_box",
    "device_state",
    "turn_info",
  ]
  assert seen == [snapshot, snapshot]


# --- PlotRenderer: 그리기 간격(PLOT_DRAW_STRIDE) 경량화 ---------------------------------


def _plot_capture(module, monkeypatch):
  """_draw_plotting이 그린 선분 끝점(x, y)과 숫자 텍스트를 기록한다."""
  lines = []
  texts = []
  monkeypatch.setattr(module.rl, "draw_line_ex", lambda a, b, thickness, color: lines.append(((a.x, a.y), (b.x, b.y))))
  monkeypatch.setattr(module, "draw_text_ui_style", lambda text, *args, **kwargs: texts.append(text))
  return lines, texts


def _plot_feed(renderer, values):
  for v in values:
    renderer._update_plot_queue([v, v + 0.25, v - 0.25])


def _plot_points(lines):
  """선분 목록을 그린 순서대로의 점 목록으로 되돌린다(첫 점 + 각 선분의 끝점)."""
  if not lines:
    return []
  return [lines[0][0]] + [end for _, end in lines]


def _plot_reference_points(renderer, index):
  """변경 전 구현(모든 샘플, 샘플마다 나머지 연산)을 그대로 옮긴 기준값."""
  plot_range = renderer._plot_max - renderer._plot_min
  ratio = renderer._plot_height if plot_range < 1.0 else renderer._plot_height / plot_range
  pts = []
  for i in range(renderer._plot_size):
    data = renderer._plot_queue[index][(renderer._plot_index - i + renderer.PLOT_MAX) % renderer.PLOT_MAX]
    y = 0.0 + renderer._plot_height - (data - renderer._plot_min) * ratio
    x = 0.0 + (renderer._plot_size - i) * renderer._plot_dx
    pts.append((x, y))
  return pts


def test_plot_draw_stride_default_is_two(hud_module):
  module, _ = hud_module
  assert module.PlotRenderer.PLOT_DRAW_STRIDE == 2


@pytest.mark.parametrize("count", [1, 2, 3, 37, 399, 400, 401, 799, 1234])
def test_plot_stride_one_matches_previous_implementation(hud_module, monkeypatch, count):
  module, _ = hud_module
  monkeypatch.setattr(module.PlotRenderer, "PLOT_DRAW_STRIDE", 1)
  renderer = module.PlotRenderer()
  lines, texts = _plot_capture(module, monkeypatch)
  _plot_feed(renderer, [((n * 7) % 23) * 0.1 - 1.0 for n in range(count)])

  for index in range(3):
    lines.clear()
    texts.clear()
    renderer._draw_plotting(index, 0.0, 0.0, module.rl.WHITE, None)
    expected = _plot_reference_points(renderer, index)
    if len(expected) > 1:
      assert _plot_points(lines) == expected
    else:
      assert not lines
    assert len(texts) == 1


@pytest.mark.parametrize("stride", [2, 3])
@pytest.mark.parametrize("count", [1, 2, 5, 40, 399, 400, 401, 777])
def test_plot_stride_draws_only_sample_numbers_on_the_stride_plus_latest(hud_module, monkeypatch, stride, count):
  module, _ = hud_module
  monkeypatch.setattr(module.PlotRenderer, "PLOT_DRAW_STRIDE", stride)
  renderer = module.PlotRenderer()
  lines, texts = _plot_capture(module, monkeypatch)
  # 값이 곧 누적 샘플 번호가 되게 한다(y에서 번호를 되찾기 위해 범위를 고정한다).
  _plot_feed(renderer, [float(n) for n in range(count)])
  renderer._plot_min, renderer._plot_max = 0.0, float(renderer._plot_height)  # ratio == 1
  renderer._draw_plotting(0, 0.0, 0.0, module.rl.WHITE, None)

  size = renderer._plot_size
  drawn = []
  for x, y in _plot_points(lines):
    age = size - round(x / renderer._plot_dx)
    drawn.append(count - 1 - age)  # 누적 샘플 번호
  drawn_set = set(drawn)

  oldest = count - size
  expected = {n for n in range(oldest, count) if n % stride == 0} | {count - 1}
  if size == 1:
    assert not lines
  else:
    assert drawn_set == expected
    assert drawn == sorted(drawn, reverse=True)  # 최신부터 오래된 순
    assert drawn[0] == count - 1  # 최신 점은 항상 그린다
  assert texts == [f"{float(count - 1):.2f}"]


@pytest.mark.parametrize("stride", [2, 3])
def test_plot_stride_keeps_same_samples_while_scrolling(hud_module, monkeypatch, stride):
  module, _ = hud_module
  monkeypatch.setattr(module.PlotRenderer, "PLOT_DRAW_STRIDE", stride)
  renderer = module.PlotRenderer()
  lines, _ = _plot_capture(module, monkeypatch)
  _plot_feed(renderer, [float(n) for n in range(450)])
  renderer._plot_min, renderer._plot_max = 0.0, float(renderer._plot_height)

  def anchors():
    lines.clear()
    renderer._draw_plotting(0, 0.0, 0.0, module.rl.WHITE, None)
    pts = _plot_points(lines)
    size = renderer._plot_size
    # 가장 최근 점은 매번 새로 생기므로 앵커(누적 번호가 stride 배수)만 비교한다.
    nums = [renderer._plot_total - 1 - (size - round(x / renderer._plot_dx)) for x, _ in pts]
    return {n for n in nums if n % stride == 0}

  before = anchors()
  for _ in range(stride * 5):
    _plot_feed(renderer, [float(renderer._plot_total)])
    renderer._plot_min, renderer._plot_max = 0.0, float(renderer._plot_height)
    after = anchors()
    # 이전 프레임에서 그려진 앵커 중 버퍼 밖으로 밀려난 것을 뺀 나머지는 계속 그려진다.
    still_inside = {n for n in before if n >= renderer._plot_total - renderer._plot_size}
    assert still_inside <= after
    before = after


def test_plot_stride_value_text_is_latest_sample(hud_module, monkeypatch):
  module, _ = hud_module
  renderer = module.PlotRenderer()
  lines, texts = _plot_capture(module, monkeypatch)
  _plot_feed(renderer, [1.0, 2.0, 3.0, 4.5])
  renderer._draw_plotting(1, 0.0, 0.0, module.rl.WHITE, None)
  assert texts == ["4.75"]  # 두 번째 선은 최신 값 + 0.25


def test_plot_stride_empty_and_single_sample(hud_module, monkeypatch):
  module, _ = hud_module
  renderer = module.PlotRenderer()
  lines, texts = _plot_capture(module, monkeypatch)
  renderer._draw_plotting(0, 0.0, 0.0, module.rl.WHITE, None)
  assert not lines and not texts
  _plot_feed(renderer, [2.0])
  renderer._draw_plotting(0, 0.0, 0.0, module.rl.WHITE, None)
  assert not lines and texts == ["2.00"]


def test_plot_clear_resets_sample_counter(hud_module):
  module, _ = hud_module
  renderer = module.PlotRenderer()
  _plot_feed(renderer, [1.0, 2.0, 3.0])
  assert renderer._plot_total == 3
  renderer._clear()
  assert renderer._plot_total == 0 and renderer._plot_size == 0


def test_plot_stride_draws_fewer_lines_than_every_sample(hud_module, monkeypatch):
  module, _ = hud_module
  renderer = module.PlotRenderer()
  lines, _ = _plot_capture(module, monkeypatch)
  _plot_feed(renderer, [float(n % 11) for n in range(600)])
  renderer._draw_plotting(0, 0.0, 0.0, module.rl.WHITE, None)
  # 400샘플을 2개마다 -> 약 200점, 선분은 약 200개(전부 그리면 399개)
  assert 190 <= len(lines) <= 201
