import pyray as rl

from openpilot.common.swaglog import cloudlog
from openpilot.system.ui.widgets import Widget


class ScreenshotButton(Widget):
  """Bottom-center onroad button that saves a screenshot into the folder
  carrotweb's log tab already scans for screen recordings.

  Uses an explicit tap-on-a-button instead of a double-tap-anywhere gesture,
  so it never conflicts with the existing single-tap sidebar toggle on the
  rest of the onroad screen (see augmented_road_view.py's click_callback).

  51cha: the actual capture no longer happens inside _on_click(). HudRenderer
  draws this button before _draw_date_time()/_draw_tpms() in its _render()
  method, so a screenshot taken at click time only contains what was already
  drawn up to that point in the frame -- the clock/temperature/etc drawn
  later in the same frame are missing from the saved file (root cause of the
  51cha report "capture works but the clock/temperature HUD is missing").
  Instead, _on_click() only raises a pending flag; HudRenderer consumes it
  via consume_pending_capture() at the very end of _render(), after every
  HUD element for this frame has been drawn, and only then calls
  capture_onroad_screenshot().
  """

  def __init__(self, button_size: int):
    super().__init__()
    self._rect = rl.Rectangle(0, 0, button_size, button_size)
    self._black_bg = rl.Color(0, 0, 0, 166)
    self._pending_capture = False
    self.set_click_callback(self._on_click)

  def _on_click(self) -> None:
    # 49차: 클릭 콜백이 실제로 호출되는지 자체를 로그로 남겨, "버튼이 안
    # 눌러진다"는 제보가 (a) 클릭이 전달되지 않는 문제인지 (b) 클릭은
    # 전달되지만 캡처만 실패하는 문제인지 다음 실차 테스트에서 구분한다.
    # 51차: 실제 캡처 호출은 이 프레임의 HUD 요소가 모두 그려진 뒤로
    # 미룬다(위 클래스 docstring 참고) -- 여기서는 플래그만 세운다.
    cloudlog.debug("ScreenshotButton clicked")
    self._pending_capture = True

  def consume_pending_capture(self) -> bool:
    """Return True at most once per click; caller is responsible for
    performing the actual capture after this frame's remaining HUD
    elements have been drawn."""
    pending = self._pending_capture
    self._pending_capture = False
    return pending

  def _render(self, rect: rl.Rectangle) -> None:
    center_x = int(self._rect.x + self._rect.width // 2)
    center_y = int(self._rect.y + self._rect.height // 2)
    radius = self._rect.width / 2
    alpha = 180 if self.is_pressed else 255
    icon_color = rl.Color(255, 255, 255, alpha)

    rl.draw_circle(center_x, center_y, radius, self._black_bg)

    body_w, body_h = radius * 1.15, radius * 0.72
    body_x = center_x - body_w / 2
    body_y = center_y - body_h / 2 + radius * 0.10
    rl.draw_rectangle_rounded(rl.Rectangle(body_x, body_y, body_w, body_h), 0.30, 8, icon_color)

    bump_w, bump_h = body_w * 0.30, body_h * 0.36
    rl.draw_rectangle_rounded(
      rl.Rectangle(center_x - bump_w / 2, body_y - bump_h * 0.65, bump_w, bump_h), 0.35, 8, icon_color
    )

    lens_center_y = int(body_y + body_h / 2)
    lens_r = body_h * 0.34
    rl.draw_circle(center_x, lens_center_y, lens_r, self._black_bg)
    rl.draw_circle_lines(center_x, lens_center_y, lens_r, icon_color)
