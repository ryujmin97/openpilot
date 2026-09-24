from __future__ import annotations

import asyncio
import os
import shutil
import tempfile
import time
import uuid
import zipfile
from collections import deque
from datetime import datetime
from typing import Any

from openpilot.selfdrive.carrot import gdrive_upload
from openpilot.selfdrive.carrot.web_upload import upload_device_id

from ...config import DASHCAM_UPLOAD_TMP_DIR
from ...services.params import HAS_PARAMS, Params
from . import upload
from .catalog import segment_file_summary
from .paths import route_name, segment_dir, segment_index


UPLOAD_JOB_KEEP_COUNT = 12
UPLOAD_JOB_MAX_LOG_CHARS = 60000
UPLOAD_JOB_STALE_SECONDS = 30 * 60
UPLOAD_PHASE_QUEUED = "queued"
UPLOAD_PHASE_PREPARING = "preparing"
UPLOAD_PHASE_UPLOADING = "uploading"
UPLOAD_PHASE_NOTIFYING = "notifying"
UPLOAD_PHASE_CANCELING = "canceling"
UPLOAD_PHASE_COMPLETE = "complete"
UPLOAD_PHASE_CANCELED = "canceled"
UPLOAD_PHASE_FAILED = "failed"
UPLOAD_PREPARING_END_PERCENT = 8
UPLOAD_TRANSFERRING_END_PERCENT = 97
UPLOAD_NOTIFYING_START_PERCENT = 98
UPLOAD_NOTIFYING_END_PERCENT = 99
UPLOAD_PHASES = frozenset({
  UPLOAD_PHASE_QUEUED,
  UPLOAD_PHASE_PREPARING,
  UPLOAD_PHASE_UPLOADING,
  UPLOAD_PHASE_NOTIFYING,
  UPLOAD_PHASE_CANCELING,
  UPLOAD_PHASE_COMPLETE,
  UPLOAD_PHASE_CANCELED,
  UPLOAD_PHASE_FAILED,
})
_jobs: dict[str, dict[str, Any]] = {}


class UploadCanceled(Exception):
  pass


def jobs() -> dict[str, dict[str, Any]]:
  return _jobs


def running_job() -> dict[str, Any] | None:
  expire_stale_jobs()
  for job in _jobs.values():
    if job.get("status") == "running":
      return job
  return None


def touch(job: dict[str, Any]) -> None:
  job["updated_at"] = time.time()  # noqa: TID251
  job["_activity_at"] = time.monotonic()


def append(job: dict[str, Any], text: Any) -> None:
  if text is None:
    return
  chunk = str(text).replace("\r\n", "\n").replace("\r", "\n")
  if not chunk:
    return
  cur = job.get("log") or ""
  if cur and not cur.endswith("\n") and not chunk.startswith("\n"):
    cur += "\n"
  job["log"] = (cur + chunk)[-UPLOAD_JOB_MAX_LOG_CHARS:]
  touch(job)


def progress(
  job: dict[str, Any],
  *,
  message: str | None = None,
  current: int | None = None,
  total: int | None = None,
  percent: int | None = None,
  phase: str | None = None,
  phase_current: int | None = None,
  phase_total: int | None = None,
  bytes_current: int | None = None,
  bytes_total: int | None = None,
  bytes_per_second: int | None = None,
) -> None:
  changed = False
  if message is not None:
    normalized_message = str(message)
    changed = changed or job.get("message") != normalized_message
    job["message"] = normalized_message
  if phase is not None:
    normalized_phase = str(phase).strip().lower()
    if normalized_phase not in UPLOAD_PHASES:
      raise ValueError(f"unsupported upload phase: {phase}")
    changed = changed or job.get("phase") != normalized_phase
    job["phase"] = normalized_phase
  if current is not None:
    normalized_current = max(0, int(current))
    changed = changed or job.get("step_current") != normalized_current
    job["step_current"] = normalized_current
  if total is not None:
    normalized_total = max(0, int(total))
    changed = changed or job.get("step_total") != normalized_total
    job["step_total"] = normalized_total
  if phase_current is not None:
    normalized_phase_current = max(0, int(phase_current))
    changed = changed or job.get("phase_current") != normalized_phase_current
    job["phase_current"] = normalized_phase_current
  if phase_total is not None:
    normalized_phase_total = max(0, int(phase_total))
    changed = changed or job.get("phase_total") != normalized_phase_total
    job["phase_total"] = normalized_phase_total
  if bytes_current is not None:
    normalized_bytes_current = max(0, int(bytes_current))
    changed = changed or job.get("bytes_current") != normalized_bytes_current
    job["bytes_current"] = normalized_bytes_current
  if bytes_total is not None:
    normalized_bytes_total = max(0, int(bytes_total))
    changed = changed or job.get("bytes_total") != normalized_bytes_total
    job["bytes_total"] = normalized_bytes_total
  if bytes_per_second is not None:
    normalized_bytes_per_second = max(0, int(bytes_per_second))
    changed = changed or job.get("bytes_per_second") != normalized_bytes_per_second
    job["bytes_per_second"] = normalized_bytes_per_second
  if percent is None:
    percent = job.get("progress")
  if percent is not None:
    normalized_percent = int(max(0, min(100, round(float(percent)))))
    previous_percent = job.get("progress")
    if isinstance(previous_percent, (int, float)) and job.get("status") == "running":
      normalized_percent = max(int(previous_percent), normalized_percent)
    changed = changed or previous_percent != normalized_percent
    job["progress"] = normalized_percent
  if changed:
    job["revision"] = max(0, int(job.get("revision") or 0)) + 1
  touch(job)


