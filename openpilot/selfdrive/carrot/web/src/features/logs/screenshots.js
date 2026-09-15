"use strict";

import { hydrateLogsLazyImages, isLogsPageActive, unobserveLogsLazyImages } from "./runtime.js";

// Logs page — Screen Recording tab, "Photos" list.
//
// The onroad capture button (openpilot/selfdrive/ui/onroad/screenshot_capture.py)
// saves PNG screenshots into the same folders as video recordings, but
// server/features/screenrecord/catalog.py's video listing only recognizes
// video extensions, so screenshots never showed up anywhere in the UI.
// Rather than folding photos into the video list's virtualized rendering
// (screenrecord.js), this renders them as their own small non-virtualized
// list: photo counts are expected to stay far smaller than video counts, so
// the extra complexity of windowing isn't worth it here.
//
// [39차] Originally a thumbnail-only strip (view on click, nothing else).
// Selection/toolbar/download/upload mirrors screenrecord.js's flat video
// list convention (checkbox in front, download+send buttons at the end of
// each row, select-all/download-selected/upload-selected toolbar above).

const SCREENSHOTS_PAGE_SIZE = 60;

const screenshotsState = {
  initialized: false,
  loading: false,
  photos: [],
  selected: new Set(),
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
  ].join("|")).join("\n");
}

// Selection — a flat Set of photo ids (mirrors screenrecordState.selected).
function screenshotsSelectedPhotos() {
  const photos = screenshotsState.photos || [];
  return photos.filter((photo) => screenshotsState.selected.has(String(photo?.id || "")));
}

function pruneScreenshotsSelection(photos) {
  const present = new Set((photos || []).map((photo) => String(photo?.id || "")));
  for (const id of Array.from(screenshotsState.selected)) {
    if (!present.has(id)) screenshotsState.selected.delete(id);
  }
}

function screenshotRowHtml(photo, index = 0) {
  const id = escapeHtml(photo.id || "");
  const name = escapeHtml(photo.name || "-");
  const date = escapeHtml(formatRelativeEpoch(photo.modifiedEpoch) || localizeRelativeLabel(photo.modifiedLabel || photo.relativeModifiedLabel) || "-");
  const size = escapeHtml(formatLogBytes(photo.size));
  const checked = screenshotsState.selected.has(String(photo?.id || "")) ? " checked" : "";
  return `<article class="screenrecord-row ui-stagger-item" style="--i:${index}" data-action="view-screenshot" data-id="${id}" data-name="${name}">
    <label class="dashcam-segment-inline-check" title="${escapeHtml(getUIText("select_all", "Select"))}" onclick="event.stopPropagation()">
      <input type="checkbox" data-action="select-screenshot" data-id="${id}"${checked}>
    </label>
    <div class="screenrecord-row__thumb" aria-hidden="true">
      <img class="logs-lazy-img" loading="lazy" decoding="async" fetchpriority="low" data-src="${screenshotApiPath("thumbnail", photo.id || "")}" alt="">
    </div>
    <div class="screenrecord-row__main">
      <div class="screenrecord-row__name">${name}</div>
      <div class="screenrecord-row__meta">
        <span>${date}</span>
        <span>${size}</span>
      </div>
    </div>
    <button class="screenrecord-download" type="button" data-action="download-screenshot" data-id="${id}" aria-label="${escapeHtml(getUIText("download", "Download"))}" title="${escapeHtml(getUIText("download", "Download"))}">
      <svg viewBox="0 0 24 24"><path fill="currentColor" d="M5 20h14v-2H5m14-9h-4V3H9v6H5l7 7z"/></svg>
    </button>
    <button class="screenrecord-download" type="button" data-action="upload-screenshot" data-id="${id}" aria-label="${escapeHtml(getUIText("upload_send", "Send"))}" title="${escapeHtml(getUIText("upload_send", "Send"))}">
      <svg viewBox="0 0 24 24"><path fill="currentColor" d="M5 4h14v2H5m7 3 5 5h-3v6h-4v-6H7z"/></svg>
    </button>
  </article>`;
}

