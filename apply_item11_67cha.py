import sys, os

root = sys.argv[1]
CARROT = os.path.join(root, "openpilot", "selfdrive", "carrot")

def p(*parts):
    return os.path.join(CARROT, *parts)

def read(path):
    with open(path, "r", encoding="utf-8", newline="") as f:
        return f.read().replace("\r\n", "\n")

def write(path, s):
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(s)

def replace_once(content, old, new, label):
    n = content.count(old)
    if n != 1:
        print(f"[ABORT] {label}: anchor match count = {n} (expected 1)")
        sys.exit(1)
    print(f"[OK] {label}")
    return content.replace(old, new, 1)

# --- config.py ---
fp = p("server", "config.py")
c = read(fp)
c = replace_once(
    c,
    'SCREEN_RECORDING_EXTS = (".mp4", ".mkv", ".avi", ".mov", ".ts", ".hevc")\n',
    'SCREEN_RECORDING_EXTS = (".mp4", ".mkv", ".avi", ".mov", ".ts", ".hevc")\nSCREEN_RECORDING_PHOTO_EXTS = (".png", ".jpg", ".jpeg")\n',
    "config.py: SCREEN_RECORDING_PHOTO_EXTS",
)
write(fp, c)

# --- catalog.py ---
fp = p("server", "features", "screenrecord", "catalog.py")
c = read(fp)
c = replace_once(
    c,
    "from ...config import SCREEN_RECORDING_DIRS, SCREEN_RECORDING_EXTS\n",
    "from ...config import SCREEN_RECORDING_DIRS, SCREEN_RECORDING_EXTS, SCREEN_RECORDING_PHOTO_EXTS\n",
    "catalog.py: import",
)
old_tail = '''  result = run_ffmpeg(["-ss", "1", "-i", path, "-vframes", "1", "-vf", "scale=320:-1", out])
  if result.returncode != 0 or not os.path.isfile(out) or os.path.getsize(out) <= 0:
    raise web.HTTPInternalServerError(text=result.stderr or result.stdout or "screenrecord thumbnail generation failed")
  return out
'''
new_tail = old_tail + '''

def build_photos() -> list[dict[str, Any]]:
  """Onroad screen captures (.png), listed separately from video recordings.

  Mirrors build_videos()'s scan/dedupe logic against SCREEN_RECORDING_PHOTO_EXTS
  instead of sharing code with it, so video listing behavior can't regress.
  """
  photos: list[dict[str, Any]] = []
  seen: set[str] = set()
  for folder in SCREEN_RECORDING_DIRS:
    if not os.path.isdir(folder):
      continue
    try:
      with os.scandir(folder) as it:
        for entry in it:
          try:
            name = entry.name
            if not entry.is_file(follow_symlinks=False):
              continue
            if not name.lower().endswith(SCREEN_RECORDING_PHOTO_EXTS):
              continue
            stat = entry.stat(follow_symlinks=False)
            if stat.st_size <= 0:
              continue
            path = os.path.abspath(entry.path)
            real = os.path.realpath(path)
            if real in seen:
              continue
            seen.add(real)
            modified = int(stat.st_mtime)
            photos.append({
              "id": file_id(path),
              "name": name,
              "folder": folder,
              "size": int(stat.st_size),
              "modifiedEpoch": modified,
              "modifiedLabel": date_label(modified),
              "relativeModifiedLabel": relative_time(modified),
              "ext": os.path.splitext(name)[1].lower().lstrip("."),
            })
          except Exception:
            continue
    except Exception:
      continue
  photos.sort(key=lambda item: (item.get("modifiedEpoch", 0), item.get("name", "")), reverse=True)
  return photos


def find_photo(file_id_in: str) -> str:
  file_id_in = (file_id_in or "").strip()
  if not file_id_in or "/" in file_id_in or "\\\\" in file_id_in or len(file_id_in) > 64:
    raise web.HTTPBadRequest(text="bad file id")
  for item in build_photos():
    folder = str(item.get("folder") or "")
    name = str(item.get("name") or "")
    path = os.path.abspath(os.path.join(folder, name))
    if file_id(path) == file_id_in and os.path.isfile(path):
      return path
  raise web.HTTPNotFound(text="screenshot not found")


def photo_thumbnail_path(file_id_in: str) -> str:
  path = find_photo(file_id_in)
  out = cache_path("screen_photo_thumb", file_id_in, ".jpg")
  if os.path.isfile(out) and os.path.getsize(out) > 0:
    return out
  result = run_ffmpeg(["-i", path, "-vf", "scale=320:-1", out])
  if result.returncode != 0 or not os.path.isfile(out) or os.path.getsize(out) <= 0:
    raise web.HTTPInternalServerError(text=result.stderr or result.stdout or "screenshot thumbnail generation failed")
  return out
'''
n = c.count(old_tail)
if n != 1:
    print(f"[ABORT] catalog.py: append build_photos/find_photo/photo_thumbnail_path: anchor match count = {n} (expected 1)")
    sys.exit(1)