def is_cancel_requested(job: dict[str, Any] | None) -> bool:
  return bool(job and job.get("cancel_requested"))


def ensure_not_canceled(job: dict[str, Any] | None) -> None:
  if is_cancel_requested(job):
    raise UploadCanceled("upload canceled")


def cancel_job(job_id: str) -> dict[str, Any]:
  job = _jobs.get(job_id)
  if not job:
    return {"ok": False, "error": "job not found"}
  if job.get("status") in ("done", "failed", "canceled"):
    return {"ok": True, "already_done": True, **snapshot(job)}
  job["cancel_requested"] = True
  progress(job, message="Canceling upload", phase=UPLOAD_PHASE_CANCELING)
  append(job, "Cancel requested")
  return {"ok": True, **snapshot(job)}


def snapshot(job: dict[str, Any]) -> dict[str, Any]:
  return {
    "ok": True,
    "id": job["id"],
    "action": job["action"],
    "status": job["status"],
    "done": job["status"] in ("done", "failed", "canceled"),
    "cancel_requested": bool(job.get("cancel_requested")),
    "log": job.get("log") or "",
    "progress": job.get("progress"),
    "revision": max(0, int(job.get("revision") or 0)),
    "phase": job.get("phase") or UPLOAD_PHASE_QUEUED,
    "message": job.get("message") or "",
    "step_current": job.get("step_current"),
    "step_total": job.get("step_total"),
    "phase_current": job.get("phase_current"),
    "phase_total": job.get("phase_total"),
    "bytes_current": job.get("bytes_current"),
    "bytes_total": job.get("bytes_total"),
    "bytes_per_second": job.get("bytes_per_second"),
    "error": job.get("error"),
    "created_at": job.get("created_at"),
    "updated_at": job.get("updated_at"),
    "result": job.get("result"),
  }


def finish(
  job: dict[str, Any],
  *,
  ok: bool,
  result: dict[str, Any] | None = None,
  error: str | None = None,
  status: str | None = None,
) -> None:
  final_status = status or ("done" if ok else "failed")
  job["status"] = final_status
  job["phase"] = (
    UPLOAD_PHASE_CANCELED
    if final_status == "canceled"
    else UPLOAD_PHASE_COMPLETE
    if ok
    else UPLOAD_PHASE_FAILED
  )
  job["result"] = result or {"ok": bool(ok)}
  job["error"] = error or (None if ok else job["result"].get("error"))
  if ok:
    job["progress"] = 100
    job["phase_current"] = 1
    job["phase_total"] = 1
  job["revision"] = max(0, int(job.get("revision") or 0)) + 1
  touch(job)
  prune()


def fail_running_job(job: dict[str, Any], error: str) -> None:
  if job.get("status") != "running":
    return
  results = list(job.get("partial_results") or [])
  uploaded = sum(1 for item in results if item.get("ok"))
  total = len(job.get("segments") or [])
  result = {
    "ok": False,
    "error": error,
    "uploaded": uploaded,
    "total": total,
    "results": results,
    "message": f"Upload failed: {error}",
  }
  append(job, f"FAILED: {error}")
  finish(job, ok=False, result=result, error=error)


