import asyncio
import json
from pathlib import Path
from typing import cast

import pytest
from aiohttp import web

from openpilot.selfdrive.carrot import web_upload
from openpilot.selfdrive.carrot.server.features.dashcam import catalog, routes, upload_jobs
from openpilot.selfdrive.carrot.server.services import dashcam_upload_report
from openpilot.selfdrive.carrot.server.services import web_settings


def clear_upload_env(monkeypatch):
  for key in (
    "CARROT_WEB_UPLOAD_URL",
    "CARROT_WEB_UPLOAD_TOKEN",
    "CARROT_TOSS_UPLOAD_URL",
    "CARROT_TOSS_UPLOAD_TOKEN",
    "CARROT_TMUX_WEB_UPLOAD_URL",
  ):
    monkeypatch.delenv(key, raising=False)


class FakeUploadTask:
  def __init__(self, *, done=False):
    self._done = done
    self.cancel_called = False

  def done(self):
    return self._done

  def cancel(self):
    self.cancel_called = True


def test_dashcam_stale_upload_job_is_failed_and_released():
  upload_jobs.jobs().clear()
  job = upload_jobs.create_job(["route--0"])
  task = FakeUploadTask()
  job["_task"] = task
  job["_activity_at"] = 100.0

  upload_jobs.expire_stale_jobs(now=100.0 + upload_jobs.UPLOAD_JOB_STALE_SECONDS)

  assert task.cancel_called is True
  assert job["status"] == "failed"
  assert job["error"] == "upload job expired after 30 minutes without activity"
  assert upload_jobs.running_job() is None
  upload_jobs.jobs().clear()


def test_dashcam_finished_task_cannot_leave_running_job():
  upload_jobs.jobs().clear()
  job = upload_jobs.create_job(["route--0"])
  job["_task"] = FakeUploadTask(done=True)

  upload_jobs.expire_stale_jobs(now=job["_activity_at"])

  assert job["status"] == "failed"
  assert job["error"] == "upload task ended without a final state"
  upload_jobs.jobs().clear()


def test_dashcam_upload_job_exposes_stable_phase_codes():
  upload_jobs.jobs().clear()
  job = upload_jobs.create_job(["route--0"])

  assert upload_jobs.snapshot(job)["phase"] == "queued"

  upload_jobs.progress(job, current=1, total=1, phase=upload_jobs.UPLOAD_PHASE_UPLOADING)
  assert upload_jobs.snapshot(job)["phase"] == "uploading"

  upload_jobs.finish(job, ok=True, result={"ok": True})
  snapshot = upload_jobs.snapshot(job)
  assert snapshot["status"] == "done"
  assert snapshot["phase"] == "complete"
  upload_jobs.jobs().clear()


def test_dashcam_upload_progress_is_monotonic_and_revisioned():
  upload_jobs.jobs().clear()
  job = upload_jobs.create_job(["route--0", "route--1"])
  assert upload_jobs.snapshot(job)["revision"] == 0

  upload_jobs.progress(
    job,
    phase=upload_jobs.UPLOAD_PHASE_PREPARING,
    current=1,
    total=2,
    phase_current=1,
    phase_total=2,
    percent=4,
  )
  preparing = upload_jobs.snapshot(job)
  assert preparing["progress"] == 4
  assert preparing["phase_current"] == 1
  assert preparing["phase_total"] == 2
  assert preparing["revision"] == 1

  upload_jobs.progress(
    job,
    phase=upload_jobs.UPLOAD_PHASE_UPLOADING,
    percent=2,
    bytes_current=128,
    bytes_total=1024,
    bytes_per_second=512,
  )
  uploading = upload_jobs.snapshot(job)
  assert uploading["progress"] == 4
  assert uploading["bytes_current"] == 128
  assert uploading["bytes_total"] == 1024
  assert uploading["bytes_per_second"] == 512
  assert uploading["revision"] == 2

  upload_jobs.finish(job, ok=True, result={"ok": True})
  complete = upload_jobs.snapshot(job)
  assert complete["progress"] == 100
  assert complete["revision"] == 3
  upload_jobs.jobs().clear()


