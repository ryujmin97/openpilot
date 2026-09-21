from __future__ import annotations

import time
from typing import Iterable

_MESSAGING_IMPORT_ERROR: Exception | None = None
try:
  import openpilot.cereal.messaging as messaging
except ModuleNotFoundError as exc:
  messaging = None  # type: ignore[assignment]
  _MESSAGING_IMPORT_ERROR = exc

from .contract import DEFAULT_CAMERA_KIND
from .services import build_service_list
from .snapshot import build_live_payload, empty_live_payload

try:
  from openpilot.common.params import Params  # type: ignore
except Exception:
  Params = None

class RealtimeBroker:
  def __init__(
    self,
    *,
    repo_flavor: str,
    selected_camera: str = DEFAULT_CAMERA_KIND,
    include_optional: Iterable[str] | None = None,
    exclude_services: Iterable[str] | None = None,
  ) -> None:
    if messaging is None:
      raise RuntimeError(
        "realtime broker requires openpilot native messaging artifacts. "
        "Build openpilot first so msgq/ipc_pyx.so is available."
      ) from _MESSAGING_IMPORT_ERROR

    self.repo_flavor = repo_flavor
    self.selected_camera = selected_camera
    self.service_names = build_service_list(include_optional=include_optional, exclude=exclude_services)
    self.sm = messaging.SubMaster(self.service_names)
    self.params = Params() if Params is not None else None

    self.last_snapshot = empty_live_payload(repo_flavor=repo_flavor, selected_camera=selected_camera)
    self.last_snapshot_monotonic = 0.0

  def poll(self, timeout: int = 0) -> dict:
    self.sm.update(timeout)
    params_snapshot = self._read_params()
    snapshot = build_live_payload(
      sm=self.sm,
      repo_flavor=self.repo_flavor,
      selected_camera=self.selected_camera,
      params_snapshot=params_snapshot,
      capability_flags=self.capability_flags(),
      previous_payload=self.last_snapshot,
    )
    self.last_snapshot = snapshot
    self.last_snapshot_monotonic = time.monotonic()
    return snapshot

  def snapshot_age_ms(self) -> int | None:
    if self.last_snapshot_monotonic <= 0:
      return None
    return int((time.monotonic() - self.last_snapshot_monotonic) * 1000)

  def capability_flags(self) -> list[str]:
    flags = ["live", "camera-road", "road-only-ui", "carrotlink-projection"]
    if "wideRoadCameraState" in self.service_names:
      flags.append("wide-meta")
    return flags

  def _read_params(self) -> dict:
    if self.params is None:
      return {}

    names = (
      "IsMetric",
      "LongitudinalPersonality",
      "ShowDateTime",
      "ShowPathEnd",
      "ShowLaneInfo",
      "ShowPathMode",
      "ShowPathColor",
      "ShowPathModeLane",
      "ShowPathColorLane",
      "ShowPathColorCruiseOff",
      "ShowPathWidth",
      "ShowPlotMode",
      "ShowRadarInfo",
      "RadarLatFactor",
      "CustomSR",
    )
    snapshot: dict[str, object] = {}
    for name in names:
      try:
        if name == "IsMetric":
          snapshot[name] = "1" if self.params.get_bool(name) else "0"
          continue
        value = self.params.get(name)
      except Exception:
        value = None
      if value is None:
        snapshot[name] = None
      elif isinstance(value, bytes):
        snapshot[name] = value.decode("utf-8", errors="replace")
      else:
        snapshot[name] = str(value)
    return snapshot