def expire_stale_jobs(now: float | None = None) -> None:
  current = time.monotonic() if now is None else float(now)
  for job in list(_jobs.values()):
    if job.get("status") != "running":
      continue
    task = job.get("_task")
    task_done = task is not None and task.done()
    activity_at = float(job.get("_activity_at") or current)
    inactive = current - activity_at >= UPLOAD_JOB_STALE_SECONDS
    if not task_done and not inactive:
      continue
    if task is not None and not task.done():
      task.cancel()
    stale_minutes = max(1, round(UPLOAD_JOB_STALE_SECONDS / 60))
    reason = (
      "upload task ended without a final state"
      if task_done
      else f"upload job expired after {stale_minutes} minutes without activity"
    )
    fail_running_job(job, reason)


def prune() -> None:
  finished = [job for job in _jobs.values() if job.get("status") in ("done", "failed", "canceled")]
  if len(finished) <= UPLOAD_JOB_KEEP_COUNT:
    return
  finished.sort(key=lambda job: float(job.get("updated_at") or 0), reverse=True)
  for old in finished[UPLOAD_JOB_KEEP_COUNT:]:
    _jobs.pop(old["id"], None)


def create_job(segments: list[str]) -> dict[str, Any]:
  job_id = uuid.uuid4().hex[:12]
  now = time.time()  # noqa: TID251
  job = {
    "id": job_id,
    "action": "dashcam_upload",
    "segments": list(segments),
    "status": "running",
    "log": "",
    "progress": 0,
    "revision": 0,
    "phase": UPLOAD_PHASE_QUEUED,
    "message": "",
    "step_current": 0,
    "step_total": len(segments),
    "phase_current": 0,
    "phase_total": len(segments),
    "bytes_current": 0,
    "bytes_total": 0,
    "bytes_per_second": 0,
    "error": None,
    "result": None,
    "cancel_requested": False,
    "created_at": now,
    "updated_at": now,
    "_activity_at": time.monotonic(),
  }
  _jobs[job_id] = job
  prune()
  return job


def start_job(job: dict[str, Any]) -> asyncio.Task:
  task = asyncio.create_task(run_job(job))
  job["_task"] = task

  def finalize_task(done_task: asyncio.Task) -> None:
    if job.get("_task") is done_task:
      job.pop("_task", None)
    if job.get("status") != "running":
      return
    if done_task.cancelled():
      error = "upload task canceled before completion"
    else:
      exception = done_task.exception()
      error = str(exception) if exception else "upload task ended without a final state"
    fail_running_job(job, error)

  task.add_done_callback(finalize_task)
  return task


