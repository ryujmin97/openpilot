"""
Google Drive 연동 — 로그탭 "전송" 버튼 + tmux 진단 전송(carrot/toss 선택 전송)의
공통 업로드 백엔드.

c3-ms-dev 브랜치의 server/gdrive.py(OAuth2 Device Authorization Grant, 511줄,
로컬 검증됨)를 기반으로 이식했으며, carrot-ryu에서는 다음 두 곳을 대체한다.
  1. server/features/dashcam/upload_jobs.py의 run_upload_segments()
     (기존 Carrot/Toss HTTP 업로드 대체)
  2. carrot_man.py의 send_tmux_web()
     (기존 carrot/toss 선택 전송 대체. send_tmux_carrot_logs()는 Discord
     carrot_logs 포럼용 별도 고정 전송이라 이번 변경과 무관 — 그대로 둔다)

c3-ms-dev 원본과 다른 점 (사용자 지정):
  - 폴더를 매번 이름으로 검색/자동생성하지 않고, 고정 폴더 ID
    (DRIVE_FOLDER_ID)로 바로 사용한다. drive.file(최소 권한) 스코프로는
    앱이 만들지 않은 기존 폴더에 ID로 접근할 수 없으므로, 스코프를
    drive(전체 권한)로 확대했다.
  - _ensure_folder() 대신 _verify_folder()로, 해당 ID가 (a) 존재하고
    (b) 휴지통에 있지 않고 (c) 실제로 폴더 타입인지만 확인한다(폴더를
    새로 만들지 않음 — 사용자가 이미 만들어둔 폴더를 그대로 씀).

핵심 설계(c3-ms-dev와 동일):
  1. OAuth2 Device Authorization Grant — 콤마 기기 자체 브라우저 없이도
     폰/PC에서 코드를 입력해 인증. refresh_token은 Params에 영구 저장하여
     carrotweb 재시작/기기 재부팅 후에도 재인증 불필요.
  2. 업로드는 uploadType=resumable, 8MB 청크 PUT.
     - multipart는 요청 본문 5MB 제한이 있어 대용량 파일(대시캠 zip 등)에서
       "Malformed multipart body." 400을 유발함(c3-ms-dev에서 실제 관찰).
     - 파일을 메모리에 통째로 읽지 않고 청크 단위로만 읽어 올려 OOM 방지.
  3. 업로드는 시간이 걸릴 수 있어 job 방식 비동기 처리 — 요청은 즉시
     job_id를 반환하고, 프론트는 폴링으로 진행률(%)을 받는다.

필요 사전 준비 (Google Cloud Console에서 1회 설정, c3-ms-dev와 동일):
  1. https://console.cloud.google.com/ 에서 프로젝트 생성
  2. "API 및 서비스 > 라이브러리"에서 Google Drive API 활성화
  3. "API 및 서비스 > 사용자 인증 정보 > OAuth 클라이언트 ID 만들기"
     -> 애플리케이션 유형: "TV 및 제한된 입력이 있는 기기" (필수!)
  4. 발급된 클라이언트 ID / 클라이언트 보안 비밀번호를 로그탭 설정에 입력
  5. 이 파일의 DRIVE_FOLDER_ID가 가리키는 폴더에 대해, 인증에 사용할
     구글 계정이 최소 "편집자" 권한을 갖고 있어야 함
"""

import os
import time
import uuid
from collections.abc import Callable
from typing import Any

import aiohttp
from aiohttp import web

try:
  from openpilot.common.params import Params as _Params
  HAS_PARAMS = True
except Exception:
  _Params = None
  HAS_PARAMS = False

DEVICE_CODE_URL = "https://oauth2.googleapis.com/device/code"
TOKEN_URL = "https://oauth2.googleapis.com/token"
DRIVE_FILES_URL = "https://www.googleapis.com/drive/v3/files"
DRIVE_UPLOAD_URL = "https://www.googleapis.com/upload/drive/v3/files"

DRIVE_SCOPE = "https://www.googleapis.com/auth/drive"
DRIVE_FOLDER_ID = "1Sb5nxF5wknwM9CbJFbXQPY1OIEB_bL9t"

PARAM_CLIENT_ID = "CarrotGDriveClientId"
PARAM_CLIENT_SECRET = "CarrotGDriveClientSecret"
PARAM_REFRESH_TOKEN = "CarrotGDriveRefreshToken"