def test_dashcam_upload_cancel_and_failure_keep_visible_progress():
  upload_jobs.jobs().clear()

  canceled_job = upload_jobs.create_job(["route--0"])
  upload_jobs.progress(
    canceled_job,
    phase=upload_jobs.UPLOAD_PHASE_UPLOADING,
    percent=41,
  )
  canceled = upload_jobs.cancel_job(canceled_job["id"])
  assert canceled["phase"] == "canceling"
  assert canceled["progress"] == 41
  upload_jobs.finish(
    canceled_job,
    ok=False,
    status="canceled",
    result={"ok": False, "canceled": True},
  )
  canceled = upload_jobs.snapshot(canceled_job)
  assert canceled["phase"] == "canceled"
  assert canceled["progress"] == 41

  failed_job = upload_jobs.create_job(["route--1"])
  upload_jobs.progress(
    failed_job,
    phase=upload_jobs.UPLOAD_PHASE_UPLOADING,
    percent=62,
  )
  upload_jobs.finish(
    failed_job,
    ok=False,
    error="network failed",
    result={"ok": False, "error": "network failed"},
  )
  failed = upload_jobs.snapshot(failed_job)
  assert failed["phase"] == "failed"
  assert failed["progress"] == 62
  upload_jobs.jobs().clear()


def test_dashcam_start_job_finalizes_unhandled_task_failure(monkeypatch):
  upload_jobs.jobs().clear()

  async def scenario():
    async def crash(_job):
      raise RuntimeError("unexpected task failure")

    monkeypatch.setattr(upload_jobs, "run_job", crash)
    job = upload_jobs.create_job(["route--0"])
    task = upload_jobs.start_job(job)
    with pytest.raises(RuntimeError, match="unexpected task failure"):
      await task
    await asyncio.sleep(0)
    return job

  job = asyncio.run(scenario())
  assert job["status"] == "failed"
  assert job["error"] == "unexpected task failure"
  upload_jobs.jobs().clear()


def test_carrot_runtime_contains_no_legacy_ftp_code():
  carrot_root = Path(__file__).resolve().parents[2]
  legacy_terms = (
    "ft" + "plib",
    "carrot_" + "ftp",
    "ftp" + "://",
    "ftp" + "_ok",
    "upload_folder_to_" + "ftp",
  )
  findings = []
  for path in carrot_root.rglob("*"):
    if not path.is_file() or path.suffix.lower() not in {".py", ".js", ".sh"}:
      continue
    if "tests" in path.parts or "generated" in path.parts or "vendor" in path.parts:
      continue
    text = path.read_text(encoding="utf-8", errors="ignore").lower()
    if any(term in text for term in legacy_terms):
      findings.append(str(path.relative_to(carrot_root)))
  assert findings == []


def test_carrot_man_sends_diagnostics_to_selected_target_and_carrot_logs():
  carrot_man = (Path(__file__).resolve().parents[2] / "carrot_man.py").read_text(encoding="utf-8")
  assert "def send_tmux_web(" in carrot_man
  assert "def send_tmux_carrot_logs(" in carrot_man
  assert 'self.send_tmux_carrot_logs("onroad", send_settings = True)' in carrot_man
  assert "self.send_tmux_carrot_logs(pending_tmux_reason, send_settings = False)" in carrot_man
  assert 'self.send_tmux_carrot_logs("tmux_send")' in carrot_man
  assert "using tmux web fallback" not in carrot_man
  assert "selected_upload_settings(upload_settings)" in carrot_man
  assert "Toss upload token is not configured" in carrot_man
  assert "def _tmux_toss_only(" in carrot_man
  assert "carrot_logs upload skipped: Toss-only target selected" in carrot_man
  assert "discord tmux skipped: Toss-only target selected" in carrot_man


def test_upload_targets_keep_carrot_sessions_and_toss_credentials_separate(monkeypatch):
  clear_upload_env(monkeypatch)
  settings = {
    "web_upload_url": "https://carrot.example/",
    "toss_upload_url": "https://toss.example/",
    "toss_upload_token": "toss-token",
  }
  assert web_upload.selected_upload_settings(settings) == (
    "carrot", "https://carrot.example", "",
  )
  assert web_upload.selected_upload_settings({**settings, "log_upload_target": "toss"}) == (
    "toss", "https://toss.example", "toss-token",
  )

  monkeypatch.setenv("CARROT_WEB_UPLOAD_URL", "https://carrot-env.example/root/")
  monkeypatch.setenv("CARROT_WEB_UPLOAD_TOKEN", "carrot-service-token")
  monkeypatch.setenv("CARROT_TOSS_UPLOAD_URL", "https://toss-env.example/root/")
  monkeypatch.setenv("CARROT_TOSS_UPLOAD_TOKEN", "toss-env-token")
  assert web_upload.selected_upload_settings(settings) == (
    "carrot", "https://carrot-env.example/root", "carrot-service-token",
  )
  assert web_upload.selected_upload_settings({**settings, "log_upload_target": "toss"}) == (
    "toss", "https://toss-env.example/root", "toss-env-token",
  )