c = c.replace(old_tail, new_tail, 1)
print("[OK] catalog.py: append build_photos/find_photo/photo_thumbnail_path")
write(fp, c)

# --- routes.py ---
fp = p("server", "features", "screenrecord", "routes.py")
c = read(fp)
c = replace_once(
    c,
    "from .catalog import build_videos, find_file, thumbnail_path\n",
    "from .catalog import build_photos, build_videos, find_file, find_photo, photo_thumbnail_path, thumbnail_path\n",
    "routes.py: import",
)
old_before_register = '''  return web.FileResponse(
    path,
    headers={
      "Content-Type": mime,
      "Content-Disposition": f'attachment; filename="{safe_filename or "screenrecord"}"',
    },
  )


def register(app: web.Application) -> None:
  app.router.add_get("/api/screenrecord/videos", api_screenrecord_videos)
  app.router.add_get("/api/screenrecord/thumbnail/{file_id}", api_screenrecord_thumbnail)
  app.router.add_get("/api/screenrecord/video/{file_id}", api_screenrecord_video)
  app.router.add_get("/api/screenrecord/download/{file_id}", api_screenrecord_download)
'''
new_before_register = '''  return web.FileResponse(
    path,
    headers={
      "Content-Type": mime,
      "Content-Disposition": f'attachment; filename="{safe_filename or "screenrecord"}"',
    },
  )


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
    safe_filename = "".join(ch if 32 <= ord(ch) < 127 and ch not in {'"', "\\\\"} else "_" for ch in filename)
    headers["Content-Disposition"] = f'attachment; filename="{safe_filename or "screenshot"}"'
  return web.FileResponse(path, headers=headers)


async def api_screenrecord_photo_download(request: web.Request) -> web.StreamResponse:
  file_id_in = request.match_info.get("file_id", "")
  path = await asyncio.to_thread(find_photo, file_id_in)
  filename = os.path.basename(path)
  safe_filename = "".join(ch if 32 <= ord(ch) < 127 and ch not in {'"', "\\\\"} else "_" for ch in filename)
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
  app.router.add_get("/api/screenrecord/photos", api_screenrecord_photos)
  app.router.add_get("/api/screenrecord/photo/thumbnail/{file_id}", api_screenrecord_photo_thumbnail)
  app.router.add_get("/api/screenrecord/photo/{file_id}", api_screenrecord_photo)
  app.router.add_get("/api/screenrecord/photo/download/{file_id}", api_screenrecord_photo_download)
'''
n = c.count(old_before_register)
if n != 1:
    print(f"[ABORT] routes.py: photo routes: anchor match count = {n} (expected 1)")
    sys.exit(1)
c = c.replace(old_before_register, new_before_register, 1)
print("[OK] routes.py: photo routes")
write(fp, c)

# --- index.html ---
fp = p("web", "index.html")
c = read(fp)
c = replace_once(
    c,
    '<div id="screenrecordStatus" class="dashcam-status" hidden></div>\n          <div id="screenrecordVideos" class="screenrecord-list"></div>\n',
    '<div id="screenrecordStatus" class="dashcam-status" hidden></div>\n          <div id="screenrecordPhotosWrap" class="screenrecord-photos-wrap" hidden>\n            <div id="screenrecordPhotosTitle" class="screenrecord-photos-title"></div>\n            <div id="screenrecordPhotos" class="screenrecord-photos"></div>\n          </div>\n          <div id="screenrecordVideos" class="screenrecord-list"></div>\n',
    "index.html: photos wrap",
)
write(fp, c)

# --- translations ---
for fn, old_line, new_line in [
    ("en.js", 'screenrecord_load_failed: "Failed to load screen recordings",\n',
     'screenrecord_load_failed: "Failed to load screen recordings",\n    screenrecord_photos_title: "Photos",\n    screenrecord_photos_load_failed: "Failed to load photos",\n'),
    ("ko.js", 'screenrecord_load_failed: "화면녹화 목록 로드 실패",\n',
     'screenrecord_load_failed: "화면녹화 목록 로드 실패",\n    screenrecord_photos_title: "사진",\n    screenrecord_photos_load_failed: "사진 목록 로드 실패",\n'),
    ("zh.js", 'screenrecord_load_failed: "屏幕录制列表加载失败",\n',
     'screenrecord_load_failed: "屏幕录制列表加载失败",\n    screenrecord_photos_title: "照片",\n    screenrecord_photos_load_failed: "照片列表加载失败",\n'),
]:
    fp = p("web", "js", "translations", fn)
    c = read(fp)
    c = replace_once(c, old_line, new_line, fn)
    write(fp, c)

