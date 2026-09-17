import asyncio
import mimetypes
import os
import threading
import time

from aiohttp import web

from openpilot.selfdrive.carrot import gdrive_upload

from ...config import SCREEN_RECORDING_DIRS
from .catalog import build_photos, build_videos, find_file, find_photo, photo_thumbnail_path, thumbnail_path

VIDEO_CACHE_TTL = 3.0
_video_cache_lock = threading.Lock()
_video_cache = {"time": 0.0, "videos": []}


def cached_screenrecord_videos() -> list[dict]:
  now = time.monotonic()
  with _video_cache_lock:
    if now - float(_video_cache.get("time") or 0.0) < VIDEO_CACHE_TTL:
      return list(_video_cache.get("videos") or [])

  videos = build_videos()
  with _video_cache_lock:
    _video_cache["time"] = time.monotonic()
    _video_cache["videos"] = videos
  return list(videos)


async def api_screenrecord_videos(request: web.Request) -> web.Response:
  try:
    offset = max(0, int(request.query.get("offset", "0") or 0))
    limit = max(1, min(200, int(request.query.get("limit", "80") or 80)))
    videos = await asyncio.to_thread(cached_screenrecord_videos)
    total = len(videos)
    end = min(offset + limit, total)
    folders = [folder for folder in SCREEN_RECORDING_DIRS if os.path.isdir(folder)]
    return web.json_response({
      "ok": True,
      "videos": videos[offset:end],
      "folders": folders,
      "offset": offset,
      "limit": limit,
      "total": total,
      "nextOffset": end if end < total else None,
      "hasMore": end < total,
    })
  except Exception as e:
    return web.json_response({"ok": False, "error": str(e)}, status=500)


async def api_screenrecord_thumbnail(request: web.Request) -> web.StreamResponse:
  file_id_in = request.match_info.get("file_id", "")
  path = await asyncio.to_thread(thumbnail_path, file_id_in)
  return web.FileResponse(path, headers={"Cache-Control": "public, max-age=86400"})


async def api_screenrecord_video(request: web.Request) -> web.StreamResponse:
  file_id_in = request.match_info.get("file_id", "")
  path = await asyncio.to_thread(find_file, file_id_in)
  mime = mimetypes.guess_type(path)[0] or "application/octet-stream"
  headers = {
    "Content-Type": mime,
    "Cache-Control": "private, max-age=3600",
  }
  if request.query.get("download"):
    filename = os.path.basename(path)
    safe_filename = "".join(ch if 32 <= ord(ch) < 127 and ch not in {'"', "\\"} else "_" for ch in filename)
    headers["Content-Disposition"] = f'attachment; filename="{safe_filename or "screenrecord"}"'
  return web.FileResponse(path, headers=headers)


async def api_screenrecord_download(request: web.Request) -> web.StreamResponse:
  file_id_in = request.match_info.get("file_id", "")
  path = await asyncio.to_thread(find_file, file_id_in)
  filename = os.path.basename(path)
  safe_filename = "".join(ch if 32 <= ord(ch) < 127 and ch not in {'"', "\\"} else "_" for ch in filename)
  mime = mimetypes.guess_type(path)[0] or "application/octet-stream"
  return web.FileResponse(
    path,
    headers={
      "Content-Type": mime,
      "Content-Disposition": f'attachment; filename="{safe_filename or "screenrecord"}"',
    },
  )


async def api_screenrecord_upload(request: web.Request) -> web.Response:
  """Upload selected screen recordings to Google Drive.

  Deliberately synchronous and per-file sequential (no zip, no job/polling):
  unlike dashcam segments (many small qcamera/rlog files bundled into one
  zip), each screen recording is already a single video file, and the
  request is expected to cover only a handful of them at a time. This trades
  away cancel support and a live progress bar for a much smaller surface
  area than dashcam's upload_jobs.py.
  """
  try:
    body = await request.json()
  except Exception:
    body = {}
  ids = body.get("ids")
  if not isinstance(ids, list):
    one = body.get("id")
    ids = [one] if one else []
  ids = [str(item).strip() for item in ids if str(item or "").strip()]
  if not ids:
    return web.json_response({"ok": False, "error": "missing ids"}, status=400)

  results: list[dict] = []
  for file_id_in in ids:
    try:
      path = await asyncio.to_thread(find_file, file_id_in)
      name = os.path.basename(path)
      drive_result = await gdrive_upload.upload_file_resumable(path, name)
      results.append({
        "id": file_id_in,
        "name": name,
        "ok": True,
        "driveFileId": drive_result.get("id"),
        "webViewLink": drive_result.get("webViewLink"),
      })
    except web.HTTPException as e:
      results.append({"id": file_id_in, "ok": False, "error": e.text or e.reason})
    except Exception as e:
      results.append({"id": file_id_in, "ok": False, "error": str(e)})

  uploaded = sum(1 for item in results if item.get("ok"))
  return web.json_response({
    "ok": uploaded == len(results),
    "uploaded": uploaded,
    "total": len(results),
    "target": "gdrive",
    "results": results,
  })