_pending_flow: dict[str, Any] = {}
_access_token_cache: dict[str, Any] = {"token": None, "expires_at": 0}
_folder_verified_cache: dict[str, Any] = {"ok": False, "checked_at": 0}
_last_error: dict[str, str] = {"message": ""}


def _params():
  if not HAS_PARAMS:
    raise RuntimeError("openpilot Params 모듈을 사용할 수 없습니다")
  return _Params()


def _param_str(key: str) -> str:
  try:
    v = _params().get(key)
  except Exception:
    return ""
  if v is None:
    return ""
  if isinstance(v, bytes):
    return v.decode("utf-8", errors="ignore")
  return str(v)


def get_client_credentials() -> tuple[str, str]:
  return _param_str(PARAM_CLIENT_ID), _param_str(PARAM_CLIENT_SECRET)


def is_connected() -> bool:
  return bool(_param_str(PARAM_REFRESH_TOKEN))


def disconnect() -> None:
  try:
    _params().put(PARAM_REFRESH_TOKEN, "")
  except Exception:
    pass
  _access_token_cache["token"] = None
  _access_token_cache["expires_at"] = 0
  _folder_verified_cache["ok"] = False
  _folder_verified_cache["checked_at"] = 0


async def _read_json_safe(resp: aiohttp.ClientResponse) -> dict[str, Any]:
  try:
    return await resp.json(content_type=None)
  except Exception:
    text = (await resp.text())[:500]
    raise RuntimeError(f"HTTP {resp.status}: {text or '(empty body)'}") from None


async def api_gdrive_status(request: web.Request) -> web.Response:
  client_id, client_secret = get_client_credentials()
  connected = is_connected()
  pending = bool(_pending_flow.get("device_code")) and not connected
  status = "connected" if connected else ("pending" if pending else ("error" if _last_error["message"] else "disconnected"))
  return web.json_response({
    "ok": True,
    "connected": connected,
    "status": status,
    "hasCredentials": bool(client_id and client_secret),
    "user_code": _pending_flow.get("user_code", ""),
    "verification_uri": _pending_flow.get("verification_uri", ""),
    "folder_id": DRIVE_FOLDER_ID,
    "last_error": _last_error["message"],
  })


async def api_gdrive_device(request: web.Request) -> web.Response:
  try:
    body = await request.json()
  except Exception:
    body = {}
  client_id = str(body.get("client_id") or "").strip()
  client_secret = str(body.get("client_secret") or "").strip()
  if not client_id:
    return web.json_response({"ok": False, "error": "missing client_id"}, status=400)

  try:
    _params().put(PARAM_CLIENT_ID, client_id)
    _params().put(PARAM_CLIENT_SECRET, client_secret)
  except Exception as e:
    return web.json_response({"ok": False, "error": str(e)}, status=500)

  try:
    async with aiohttp.ClientSession() as session:
      async with session.post(DEVICE_CODE_URL, data={
        "client_id": client_id,
        "scope": DRIVE_SCOPE,
      }) as resp:
        data = await _read_json_safe(resp)
        if resp.status != 200:
          _last_error["message"] = data.get("error_description", str(data))
          return web.json_response({"ok": False, "error": _last_error["message"]}, status=400)
  except Exception as e:
    _last_error["message"] = str(e)
    return web.json_response({"ok": False, "error": str(e)}, status=500)

  _pending_flow.clear()
  _pending_flow.update({
    "device_code": data.get("device_code"),
    "user_code": data.get("user_code", ""),
    "verification_uri": data.get("verification_url") or data.get("verification_uri") or "https://www.google.com/device",
    "interval": int(data.get("interval") or 5),
    "expires_at": time.monotonic() + float(data.get("expires_in", 1800)),
  })
  _last_error["message"] = ""

  return web.json_response({
    "ok": True,
    "device_code": _pending_flow["device_code"],
    "user_code": _pending_flow["user_code"],
    "verification_uri": _pending_flow["verification_uri"],
    "interval": _pending_flow["interval"],
    "status": "pending",
  })