// Toolbar above the photo list — mirrors screenrecord.js's flat toolbar
// (one toolbar for the whole list, no grouping).
function renderScreenshotsToolbar() {
  const wrap = document.getElementById("screenshotsToolbarWrap");
  const toolbar = document.getElementById("screenshotsToolbar");
  if (!wrap || !toolbar) return;
  const photos = screenshotsState.photos || [];
  if (!photos.length) {
    wrap.hidden = true;
    return;
  }
  wrap.hidden = false;
  const selectedCount = screenshotsState.selected.size;
  const allSelected = photos.length > 0 && selectedCount === photos.length;

  const countEl = document.getElementById("screenshotsSelectionCount");
  if (countEl) countEl.textContent = getUIText("selected_count", "{count} selected", { count: selectedCount });

  const selectBtn = toolbar.querySelector('[data-action="select-all-screenshots"]');
  if (selectBtn) {
    selectBtn.dataset.selected = allSelected ? "1" : "0";
    selectBtn.textContent = allSelected
      ? getUIText("deselect_all", "Deselect all")
      : getUIText("select_all", "Select all");
  }

  const downloadBtn = toolbar.querySelector('[data-action="download-selected-screenshots"]');
  if (downloadBtn) {
    downloadBtn.textContent = getUIText("download_selected", "Download selected");
    downloadBtn.disabled = selectedCount === 0;
  }

  const uploadBtn = toolbar.querySelector('[data-action="upload-selected-screenshots"]');
  if (uploadBtn) {
    uploadBtn.textContent = getUIText("upload_selected", "Upload selected");
    uploadBtn.disabled = selectedCount === 0;
  }
}

// Bulk state changes (select-all/deselect-all) don't recreate rows, so their
// checkboxes need an explicit sync; a single row's own checkbox toggle
// doesn't need this — the browser already reflects the click natively.
function syncScreenshotRowCheckboxes() {
  const host = document.getElementById("screenrecordPhotos");
  if (!host) return;
  host.querySelectorAll('input[data-action="select-screenshot"]').forEach((input) => {
    const id = input.dataset.id || "";
    input.checked = screenshotsState.selected.has(id);
  });
}

function toggleScreenshotSelection(id, checked) {
  const key = String(id || "");
  if (!key) return;
  if (checked) screenshotsState.selected.add(key);
  else screenshotsState.selected.delete(key);
  renderScreenshotsToolbar();
}

function toggleScreenshotSelectAll(shouldClear) {
  if (shouldClear) {
    screenshotsState.selected.clear();
  } else {
    (screenshotsState.photos || []).forEach((photo) => {
      const id = String(photo?.id || "");
      if (id) screenshotsState.selected.add(id);
    });
  }
  syncScreenshotRowCheckboxes();
  renderScreenshotsToolbar();
}

function screenshotUploadConfirmHtml(photos) {
  const totalBytes = photos.reduce((sum, photo) => sum + (Number(photo?.size) || 0), 0);
  const fileCountLabel = getUIText("upload_file_count", "{count} files", { count: photos.length });
  const sizeLabel = totalBytes > 0 ? formatLogBytes(totalBytes) : getUIText("upload_size_unknown", "size unknown");
  const networkWarning = getUIText("upload_data_warning", "This upload may use mobile data depending on your network connection.");
  return `<section class="app-dialog__uploadBrief" aria-label="${escapeHtml(getUIText("upload_summary_label", "Upload summary"))}">
    <div class="app-dialog__uploadBriefCopy">
      <strong class="app-dialog__uploadBriefTitle">${escapeHtml(fileCountLabel)}</strong>
    </div>
    <div class="app-dialog__uploadBriefAmount">
      <strong>${escapeHtml(sizeLabel)}</strong>
    </div>
    <div class="app-dialog__metaLine">${escapeHtml(networkWarning)}</div>
  </section>`;
}

function screenshotUploadResultHtml(result) {
  const results = Array.isArray(result?.results) ? result.results : [];
  const rows = results.map((item) => {
    const ok = item?.ok === true;
    const status = ok
      ? getUIText("upload_status_complete", "Complete")
      : getUIText("upload_status_failed", "Failed");
    return `<div class="app-dialog__metaResult">
      <code class="app-dialog__metaCode">${escapeHtml(String(item?.name || item?.id || ""))}</code>
      <span class="app-dialog__metaState" data-tone="${ok ? "success" : "error"}">${escapeHtml(status)}</span>
    </div>`;
  }).join("");
  return `<div class="app-dialog__metaList">
    <div class="app-dialog__metaLine">${escapeHtml(getUIText("upload_complete_count", "Upload complete {uploaded}/{total}", {
      uploaded: Number(result?.uploaded || 0),
      total: Number(result?.total || 0),
    }))}</div>
    <div class="app-dialog__metaResultList">${rows}</div>
  </div>`;
}