_photo_cache_lock = threading.Lock()
_photo_cache = {"time": 0.0, "photos": []}


def cached_screenrecord_photos() -> list[dict]:
  now = time.monotonic()
  with _photo_cache_lock:
    if now - float(_photo_cache.get("time") or 0.0) < VIDEO_CACHE_TTL:
      return list(_photo_cache.get("photos") or [])

  photos = build_photos()
  with _photo_cache_lock:
    _photo_cache["time"] = time.monotonic()
    _photo_cache["photos"] = photos
  return list(photos)


async def api_screenrecord_photos(request: web.Request) -> web.Response:
  try:
    offset = max(0, int(request.query.get("offset", "0") or 0))
    limit = max(1, min(200, int(request.query.get("limit", "80") or 80)))
    photos = await asyncio.to_thread(cached_screenrecord_photos)
    total = len(photos)
    end = min(offset + limit, total)
    return web.json_response({
      "ok": True,
      "photos": photos[offset:end],
      "offset": offset,
      "limit": limit,
      "total": total,
      "nextOffset": end if end < total else None,
      "hasMore": end < total,
    })
  except Exception as e:
    return web.json_response({"ok": False, "error": str(e)}, status=500)


async def api_screenrecord_photo_thumbnail(request: web.Request) -> web.StreamResponse:
  file_id_in = request.match_info.get("file_id", "")
  path = await asyncio.to_thread(photo_thumbnail_path, file_id_in)
  return web.FileResponse(path, headers={"Cache-Control": "public, max-age=86400"})


async def api_screenrecord_photo(request: web.Request) -> web.StreamResponse:
  file_id_in = request.match_info.get("file_id", "")
  path = await asyncio.to_thread(find_photo, file_id_in)
  mime = mimetypes.guess_type(path)[0] or "application/octet-stream"
  headers = {
    "Content-Type": mime,
    "Cache-Control": "private, max-age=3600",
  }
  if request.query.get("download"):
    filename = os.path.basename(path)
    safe_filename = "".join(ch if 32 <= ord(ch) < 127 and ch not in {'"', "\\"} else "_" for ch in filename)
    headers["Content-Disposition"] = f'attachment; filename="{safe_filename or "screenshot"}"'
  return web.FileResponse(path, headers=headers)


async def api_screenrecord_photo_download(request: web.Request) -> web.StreamResponse:
  file_id_in = request.match_info.get("file_id", "")
  path = await asyncio.to_thread(find_photo, file_id_in)
  filename = os.path.basename(path)
  safe_filename = "".join(ch if 32 <= ord(ch) < 127 and ch not in {'"', "\\"} else "_" for ch in filename)
  mime = mimetypes.guess_type(path)[0] or "application/octet-stream"
  return web.FileResponse(
    path,
    headers={
      "Content-Type": mime,
      "Content-Disposition": f'attachment; filename="{safe_filename or "screenshot"}"',
    },
  )


def register(app: web.Application) -> None:
  app.router.add_get("/api/screenrecord/videos", api_screenrecord_videos)
  app.router.add_get("/api/screenrecord/thumbnail/{file_id}", api_screenrecord_thumbnail)
  app.router.add_get("/api/screenrecord/video/{file_id}", api_screenrecord_video)
  app.router.add_get("/api/screenrecord/download/{file_id}", api_screenrecord_download)
  app.router.add_post("/api/screenrecord/upload", api_screenrecord_upload)
  app.router.add_get("/api/screenrecord/photos", api_screenrecord_photos)
  app.router.add_get("/api/screenrecord/photo/thumbnail/{file_id}", api_screenrecord_photo_thumbnail)
  app.router.add_get("/api/screenrecord/photo/{file_id}", api_screenrecord_photo)
  app.router.add_get("/api/screenrecord/photo/download/{file_id}", api_screenrecord_photo_download)