async def run_upload_segments(segments: list[str], job: dict[str, Any] | None = None) -> dict[str, Any]:
  """세그먼트(들)를 zip으로 압축해 Google Drive에 업로드한다.

  [15차->16차 전환] 기존에는 세그먼트마다, 파일마다 개별 HTTP PUT으로
  Carrot/Toss 서버에 올리고(`upload_folder_to_web`) 완료 후 `/complete`를
  통지했다. 이제는 선택된 세그먼트들의 대상 파일(qcamera/rlog)을 하나의 zip으로
  묶어 `gdrive_upload.upload_file_resumable()`로 단일 파일 업로드한다.

  이 때문에 성공/실패 단위가 "세그먼트별"에서 "zip 전체"로 바뀐다: zip 안에
  포함된 세그먼트는 업로드 성공 시 모두 ok=True, 압축 준비 단계에서 이미
  실패한 세그먼트(파일 접근 오류 등)만 ok=False로 표시된다. 업로드 자체가
  중간에 실패/취소되면 zip에 포함됐던 세그먼트 전부가 실패로 처리된다
  (부분 업로드가 Drive에 남지 않으므로 실제 상태와 일치).
  """
  params = Params() if HAS_PARAMS else None

  if not gdrive_upload.is_connected():
    raise RuntimeError("Google Drive가 연결되어 있지 않습니다. 로그탭 설정에서 Drive를 먼저 연결하세요.")

  meta = upload.upload_metadata(params)
  device_id = upload_device_id(meta)
  car_selected = meta.get("carName") or "none"
  storage_label = f"{car_selected}_{device_id}".strip().replace(" ", "_") or "unknown"

  total = len(segments)
  if job:
    job["upload_target"] = "gdrive"
    job["partial_results"] = []
    progress(
      job,
      message="Preparing upload",
      current=0,
      total=total,
      percent=0,
      phase=UPLOAD_PHASE_PREPARING,
      phase_current=0,
      phase_total=total,
    )

  ensure_not_canceled(job)

  # Gather segment file lists in parallel with bounded concurrency (unchanged
  # from the pre-Drive implementation: reading directory entries/sizes is
  # cheap but still worth not serializing across many segments).
  try:
    concurrency = max(1, min(6, int(os.environ.get("CARROT_WEB_UPLOAD_CONCURRENCY", "3") or "3")))
  except Exception:
    concurrency = 3

  prepare_sem = asyncio.Semaphore(concurrency)

  async def prepare_one(idx0: int, segment: str) -> tuple[int, list[Any], Exception | None]:
    try:
      async with prepare_sem:
        return idx0, await asyncio.to_thread(segment_file_summary, segment_dir(segment)), None
    except Exception as exc:
      return idx0, [], exc

  prepared: list[tuple[list[Any], Exception | None] | None] = [None] * total
  prepared_count = 0
  prepare_tasks = [
    asyncio.create_task(prepare_one(idx0, segment))
    for idx0, segment in enumerate(segments)
  ]
  try:
    for prepare_task in asyncio.as_completed(prepare_tasks):
      idx0, files, prepare_error = await prepare_task
      prepared[idx0] = (files, prepare_error)
      prepared_count += 1
      ensure_not_canceled(job)
      if job:
        prepare_percent = (
          round((prepared_count / total) * UPLOAD_PREPARING_END_PERCENT)
          if total > 0
          else UPLOAD_PREPARING_END_PERCENT
        )
        progress(
          job,
          message=f"Prepared {prepared_count}/{total}",
          current=prepared_count,
          total=total,
          percent=prepare_percent,
          phase=UPLOAD_PHASE_PREPARING,
          phase_current=prepared_count,
          phase_total=total,
        )
  except BaseException:
    for prepare_task in prepare_tasks:
      if not prepare_task.done():
        prepare_task.cancel()
    await asyncio.gather(*prepare_tasks, return_exceptions=True)
    raise

  normalized_prepared = [
    item if item is not None else ([], RuntimeError("segment preparation did not complete"))
    for item in prepared
  ]
  total_bytes = sum(
    max(0, int(item.get("size") or 0))
    for files, error in normalized_prepared
    if error is None
    for item in files
  )
  if total_bytes <= 0:
    raise RuntimeError("업로드할 파일이 없습니다 (선택한 세그먼트에서 qcamera/rlog를 찾지 못함)")

  if job:
    progress(
      job,
      message="Compressing segments",
      current=total,
      total=total,
      percent=UPLOAD_PREPARING_END_PERCENT,
      phase=UPLOAD_PHASE_PREPARING,
      phase_current=total,
      phase_total=total,
    )

  ensure_not_canceled(job)

  timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
  zip_filename = f"{storage_label}_{timestamp}.zip"
  # [155차] /tmp(tmpfs, 콤마 기기 150M 고정)가 아니라 /data 하위(여유 수십 GB)에
  # zip을 스테이징한다 -- 선택 세그먼트 합계가 tmpfs 용량을 넘기면 zip 작성
  # 도중 OSError(Errno 28, No space left on device)로 실패했었다(FINDINGS.md
  # 핵심 발견 56, WIP.md 155차 참고).
  os.makedirs(DASHCAM_UPLOAD_TMP_DIR, exist_ok=True)
  tmp_dir = tempfile.mkdtemp(prefix="carrot_dashcam_", dir=DASHCAM_UPLOAD_TMP_DIR)
  zip_path = os.path.join(tmp_dir, zip_filename)

  def build_zip() -> None:
    # ZIP_STORED (무압축): qcamera는 이미 h265로, rlog는 이미 zstd로 압축돼
    # 있어 추가 DEFLATE는 CPU만 태우고 용량 이득이 거의 없다(콤마 기기 CPU를
    # 아끼는 쪽을 택함).
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_STORED) as zf:
      for idx0, segment in enumerate(segments):
        files, prepare_error = normalized_prepared[idx0]
        if prepare_error is not None:
          continue
        seg_dir = segment_dir(segment)
        for item in files:
          name = str(item["name"])
          zf.write(os.path.join(seg_dir, name), arcname=f"{segment}/{name}")

  try:
    await asyncio.to_thread(build_zip)
    ensure_not_canceled(job)

    zip_size = os.path.getsize(zip_path)
    if job:
      progress(
        job,
        message="Uploading to Google Drive",
        current=0,
        total=total,
        percent=UPLOAD_PREPARING_END_PERCENT,
        phase=UPLOAD_PHASE_UPLOADING,
        phase_current=0,
        phase_total=zip_size,
        bytes_current=0,
        bytes_total=zip_size,
        bytes_per_second=0,
      )

    transfer_started = time.monotonic()
    speed_samples: deque[tuple[float, int]] = deque([(transfer_started, 0)])
    transfer_span = UPLOAD_TRANSFERRING_END_PERCENT - UPLOAD_PREPARING_END_PERCENT

    def on_upload_progress(sent: int, size: int) -> None:
      # gdrive_upload calls this synchronously from inside its chunk loop;
      # raising here (e.g. via ensure_not_canceled) aborts the upload in
      # place, which is how mid-transfer cancellation is wired up without
      # threading a cancel-check callback through gdrive_upload itself.
      ensure_not_canceled(job)
      if not job:
        return
      now = time.monotonic()
      speed_samples.append((now, sent))
      while len(speed_samples) > 2 and now - speed_samples[0][0] > 3.0:
        speed_samples.popleft()
      sample_time, sample_bytes = speed_samples[0]
      elapsed = max(0.001, now - sample_time)
      ratio = (sent / size) if size > 0 else 0.0
      percent = UPLOAD_PREPARING_END_PERCENT + round(ratio * transfer_span)
      progress(
        job,
        percent=min(UPLOAD_TRANSFERRING_END_PERCENT, percent),
        phase=UPLOAD_PHASE_UPLOADING,
        phase_current=sent,
        phase_total=size,
        bytes_current=sent,
        bytes_total=size,
        bytes_per_second=max(0, round((sent - sample_bytes) / elapsed)),
      )

    drive_result = await gdrive_upload.upload_file_resumable(
      zip_path, zip_filename, progress_cb=on_upload_progress,
    )
  finally:
    shutil.rmtree(tmp_dir, ignore_errors=True)

  ensure_not_canceled(job)

  web_link = str(drive_result.get("webViewLink") or "")
  uploaded_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  results: list[dict[str, Any]] = []
  for idx0, segment in enumerate(segments):
    files, prepare_error = normalized_prepared[idx0]
    entry = {
      "segment": segment,
      "route": route_name(segment),
      "segmentIndex": segment_index(segment),
      "ok": prepare_error is None,
      "remotePath": web_link,
      "files": files,
    }
    if prepare_error is not None:
      entry["error"] = str(prepare_error)
    results.append(entry)
  if job:
    job["partial_results"] = results

  ok_count = sum(1 for item in results if item["ok"])
  response_payload = {
    "ok": ok_count == len(results) and bool(drive_result.get("id")),
    "uploaded": ok_count,
    "total": len(results),
    "uploadedAt": uploaded_at,
    "target": "gdrive",
    "deviceId": device_id,
    "remoteBasePath": web_link,
    "meta": meta,
    "results": results,
    "message": f"{ok_count}/{len(results)} uploaded to Google Drive",
    "driveFileId": drive_result.get("id"),
    "driveFileName": drive_result.get("name"),
  }
  response_payload["shareText"] = upload.upload_share_text(response_payload)

  if job:
    progress(
      job,
      message="Sending notification",
      current=total,
      total=total,
      percent=UPLOAD_NOTIFYING_START_PERCENT,
      phase=UPLOAD_PHASE_NOTIFYING,
      phase_current=0,
      phase_total=1,
    )

  ensure_not_canceled(job)
  response_payload["discord"] = await upload.send_discord_webhook(
    upload.discord_webhook_url(params),
    response_payload,
  )

  if job:
    progress(
      job,
      message="Finalizing upload",
      current=total,
      total=total,
      percent=UPLOAD_NOTIFYING_END_PERCENT,
      phase=UPLOAD_PHASE_NOTIFYING,
      phase_current=1,
      phase_total=1,
    )
  return response_payload


async def run_job(job: dict[str, Any]) -> None:
  try:
    result = await run_upload_segments(list(job.get("segments") or []), job)
    finish(job, ok=bool(result.get("ok")), result=result)
  except UploadCanceled as exc:
    results = list(job.get("partial_results") or [])
    uploaded_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ok_count = sum(1 for item in results if item.get("ok"))
    total = len(job.get("segments") or [])
    result = {
      "ok": False,
      "canceled": True,
      "uploaded": ok_count,
      "total": total,
      "uploadedAt": uploaded_at,
      "target": job.get("upload_target") or "carrot",
      "remoteBasePath": job.get("remote_base_path") or "",
      "meta": job.get("upload_meta") or {},
      "results": results,
      "message": f"Canceled {ok_count}/{total}",
      "error": str(exc),
    }
    result["shareText"] = upload.upload_share_text(result)
    append(job, "CANCELED")
    progress(job, message="Upload canceled", percent=0, phase=UPLOAD_PHASE_CANCELED)
    finish(job, ok=False, result=result, error=str(exc), status="canceled")
  except Exception as exc:
    result = {"ok": False, "error": str(exc)}
    append(job, f"FAILED: {exc}")
    finish(job, ok=False, result=result, error=str(exc))