def test_dashcam_upload_report_links_public_segment_and_quotes_storage_directory():
  payload = {
    "uploadedAt": "2026-07-23 11:17:18",
    "remoteBasePath": "https://upload.example/routes/HYUNDAI_IONIQ_5_PE 8b06424f3adf2bd3/",
    "meta": {
      "carName": "HYUNDAI_IONIQ_5_PE",
      "dongleId": "8b06424f3adf2bd3",
      "commit": "79a2a542",
    },
    "results": [{
      "segment": "00000cfb--69588de3d7--10",
      "route": "00000cfb--69588de3d7",
      "segmentIndex": 10,
      "ok": True,
      "remotePath": "https://upload.example/routes/HYUNDAI_IONIQ_5_PE 8b06424f3adf2bd3/00000cfb--69588de3d7--10",
    }],
  }

  report = dashcam_upload_report.upload_share_text(payload)
  assert "HYUNDAI_IONIQ_5_PE%208b06424f3adf2bd3" in report
  assert "[00000cfb--69588de3d7--10 OK · Open](https://upload.example/routes/" in report
  assert "### Open & Analyze" not in report


def test_dashcam_upload_report_adds_one_slice_link_for_consecutive_segments():
  base = "https://upload.example/routes/TEST CAR 0123456789abcdef"
  results = [
    {
      "segment": f"00000cfb--69588de3d7--{index}",
      "route": "00000cfb--69588de3d7",
      "segmentIndex": index,
      "ok": True,
      "remotePath": f"{base}/00000cfb--69588de3d7--{index}",
    }
    for index in (10, 11, 12)
  ]

  report = dashcam_upload_report.upload_share_text({"remoteBasePath": f"{base}/", "results": results})
  assert "### Open & Analyze" in report
  assert "Segments 10–12 (3 logs) · Web/Video/Tools" in report
  assert "https://upload.example/routes/TEST%20CAR%200123456789abcdef/00000cfb--69588de3d7--10:13" in report
  assert report.count(" OK · Open]") == 3


def test_dashcam_upload_report_does_not_merge_nonconsecutive_segments():
  base = "https://upload.example/routes/TEST CAR 0123456789abcdef"
  results = [
    {
      "segment": f"00000cfb--69588de3d7--{index}",
      "route": "00000cfb--69588de3d7",
      "segmentIndex": index,
      "ok": True,
      "remotePath": f"{base}/00000cfb--69588de3d7--{index}",
    }
    for index in (10, 12)
  ]

  report = dashcam_upload_report.upload_share_text({"remoteBasePath": f"{base}/", "results": results})
  assert "### Open & Analyze" not in report


def test_carrot_logs_target_is_independent_from_dsm_token(monkeypatch):
  clear_upload_env(monkeypatch)
  monkeypatch.setenv("CARROT_WEB_UPLOAD_TOKEN", "dsm-token")
  monkeypatch.setenv("CARROT_TOSS_UPLOAD_URL", "https://toss.example")
  monkeypatch.setenv("CARROT_TOSS_UPLOAD_TOKEN", "toss-token")
  monkeypatch.setenv("CARROT_TMUX_WEB_UPLOAD_URL", "https://tmux.example/upload/")
  assert web_upload.carrot_logs_web_target() == ("https://tmux.example/upload", {})


def test_tmux_web_post_sends_multipart_and_closes_files(tmp_path: Path):
  tmux_path = tmp_path / "tmux.log"
  settings_path = tmp_path / "toggle_values.json"
  tmux_path.write_bytes(b"tmux-data")
  settings_path.write_bytes(b'{"enabled": true}')
  captured = {}

  def fake_post(url, *, headers, data, files, timeout):
    captured.update({"url": url, "headers": headers, "data": data, "files": files, "timeout": timeout})
    captured["contents"] = [item[1][1].read() for item in files]
    return "response"

  response = web_upload.post_tmux_web(
    "https://upload.example/api/v1/tmux/upload",
    {"Authorization": "Bearer token"},
    {"tmux_why": "exception"},
    str(tmux_path),
    str(settings_path),
    fake_post,
  )

  assert response == "response"
  assert captured["headers"] == {"Authorization": "Bearer token"}
  assert captured["data"] == {"tmux_why": "exception"}
  assert [item[0] for item in captured["files"]] == ["files[0]", "files[1]"]
  assert captured["contents"] == [b"tmux-data", b'{"enabled": true}']
  assert captured["timeout"] == 30
  assert all(item[1][1].closed for item in captured["files"])


