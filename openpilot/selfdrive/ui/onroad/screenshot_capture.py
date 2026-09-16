import os
import time

import pyray as rl

from openpilot.selfdrive.carrot.server.config import SCREEN_RECORDING_DIRS

SCREENSHOT_DIR = SCREEN_RECORDING_DIRS[1]  # "/data/media/0/screenrecord"


def capture_onroad_screenshot() -> str | None:
  """Save a JPG of the current onroad frame into SCREENSHOT_DIR.

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

  Returns the final path on success, None on failure (never raises --
  a failed screenshot should not affect driving).
  """
  filename = time.strftime("screenshot_%Y-%m-%d_%H-%M-%S.jpg")
  image = None
  try:
    image = rl.load_image_from_screen()
    if image.width <= 0 or image.height <= 0:
      return None
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    dst = os.path.join(SCREENSHOT_DIR, filename)
    if not rl.export_image(image, dst):
      return None
    if not os.path.isfile(dst) or os.path.getsize(dst) <= 0:
      return None
    return dst
  except Exception:
    return None
  finally:
    if image is not None:
      rl.unload_image(image)