# --- runtime.js ---
fp = p("web", "src", "features", "logs", "runtime.js")
c = read(fp)
c = replace_once(
    c,
    '  screenrecordShouldLoadMore,\n  screenrecordState,\n} from "./screenrecord.js";\n',
    '  screenrecordShouldLoadMore,\n  screenrecordState,\n} from "./screenrecord.js";\nimport { loadScreenshots, openScreenshot } from "./screenshots.js";\n',
    "runtime.js: import",
)
c = replace_once(
    c,
    '''    if (logsActiveTab === "screen" && !screenrecordState.initialized) {
      screenrecordState.initialized = true;
      loadScreenrecordVideos().catch(() => {});
    } else if (logsActiveTab === "screen") {
      renderScreenrecordVideos();
      loadScreenrecordVideos({ silent: true }).catch(() => {});
    } else if (dashcamState.initialized) {
''',
    '''    if (logsActiveTab === "screen" && !screenrecordState.initialized) {
      screenrecordState.initialized = true;
      loadScreenrecordVideos().catch(() => {});
      loadScreenshots().catch(() => {});
    } else if (logsActiveTab === "screen") {
      renderScreenrecordVideos();
      loadScreenrecordVideos({ silent: true }).catch(() => {});
      loadScreenshots({ silent: true }).catch(() => {});
    } else if (dashcamState.initialized) {
''',
    "runtime.js: activateLogsTab",
)
c = replace_once(
    c,
    '''      } else if (actionEl.dataset.action === "play-screenrecord") {
        openScreenrecordPlayer(actionEl.dataset.id || "", actionEl.dataset.name || "");
      }
    });
  }
}

function initLogsPage() {''',
    '''      } else if (actionEl.dataset.action === "play-screenrecord") {
        openScreenrecordPlayer(actionEl.dataset.id || "", actionEl.dataset.name || "");
      }
    });
  }

  const photosHost = document.getElementById("screenrecordPhotos");
  if (photosHost && photosHost.dataset.bound !== "1") {
    photosHost.dataset.bound = "1";
    photosHost.addEventListener("click", (ev) => {
      const actionEl = ev.target?.closest?.("[data-action]");
      if (!actionEl) return;
      if (actionEl.dataset.action === "view-screenshot") {
        openScreenshot(actionEl.dataset.id || "");
      }
    });
  }
}

function initLogsPage() {''',
    "runtime.js: bindLogsPage photosHost",
)
c = replace_once(
    c,
    '''    if (!screenrecordState.initialized) {
      screenrecordState.initialized = true;
      loadScreenrecordVideos().catch(() => {});
    } else {
      renderScreenrecordVideos({ preserve: true });
      loadScreenrecordVideos({ silent: true }).catch(() => {});
    }
  } else if (!dashcamState.initialized) {''',
    '''    if (!screenrecordState.initialized) {
      screenrecordState.initialized = true;
      loadScreenrecordVideos().catch(() => {});
      loadScreenshots().catch(() => {});
    } else {
      renderScreenrecordVideos({ preserve: true });
      loadScreenrecordVideos({ silent: true }).catch(() => {});
      loadScreenshots({ silent: true }).catch(() => {});
    }
  } else if (!dashcamState.initialized) {''',
    "runtime.js: initLogsPage",
)
write(fp, c)

# --- style.css ---
fp = p("web", "src", "features", "logs", "style.css")
c = read(fp)
if c.startswith("\ufeff"):
    c = c[1:]
    print("[OK] style.css: BOM stripped")
else:
    print("[OK] style.css: no BOM present")
old_css = '''.screenrecord-download:hover {
  color: var(--md-primary);
  background: color-mix(in srgb, var(--md-primary) 10%, transparent);
}

@media (min-width: 900px) {'''
new_css = '''.screenrecord-download:hover {
  color: var(--md-primary);
  background: color-mix(in srgb, var(--md-primary) 10%, transparent);
}

.screenrecord-photos-wrap {
  flex: 0 0 auto;
  padding: 10px var(--logs-content-inline) 4px;
  border-bottom: 1px solid color-mix(in srgb, var(--md-outline-var) 40%, transparent);
}

.screenrecord-photos-wrap[hidden] {
  display: none;
}

.screenrecord-photos-title {
  font-size: 12px;
  font-weight: 750;
  color: var(--md-on-surface-var);
  margin-bottom: 8px;
}

.screenrecord-photos {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  overscroll-behavior-x: contain;
  scrollbar-width: none;
  padding-bottom: 2px;
}

.screenrecord-photos::-webkit-scrollbar {
  display: none;
}

.screenrecord-photo {
  appearance: none;
  border: 1px solid color-mix(in srgb, var(--md-outline-var) 44%, transparent);
  border-radius: 6px;
  width: 68px;
  height: 68px;
  flex: 0 0 68px;
  padding: 0;
  overflow: hidden;
  background: var(--md-surface-cont);
  cursor: pointer;
}

.screenrecord-photo:hover {
  border-color: color-mix(in srgb, var(--md-primary) 38%, var(--md-outline-var));
}

.screenrecord-photo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

@media (min-width: 900px) {'''
c = replace_once(c, old_css, new_css, "style.css: photo strip styles")
write(fp, c)

