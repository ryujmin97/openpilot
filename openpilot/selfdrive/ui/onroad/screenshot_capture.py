import os
import time

import pyray as rl

from openpilot.common.swaglog import cloudlog
from openpilot.selfdrive.carrot.server.config import SCREEN_RECORDING_DIRS

SCREENSHOT_DIR = SCREEN_RECORDING_DIRS[1]  # "/data/media/0/screenrecord"
MAX_SCREENSHOT_HEIGHT = 480  # 51cha: downscale before saving, see docstring


def save_screenshot_image(image: rl.Image) -> str | None:
  """Downscale and save an already-captured rl.Image into SCREENSHOT_DIR.

  54cha: this replaces the previous capture_onroad_screenshot(), which read
  the frame directly with rl.load_image_from_screen() (or, before 47cha,
  rl.take_screenshot()). Both approaches had real-device problems specific to
  reading pixels mid-frame or straight off the screen buffer:
  - rl.take_screenshot() sized the capture as render_width/height *
    GetWindowScaleDPI() (raylib's rcore.c); on this device that DPI scale
    came out anisotropic, producing a portrait file for a landscape frame
    (47cha).
  - rl.load_image_from_screen() avoided the DPI bug but was still called
    mid-frame, before every HUD element for that frame had been drawn, so
    the clock/temperature/etc were missing from the saved file (51cha) --
    and further reordering the call within the same widget-render pass still
    missed border/alert/driver-state overlays drawn even later (52cha).
    53cha's real-device test also showed rl.export_image() failing outright
    on JPG targets on this raylib build (comma-deps-raylib==6.0.0.1.post101,
    confirmed via 49cha/50cha diagnostic logging), separate from the framing
    problems above.

  54cha fixes the framing problems structurally instead of chasing draw-order
  bugs one HUD element at a time: the caller (screenshot_button.py) requests
  a one-shot capture via GuiApplication.request_temp_capture(), which reuses
  the exact mechanism recording already relies on to get a complete frame --
  render everything into an offscreen render texture, then read the texture
  with rl.load_image_from_texture() only after end_texture_mode() confirms
  the frame is fully drawn (see application.py's render() loop). By
  construction this always contains every widget drawn that frame, in
  whatever order, so there is no more HUD-ordering class of bug to chase
  here. This function only does the save/downscale step on the Image that
  mechanism produces.

  Takes ownership of `image`: always unloads it via rl.unload_image(),
  whether the save succeeds or fails. Returns the final path on success,
  None on failure (never raises -- a failed screenshot should not affect
  driving).
  """
  filename = time.strftime("screenshot_%Y-%m-%d_%H-%M-%S.png")
  try:
    if image.width <= 0 or image.height <= 0:
      cloudlog.warning(f"save_screenshot_image: invalid image {image.width}x{image.height}")
      return None
    # 55cha: rl.load_image_from_texture() on a render texture returns pixel rows in
    # OpenGL's bottom-up order. The video recording paths already correct this with
    # ffmpeg's "vflip" filter (see application.py); this path never did the equivalent,
    # so every render-texture-based screenshot (54cha onward) was saved upside down.
    rl.image_flip_vertical(image)
    if image.height > MAX_SCREENSHOT_HEIGHT:
      target_width = max(1, round(image.width * MAX_SCREENSHOT_HEIGHT / image.height))
      rl.image_resize(image, target_width, MAX_SCREENSHOT_HEIGHT)
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    dst = os.path.join(SCREENSHOT_DIR, filename)
    if not rl.export_image(image, dst):
      cloudlog.warning(f"save_screenshot_image: export_image failed for {dst}")
      return None
    if not os.path.isfile(dst) or os.path.getsize(dst) <= 0:
      cloudlog.warning(f"save_screenshot_image: {dst} missing or empty after export_image")
      return None
    return dst
  except Exception:
    cloudlog.exception("save_screenshot_image failed")
    return None
  finally:
    rl.unload_image(image)