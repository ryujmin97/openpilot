import os
import shutil
import time
from pathlib import Path

import pyray as rl

from openpilot.selfdrive.carrot.server.config import SCREEN_RECORDING_DIRS

SCREENSHOT_DIR = SCREEN_RECORDING_DIRS[1]  # "/data/media/0/screenrecord"


def capture_onroad_screenshot() -> str | None:
  """Save a PNG of the current onroad frame into SCREENSHOT_DIR.

  rl.take_screenshot() is only confirmed (via existing usage in
  radar_validation_replay.py) to reliably write relative to the process's
  current working directory -- passing it an absolute path has not been
  verified on-device. So we screenshot to a plain filename in cwd first,
  then move the resulting file into place.

  Returns the final path on success, None on failure (never raises --
  a failed screenshot should not affect driving).
  """
  filename = time.strftime("screenshot_%Y-%m-%d_%H-%M-%S.png")
  try:
    rl.take_screenshot(filename)
    src = Path.cwd() / filename
    if not src.is_file():
      return None
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    dst = os.path.join(SCREENSHOT_DIR, filename)
    shutil.move(str(src), dst)
    return dst
  except Exception:
    return None