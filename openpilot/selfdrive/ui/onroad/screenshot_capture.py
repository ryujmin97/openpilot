import os
import time

import pyray as rl

from openpilot.common.swaglog import cloudlog
from openpilot.selfdrive.carrot.server.config import SCREEN_RECORDING_DIRS

SCREENSHOT_DIR = SCREEN_RECORDING_DIRS[1]  # "/data/media/0/screenrecord"
MAX_SCREENSHOT_HEIGHT = 480  # 51cha: downscale before saving, see docstring


def capture_onroad_screenshot() -> str | None:
  """Save a PNG of the current onroad frame into SCREENSHOT_DIR.

  Previously used rl.take_screenshot(), which internally sizes the capture
  as render_width/height * GetWindowScaleDPI() (raylib's rcore.c). On this
  device that DPI scale came out anisotropic (swapped x/y), so the saved
  file came out portrait (e.g. 1080x2160) instead of the actual 2160x1080
  onroad frame, with only part of the buffer holding real pixels and the
  rest black.

  rl.load_image_from_screen() reads the same framebuffer via the logical
  GetScreenWidth()/GetScreenHeight() with no DPI multiplication, so it
  isn't affected by that scale bug -- the same "read screen contents
  directly, skip the DPI-scaled path" idea already proven correct for
  video recording (see GuiApplication.render()'s
  rl.load_image_from_texture() usage).

  Saved as .jpg (was .png): a photographic onroad frame compresses far
  smaller as JPEG than as lossless PNG, and SCREEN_RECORDING_PHOTO_EXTS in
  carrot/server/config.py already lists ".jpg"/".jpeg" alongside ".png",
  so no backend/frontend changes are needed for the new extension to be
  listed, thumbnailed, and served.

  50cha temporary rollback: real-device swaglog after 49cha showed
  rl.export_image() failing on every attempt at the raylib level
  ("Failed to export image"), and the 49cha diagnostic log for that
  failure fired from inside _on_click -- confirming the click path and
  load_image_from_screen() are not the problem. Before 47cha, .png
  exports were succeeding (just with the wrong DPI-scaled dimensions);
  every failure since has been on a .jpg target. So JPG export support
  in this device's raylib build (comma-deps-raylib==6.0.0.1.post101) is
  the leading suspect. Reverting only the extension to .png here, while
  keeping the load_image_from_screen() DPI fix, isolates that one
  variable for the next real-device test (11-jeol: isolate before
  confirming a cause). 50cha real-device test confirmed .png export now
  succeeds and files show up in the log tab, so JPG export being
  unsupported on this raylib build is treated as confirmed; staying on
  .png going forward.

  51cha: downscale to MAX_SCREENSHOT_HEIGHT (480p) before export_image(),
  via rl.image_resize() (in-place, keeps aspect ratio) -- purely a
  file-size/storage reduction. This does not affect *what* content ends
  up in the frame; see screenshot_button.py's 51cha docstring note for
  the separate fix that makes the clock/temperature HUD actually present
  in the captured frame. If rl.image_resize() itself misbehaves on this
  raylib build, the outer try/except below still catches it and logs via
  cloudlog.exception, so a resize failure degrades to "no screenshot
  saved" rather than affecting driving (12-jeol: not yet real-device
  verified).

  Returns the final path on success, None on failure (never raises --
  a failed screenshot should not affect driving).
  """
  filename = time.strftime("screenshot_%Y-%m-%d_%H-%M-%S.png")
  image = None
  try:
    image = rl.load_image_from_screen()
    if image.width <= 0 or image.height <= 0:
      cloudlog.warning(f"capture_onroad_screenshot: load_image_from_screen returned {image.width}x{image.height}")
      return None
    if image.height > MAX_SCREENSHOT_HEIGHT:
      target_width = max(1, round(image.width * MAX_SCREENSHOT_HEIGHT / image.height))
      rl.image_resize(image, target_width, MAX_SCREENSHOT_HEIGHT)
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    dst = os.path.join(SCREENSHOT_DIR, filename)
    if not rl.export_image(image, dst):
      cloudlog.warning(f"capture_onroad_screenshot: export_image failed for {dst}")
      return None
    if not os.path.isfile(dst) or os.path.getsize(dst) <= 0:
      cloudlog.warning(f"capture_onroad_screenshot: {dst} missing or empty after export_image")
      return None
    return dst
  except Exception:
    # 49차: 이전에는 여기서 원인 정보 없이 조용히 실패해, 버튼을 눌러도
    # 아무 반응이 없다는 사용자 제보의 원인을 특정할 수 없었다. 다음 실차
    # 테스트에서 실패 원인이 로그에 남도록 cloudlog.exception 추가.
    cloudlog.exception("capture_onroad_screenshot failed")
    return None
  finally:
    if image is not None:
      rl.unload_image(image)
