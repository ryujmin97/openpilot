from __future__ import annotations

import os
from collections.abc import Callable, Mapping
from contextlib import ExitStack
from typing import Any


DEFAULT_WEB_UPLOAD_URL = "https://upload.shind0.synology.me"
DEFAULT_TOSS_UPLOAD_URL = "https://op.wjcloud.kr"
DEFAULT_TMUX_WEB_UPLOAD_URL = "https://tmux.carrotpilot.app/upload"
UPLOAD_TARGETS = {"carrot", "toss"}


def normalize_base_url(value: Any, default: str = "") -> str:
  url = str(value or "").strip().rstrip("/")
  if not url:
    url = str(default or "").strip().rstrip("/")
  if url and not url.startswith(("http://", "https://")):
    raise ValueError("web upload URL must start with http:// or https://")
  return url


def web_upload_settings(settings: Mapping[str, Any] | None = None) -> tuple[str, str]:
  """Return the upstream Carrot Web API settings.

  Toss credentials intentionally do not fall back into this path: the selected
  target owns its own URL/token so changing one target cannot redirect the other.
  """
  settings = settings or {}
  base_url = (
    os.environ.get("CARROT_WEB_UPLOAD_URL", "").strip()
    or str(settings.get("web_upload_url") or "").strip()
    or DEFAULT_WEB_UPLOAD_URL
  )
  # Normal Carrot users receive a short-lived session automatically. Keep the
  # environment override for private Carrot deployments using a static token.
  token = os.environ.get("CARROT_WEB_UPLOAD_TOKEN", "").strip()
  return normalize_base_url(base_url), token


def toss_upload_settings(settings: Mapping[str, Any] | None = None) -> tuple[str, str]:
  settings = settings or {}
  base_url = (
    os.environ.get("CARROT_TOSS_UPLOAD_URL", "").strip()
    or str(settings.get("toss_upload_url") or "").strip()
    or DEFAULT_TOSS_UPLOAD_URL
  )
  token = (
    os.environ.get("CARROT_TOSS_UPLOAD_TOKEN", "").strip()
    or str(settings.get("toss_upload_token") or "").strip()
  )
  return normalize_base_url(base_url), token


def selected_upload_settings(settings: Mapping[str, Any] | None = None) -> tuple[str, str, str]:
  settings = settings or {}
  target = str(settings.get("log_upload_target") or "carrot").strip().lower()
  target = target if target in UPLOAD_TARGETS else "carrot"
  base_url, token = toss_upload_settings(settings) if target == "toss" else web_upload_settings(settings)
  return target, base_url, token


def carrot_logs_web_target() -> tuple[str, dict[str, str]]:
  """Return the independent Carrot Logs receiver used by the Discord forum.

  This target must not depend on the DSM upload token. Diagnostics are sent to
  both destinations, so a configured DSM token must never redirect this copy
  away from the Carrot Logs service.
  """
  direct_url = normalize_base_url(
    os.environ.get("CARROT_TMUX_WEB_UPLOAD_URL", ""),
    DEFAULT_TMUX_WEB_UPLOAD_URL,
  )
  return direct_url, {}


def upload_device_id(metadata: Mapping[str, Any]) -> str:
  for key in ("dongleId", "dongle_id", "deviceId", "device_id", "serial", "device_serial"):
    value = str(metadata.get(key) or "").strip()
    if value and value.lower() not in {"unknown", "none"}:
      return value
  return "unknown"


def post_tmux_web(
  url: str,
  headers: Mapping[str, str],
  payload: Mapping[str, Any],
  tmux_path: str,
  settings_path: str | None = None,
  post: Callable[..., Any] | None = None,
):
  if post is None:
    raise ValueError("web POST function is required")
  with ExitStack() as stack:
    tmux_file = stack.enter_context(open(tmux_path, "rb"))
    files = [("files[0]", ("tmux.log", tmux_file, "text/plain"))]
    if settings_path and os.path.isfile(settings_path):
      settings_file = stack.enter_context(open(settings_path, "rb"))
      files.append(("files[1]", ("toggle_values.json", settings_file, "application/json")))
    return post(
      url,
      headers=dict(headers),
      data=dict(payload),
      files=files,
      timeout=30,
    )