# --- screenshots.js (new file) ---
fp = p("web", "src", "features", "logs", "screenshots.js")
screenshots_js = '''"use strict";

import { hydrateLogsLazyImages, isLogsPageActive, unobserveLogsLazyImages } from "./runtime.js";

// Logs page — Screen Recording tab, "Photos" strip.
//
// The onroad capture button (openpilot/selfdrive/ui/onroad/screenshot_capture.py)
// saves PNG screenshots into the same folders as video recordings, but
// server/features/screenrecord/catalog.py's video listing only recognizes
// video extensions, so screenshots never showed up anywhere in the UI.
// Rather than folding photos into the video list's virtualized rendering
// (screenrecord.js), this renders them as their own small non-virtualized
// horizontal strip: photo counts are expected to stay far smaller than video
// counts, so the extra complexity of windowing isn't worth it here.

const SCREENSHOTS_PAGE_SIZE = 60;

const screenshotsState = {
  initialized: false,
  loading: false,
  photos: [],
  signature: "",
};

function screenshotApiPath(kind, fileId) {
  const id = encodeURIComponent(fileId || "");
  return kind === "raw" ? `/api/screenrecord/photo/${id}` : `/api/screenrecord/photo/${kind}/${id}`;
}

function screenshotsSignature(photos) {
  return (photos || []).map((photo) => [
    photo.id || "",
    photo.name || "",
    photo.modifiedLabel || "",
    photo.size || 0,
  ].join("|")).join("\\n");
}

function screenshotRowHtml(photo) {
  const id = escapeHtml(photo.id || "");
  const name = escapeHtml(photo.name || "-");
  return `<button type="button" class="screenrecord-photo" data-action="view-screenshot" data-id="${id}" data-name="${name}" title="${name}">
    <img class="logs-lazy-img" loading="lazy" decoding="async" fetchpriority="low" data-src="${screenshotApiPath("thumbnail", photo.id || "")}" alt="">
  </button>`;
}

function renderScreenshots() {
  const wrap = document.getElementById("screenrecordPhotosWrap");
  const host = document.getElementById("screenrecordPhotos");
  const title = document.getElementById("screenrecordPhotosTitle");
  if (!wrap || !host) return;
  if (!isLogsPageActive()) return;
  if (title) title.textContent = getUIText("screenrecord_photos_title") || "Photos";
  const photos = screenshotsState.photos || [];
  if (!photos.length) {
    wrap.hidden = true;
    host.innerHTML = "";
    host.dataset.signature = "";
    return;
  }
  const nextSignature = screenshotsSignature(photos);
  if (host.dataset.signature === nextSignature) {
    wrap.hidden = false;
    hydrateLogsLazyImages(host);
    return;
  }
  unobserveLogsLazyImages(host);
  host.innerHTML = photos.map(screenshotRowHtml).join("");
  host.dataset.signature = nextSignature;
  wrap.hidden = false;
  hydrateLogsLazyImages(host);
}

async function loadScreenshots({ silent = false } = {}) {
  if (screenshotsState.loading) return;
  screenshotsState.loading = true;
  try {
    const json = await getJson(`/api/screenrecord/photos?offset=0&limit=${SCREENSHOTS_PAGE_SIZE}`);
    screenshotsState.loading = false;
    if (!isLogsPageActive()) return;
    const photos = Array.isArray(json.photos) ? json.photos : [];
    const nextSignature = screenshotsSignature(photos);
    if (silent && nextSignature === screenshotsState.signature) return;
    screenshotsState.photos = photos;
    screenshotsState.signature = nextSignature;
    renderScreenshots();
  } catch (e) {
    screenshotsState.loading = false;
    if (!silent && isLogsPageActive()) {
      showAppToast(e.message || getUIText("screenrecord_photos_load_failed", "Failed to load photos"), { tone: "error" });
    }
  }
}

function openScreenshot(id) {
  if (!id) return;
  window.open(screenshotApiPath("raw", id), "_blank", "noopener");
}

export {
  loadScreenshots,
  openScreenshot,
  renderScreenshots,
  screenshotApiPath,
  screenshotsState,
};
'''
write(fp, screenshots_js)
print("[OK] screenshots.js created")

print("ALL DONE")