async def api_gdrive_token(request: web.Request) -> web.Response:
  try:
    body = await request.json()
  except Exception:
    body = {}

  saved_client_id, saved_client_secret = get_client_credentials()
  client_id = str(body.get("client_id") or saved_client_id or "").strip()
  client_secret = str(body.get("client_secret") or saved_client_secret or "").strip()
  device_code = str(body.get("device_code") or _pending_flow.get("device_code") or "").strip()
  if not client_id or not device_code:
    return web.json_response({"ok": False, "error": "missing client_id or device_code"}, status=400)

  if _pending_flow.get("expires_at") and time.monotonic() > _pending_flow["expires_at"]:
    _pending_flow.clear()
    _last_error["message"] = "인증 코드가 만료되었습니다. 다시 시도해주세요."
    return web.json_response({"ok": False, "error": _last_error["message"], "expired": True}, status=400)

  try:
    async with aiohttp.ClientSession() as session:
      async with session.post(TOKEN_URL, data={
        "client_id": client_id,
        "client_secret": client_secret,
        "device_code": device_code,
        "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
      }) as resp:
        data = await _read_json_safe(resp)
  except Exception as e:
    _last_error["message"] = str(e)
    return web.json_response({"ok": False, "error": str(e)}, status=500)

  error = data.get("error")
  if error in ("authorization_pending", "slow_down"):
    return web.json_response({"ok": True, "connected": False, "pending": True, "status": "pending"})
  if error:
    _pending_flow.clear()
    _last_error["message"] = data.get("error_description", error)
    return web.json_response({"ok": False, "error": _last_error["message"]}, status=400)

  access_token = str(data.get("access_token") or "")
  refresh_token = str(data.get("refresh_token") or "")
  expires_in = int(data.get("expires_in") or 3600)
  if not access_token:
    return web.json_response({"ok": False, "error": "access_token 없음"}, status=500)

  if refresh_token:
    try:
      _params().put(PARAM_REFRESH_TOKEN, refresh_token)
    except Exception as e:
      _last_error["message"] = str(e)
      return web.json_response({"ok": False, "error": str(e)}, status=500)

  _access_token_cache["token"] = access_token
  _access_token_cache["expires_at"] = time.monotonic() + float(expires_in) - 60
  _pending_flow.clear()
  _last_error["message"] = ""

  return web.json_response({
    "ok": True,
    "connected": True,
    "pending": False,
    "status": "connected",
    "message": "Google Drive 연결 완료",
  })


async def api_gdrive_disconnect(request: web.Request) -> web.Response:
  disconnect()
  return web.json_response({"ok": True, "connected": False})


_HANDSHAKE_TIMEOUT = aiohttp.ClientTimeout(total=20, sock_connect=10, sock_read=15)


async def _get_access_token(session: aiohttp.ClientSession) -> str:
  now = time.monotonic()
  if _access_token_cache["token"] and now < _access_token_cache["expires_at"]:
    return _access_token_cache["token"]

  client_id, client_secret = get_client_credentials()
  refresh_token = _param_str(PARAM_REFRESH_TOKEN)
  if not (client_id and refresh_token):
    raise RuntimeError("Google Drive가 연결되어 있지 않습니다")

  async with session.post(TOKEN_URL, data={
    "client_id": client_id,
    "client_secret": client_secret,
    "refresh_token": refresh_token,
    "grant_type": "refresh_token",
  }, timeout=_HANDSHAKE_TIMEOUT) as resp:
    data = await _read_json_safe(resp)
    if resp.status != 200:
      raise RuntimeError(data.get("error_description", str(data)))

  token = data["access_token"]
  _access_token_cache["token"] = token
  _access_token_cache["expires_at"] = now + float(data.get("expires_in", 3600)) - 60
  return token