def test_web_settings_default_to_carrot_and_preserve_toss_credentials():
  defaults = web_settings.sanitize_web_settings({})
  assert defaults["log_upload_target"] == "carrot"
  assert defaults["web_upload_url"] == "https://upload.shind0.synology.me"
  assert defaults["toss_upload_url"] == "https://op.wjcloud.kr"
  assert defaults["toss_upload_token"] == ""
  assert "web_upload_token" not in defaults

  settings = web_settings.sanitize_web_settings({
    "log_upload_target": "toss",
    "web_upload_url": "https://carrot.example/",
    "toss_upload_url": "https://toss.example/",
    "toss_upload_token": "toss-token",
  })
  assert settings["log_upload_target"] == "toss"
  assert settings["web_upload_url"] == "https://carrot.example"
  assert settings["toss_upload_url"] == "https://toss.example"
  assert settings["toss_upload_token"] == "toss-token"


@pytest.mark.parametrize("previous_url", [
  "https://op.wjcloud.kr",
  "https://shind0.synology.me",
  "https://SHIND0.synology.me",
])
def test_web_settings_migrate_previous_default_server(previous_url):
  settings = web_settings.sanitize_web_settings({"web_upload_url": previous_url})
  assert settings["web_upload_url"] == web_upload.DEFAULT_WEB_UPLOAD_URL


def test_dashcam_upload_test_route_is_unique():
  app = web.Application()
  routes.register(app)
  matching = [
    route for route in app.router.routes()
    if route.method == "POST" and getattr(route.resource, "canonical", "") == "/api/dashcam/upload/test"
  ]
  assert len(matching) == 1


def test_dashcam_upload_test_uses_gdrive_connection(monkeypatch):
  async def fake_test_connection():
    return {"ok": True, "connected": True, "folder_id": "folder-123"}

  monkeypatch.setattr(routes.gdrive_upload, "test_connection", fake_test_connection)
  response = asyncio.run(routes.api_dashcam_upload_test(cast(web.Request, None)))
  payload = json.loads(response.text or "")
  assert response.status == 200
  assert payload["target"] == "gdrive"
  assert payload["ok"] is True
  assert payload["folder_id"] == "folder-123"


def test_dashcam_upload_test_reports_gdrive_not_connected(monkeypatch):
  async def fake_test_connection():
    return {"ok": False, "connected": False, "error": "Google Drive가 연결되어 있지 않습니다"}

  monkeypatch.setattr(routes.gdrive_upload, "test_connection", fake_test_connection)
  response = asyncio.run(routes.api_dashcam_upload_test(cast(web.Request, None)))
  payload = json.loads(response.text or "")
  assert response.status == 502
  assert payload["ok"] is False


def test_dashcam_upload_summary_selects_only_original_qcamera_and_rlog(tmp_path: Path):
  (tmp_path / "qcamera.ts").write_bytes(b"original-video")
  (tmp_path / "qcamera.mp4").write_bytes(b"converted-video")
  (tmp_path / "rlog.zst").write_bytes(b"original-rlog")
  (tmp_path / "rlog.bz2").write_bytes(b"fallback-rlog")
  (tmp_path / "qlog.zst").write_bytes(b"reduced-log")
  (tmp_path / "fcamera.hevc").write_bytes(b"auxiliary-video")

  files = catalog.segment_file_summary(str(tmp_path))

  assert [(item["kind"], item["name"], item["size"]) for item in files] == [
    ("qcamera", "qcamera.ts", len(b"original-video")),
    ("rlog", "rlog.zst", len(b"original-rlog")),
  ]


def test_dashcam_upload_summary_allows_rlog_without_qcamera(tmp_path: Path):
  (tmp_path / "rlog.bz2").write_bytes(b"original-rlog")

  files = catalog.segment_file_summary(str(tmp_path))

  assert [(item["kind"], item["name"]) for item in files] == [("rlog", "rlog.bz2")]


def test_dashcam_upload_summary_requires_rlog(tmp_path: Path):
  (tmp_path / "qcamera.ts").write_bytes(b"original-video")

  with pytest.raises(web.HTTPNotFound) as exc_info:
    catalog.segment_file_summary(str(tmp_path))
  assert exc_info.value.text == "rlog not found"