// Synchronous, per-file sequential upload (no job/polling) — same choice as
// screenrecord.js's uploadScreenrecordVideos(): screenshots are already
// single files and expected to be few at a time.
async function uploadScreenshots(ids) {
  const targets = Array.from(new Set(ids || [])).filter(Boolean);
  if (!targets.length) {
    showAppToast(getUIText("no_selected_photos", "No photos selected."), { tone: "error" });
    return;
  }
  const photos = (screenshotsState.photos || []).filter((photo) => targets.includes(String(photo?.id || "")));

  const ok = await appConfirm("", {
    title: getUIText("screenshot_upload", "Upload Photo"),
    html: true,
    messageHtml: screenshotUploadConfirmHtml(photos.length ? photos : targets.map((id) => ({ id, size: 0 }))),
    confirmLabel: getUIText("upload_send", "Send"),
  });
  if (!ok) return;

  const activityId = typeof beginAppActivity === "function"
    ? beginAppActivity("logs", getUIText("log_uploading", "Uploading logs"))
    : null;
  try {
    const result = await postJson("/api/screenrecord/photo/upload", { ids: targets });
    const message = getUIText("upload_complete_count", "Upload complete {uploaded}/{total}", {
      uploaded: Number(result?.uploaded || 0),
      total: Number(result?.total || targets.length),
    });
    showAppToast(message, { tone: result?.ok ? "default" : "error", duration: 3600 });
    await openAppDialog({
      mode: "choice",
      title: getUIText("log_upload_result", "Upload Result"),
      html: true,
      messageHtml: screenshotUploadResultHtml(result),
      cancelLabel: getUIText("close", "Close"),
    });
  } catch (e) {
    showAppToast(`${getUIText("screenshot_upload", "Upload Photo")} ${getUIText("error", "Error")}: ${e.message || e}`, {
      tone: "error",
      duration: 4200,
    });
  } finally {
    if (activityId && typeof endAppActivity === "function") endAppActivity(activityId);
  }
}

// Sequential <a download> clicks instead of window.open: opening several
// blank tabs in a row triggers the popup blocker on all but the first, while
// a same-page download-triggering anchor click is allowed per click even in
// a loop originating from one user gesture.
function downloadScreenshots(ids) {
  const targets = Array.from(new Set(ids || [])).filter(Boolean);
  if (!targets.length) {
    showAppToast(getUIText("no_selected_photos", "No photos selected."), { tone: "error" });
    return;
  }
  targets.forEach((id) => {
    const link = document.createElement("a");
    link.href = screenshotApiPath("download", id);
    link.rel = "noopener";
    document.body.appendChild(link);
    link.click();
    link.remove();
  });
}

function renderScreenshots() {
  const wrap = document.getElementById("screenrecordPhotosWrap");
  const host = document.getElementById("screenrecordPhotos");
  const title = document.getElementById("screenrecordPhotosTitle");
  if (!wrap || !host) return;
  if (!isLogsPageActive()) return;
  if (title) title.textContent = getUIText("screenrecord_photos_title") || "Photos";
  const photos = screenshotsState.photos || [];
  renderScreenshotsToolbar();
  if (!photos.length) {
    wrap.hidden = true;
    host.innerHTML = "";
    host.dataset.signature = "";
    return;
  }
  const nextSignature = `${screenshotsSignature(photos)}|${screenshotsState.selected.size}`;
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
    pruneScreenshotsSelection(photos);
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
  downloadScreenshots,
  loadScreenshots,
  openScreenshot,
  renderScreenshots,
  screenshotApiPath,
  screenshotsSelectedPhotos,
  screenshotsState,
  toggleScreenshotSelectAll,
  toggleScreenshotSelection,
  uploadScreenshots,
};