async def _verify_folder(session: aiohttp.ClientSession, token: str) -> str:
  cache_age = time.monotonic() - float(_folder_verified_cache.get("checked_at") or 0)
  if _folder_verified_cache.get("ok") and cache_age < 300:
    return DRIVE_FOLDER_ID

  headers = {"Authorization": f"Bearer {token}"}
  async with session.get(
    f"{DRIVE_FILES_URL}/{DRIVE_FOLDER_ID}",
    headers=headers,
    params={"fields": "id,name,mimeType,trashed"},
    timeout=_HANDSHAKE_TIMEOUT,
  ) as resp:
    if resp.status == 404:
      raise RuntimeError(f"대상 폴더를 찾을 수 없습니다 (id={DRIVE_FOLDER_ID}). 폴더 ID 또는 계정 권한을 확인하세요")
    data = await _read_json_safe(resp)
    if resp.status != 200:
      raise RuntimeError(data.get("error", {}).get("message", str(data)))

  if data.get("trashed"):
    raise RuntimeError("대상 폴더가 휴지통에 있습니다")
  if data.get("mimeType") != "application/vnd.google-apps.folder":
    raise RuntimeError("대상 ID가 폴더가 아닙니다")

  _folder_verified_cache["ok"] = True
  _folder_verified_cache["checked_at"] = time.monotonic()
  return DRIVE_FOLDER_ID


async def test_connection() -> dict[str, Any]:
  """연결 테스트 버튼(api_dashcam_upload_test)용. is_connected()는 refresh_token
  존재 여부만 보므로, 여기서는 실제로 access_token 갱신 + 대상 폴더 조회까지
  왕복해 Drive 연동이 실제로 동작하는지 확인한다."""
  if not is_connected():
    return {"ok": False, "connected": False, "error": "Google Drive가 연결되어 있지 않습니다"}
  try:
    async with aiohttp.ClientSession() as session:
      token = await _get_access_token(session)
      folder_id = await _verify_folder(session, token)
    return {"ok": True, "connected": True, "folder_id": folder_id}
  except Exception as e:
    return {"ok": False, "connected": True, "error": str(e)}


UPLOAD_JOB_KEEP_COUNT = 12
_upload_jobs: dict[str, dict[str, Any]] = {}


def create_job() -> dict[str, Any]:
  job_id = uuid.uuid4().hex[:12]
  job: dict[str, Any] = {
    "id": job_id,
    "status": "running",
    "message": "준비 중...",
    "sent": 0,
    "total": 0,
    "percent": 0,
    "error": None,
    "result": None,
    "created_at": time.time(),
    "updated_at": time.time(),
  }
  _upload_jobs[job_id] = job
  _prune_jobs()
  return job


def get_job(job_id: str) -> dict[str, Any] | None:
  return _upload_jobs.get(job_id)


def job_snapshot(job: dict[str, Any]) -> dict[str, Any]:
  return {
    "ok": True,
    "id": job["id"],
    "status": job["status"],
    "done": job["status"] in ("done", "failed"),
    "message": job.get("message") or "",
    "sent": job.get("sent"),
    "total": job.get("total"),
    "percent": job.get("percent"),
    "error": job.get("error"),
    "result": job.get("result"),
  }


def _touch_job(job: dict[str, Any]) -> None:
  job["updated_at"] = time.time()


def set_job_message(job: dict[str, Any] | None, message: str) -> None:
  if not job:
    return
  job["message"] = message
  _touch_job(job)


def _set_job_progress(job: dict[str, Any] | None, sent: int, total: int, message: str | None = None) -> None:
  if not job:
    return
  job["sent"] = sent
  job["total"] = total
  job["percent"] = int(max(0, min(100, round(sent / total * 100)))) if total else 0
  if message is not None:
    job["message"] = message
  _touch_job(job)


def finish_job(job: dict[str, Any] | None, *, ok: bool, result: dict[str, Any] | None = None, error: str | None = None) -> None:
  if not job:
    return
  job["status"] = "done" if ok else "failed"
  job["result"] = result
  job["error"] = error
  if ok:
    job["percent"] = 100
    job["message"] = "완료"
  _touch_job(job)
  _prune_jobs()


def _prune_jobs() -> None:
  finished = [j for j in _upload_jobs.values() if j.get("status") in ("done", "failed")]
  if len(finished) <= UPLOAD_JOB_KEEP_COUNT:
    return
  finished.sort(key=lambda j: float(j.get("updated_at") or 0), reverse=True)
  for old in finished[UPLOAD_JOB_KEEP_COUNT:]:
    _upload_jobs.pop(old["id"], None)


async def api_gdrive_job(request: web.Request) -> web.Response:
  job_id = (request.query.get("id") or "").strip()
  if not job_id:
    return web.json_response({"ok": False, "error": "missing job id"}, status=400)
  job = get_job(job_id)
  if not job:
    return web.json_response({"ok": False, "error": "job not found"}, status=404)
  return web.json_response(job_snapshot(job))


