import pyray as rl

from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.widgets import Widget


class RecordButton(Widget):
  """Bottom-center onroad button, placed next to ScreenshotButton, that toggles
  screen recording by flipping the shared "ScreenRecord" param.

  Recording can also be started/stopped from carrotweb's Record button or a
  carrotMan RECORD command (see layouts/main.py's _handle_carrot_record_cmd),
  so the drawn state always reflects the live gui_app.is_recording() status
  instead of tracking a local on/off flag.

  [44cha] While recording, the filled dot blinks (driven by hud_renderer's
  shared _blink_timer via set_blink_phase()) instead of staying solid, so
  it reads as an active indicator rather than a one-off color change.
  """

  def __init__(self, button_size: int):
    super().__init__()
    self._rect = rl.Rectangle(0, 0, button_size, button_size)
    self._black_bg = rl.Color(0, 0, 0, 166)
    self._red = rl.Color(235, 62, 54, 255)
    self._blink_on = True
    self.set_click_callback(self._on_click)

  def set_blink_phase(self, on: bool) -> None:
    self._blink_on = on

  def _on_click(self) -> None:
    try:
      recording = ui_state.params.get_bool("ScreenRecord")
    except Exception:
      recording = gui_app.is_recording()
    ui_state.params.put_bool_nonblocking("ScreenRecord", not recording)

  def _render(self, rect: rl.Rectangle) -> None:
    center_x = int(self._rect.x + self._rect.width // 2)
    center_y = int(self._rect.y + self._rect.height // 2)
    radius = self._rect.width / 2
    alpha = 180 if self.is_pressed else 255

    rl.draw_circle(center_x, center_y, radius, self._black_bg)

    dot_radius = radius * 0.55
    if gui_app.is_recording():
      red = rl.Color(self._red.r, self._red.g, self._red.b, alpha)
      if self._blink_on:
        rl.draw_circle(center_x, center_y, dot_radius, red)
      else:
        rl.draw_circle_lines(center_x, center_y, dot_radius, red)
    else:
      rl.draw_circle_lines(center_x, center_y, dot_radius, rl.Color(255, 255, 255, alpha))