_UPLOAD_TIMEOUT = aiohttp.ClientTimeout(total=1800, sock_connect=30, sock_read=300)
UPLOAD_CHUNK_SIZE = 8 * 1024 * 1024


async def upload_file_resumable(
  file_path: str,
  filename: str,
  job: dict[str, Any] | None = None,
  progress_cb: Callable[[int, int], None] | None = None,
) -> dict[str, Any]:
  """업로드. `job`은 이 모듈 자체의 job 레지스트리(create_job/get_job, /api/gdrive/job

  폴링용)에 진행률을 기록하고 싶을 때만 넘긴다. `progress_cb(sent, total)`은 호출자가
  자체 진행률/취소 체계(예: dashcam upload_jobs.py)를 갖고 있을 때 그쪽으로 바이트
  단위 진행률을 전달하기 위한 것으로, 두 방식은 상호 배타적이지 않고 함께 쓸 수 있다.
  진행률 콜백에서 예외를 던지면(예: 취소 요청 감지) 그대로 전파되어 업로드가 중단된다.
  """
  if not os.path.isfile(file_path):
    raise FileNotFoundError(file_path)
  size = os.path.getsize(file_path)
  set_job_message(job, "Google Drive 연결 확인 중...")
  if progress_cb:
    progress_cb(0, size)
  try:
    async with aiohttp.ClientSession(timeout=_UPLOAD_TIMEOUT) as session:
      token = await _get_access_token(session)
      folder_id = await _verify_folder(session, token)

      set_job_message(job, "업로드 세션 여는 중...")
      metadata = {"name": filename, "parents": [folder_id]}
      async with session.post(
        DRIVE_UPLOAD_URL,
        params={"uploadType": "resumable", "fields": "id,name,webViewLink,size"},
        headers={
          "Authorization": f"Bearer {token}",
          "Content-Type": "application/json; charset=UTF-8",
          "X-Upload-Content-Length": str(size),
        },
        json=metadata,
        timeout=_HANDSHAKE_TIMEOUT,
      ) as resp:
        if resp.status not in (200, 201):
          data = await _read_json_safe(resp)
          raise RuntimeError(data.get("error", {}).get("message", str(data)))
        session_uri = resp.headers.get("Location")
        if not session_uri:
          raise RuntimeError("업로드 세션 URI를 받지 못했습니다")

      _set_job_progress(job, 0, size, "업로드 중...")
      sent = 0
      with open(file_path, "rb") as fh:
        while sent < size:
          chunk = fh.read(UPLOAD_CHUNK_SIZE)
          if not chunk:
            break
          chunk_len = len(chunk)
          end = sent + chunk_len - 1
          async with session.put(
            session_uri,
            data=chunk,
            headers={
              "Content-Length": str(chunk_len),
              "Content-Range": f"bytes {sent}-{end}/{size}",
            },
          ) as resp:
            if resp.status in (200, 201):
              result = await _read_json_safe(resp)
              sent += chunk_len
              _set_job_progress(job, sent, size, "업로드 완료 처리 중...")
              if progress_cb:
                progress_cb(sent, size)
              return result
            if resp.status == 308:
              sent += chunk_len
              _set_job_progress(job, sent, size)
              if progress_cb:
                progress_cb(sent, size)
              continue
            text = (await resp.text())[:400]
            raise RuntimeError(f"업로드 청크 실패(HTTP {resp.status}): {text or '(empty body)'}")
      raise RuntimeError("업로드가 완료되지 않았습니다(응답 없음)")
  except (TimeoutError, aiohttp.ClientError) as e:
    msg = str(e) or type(e).__name__
    raise RuntimeError(f"Drive 업로드 실패(네트워크/타임아웃): {msg}") from None


def register(app: web.Application) -> None:
  app.router.add_get("/api/gdrive/status", api_gdrive_status)
  app.router.add_post("/api/gdrive/device", api_gdrive_device)
  app.router.add_post("/api/gdrive/token", api_gdrive_token)
  app.router.add_post("/api/gdrive/disconnect", api_gdrive_disconnect)
  app.router.add_get("/api/gdrive/job", api_gdrive_job)