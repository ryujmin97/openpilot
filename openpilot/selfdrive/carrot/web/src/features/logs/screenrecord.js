"use strict";

import {
  formatLogBytes,
  formatRelativeEpoch,
  hydrateLogsLazyImages,
  isLogsPageActive,
  localizeRelativeLabel,
  logsEmptyStateHtml,
  logsLoadingSkeletonHtml,
  logsScrollTops,
  openLogsVideoPlayer,
  restoreLogsScrollTop,
  unobserveLogsLazyImages,
} from "./runtime.js";

// Logs page — Screen Recording tab.
// Virtual list of saved screen recordings with lazy thumbnails, paged loading,
// and a download/playback action row.

const SCREENRECORD_PAGE_SIZE = 40;
const SCREENRECORD_LOAD_AHEAD_PX = 720;
const SCREENRECORD_WINDOW_OVERSCAN = 8;

const screenrecordState = {
  initialized: false,
  loading: false,
  loadingMore: false,
  loadSeq: 0,
  videos: [],
  selected: new Set(),
  rowHeight: 80,
  windowStart: 0,
  windowEnd: 0,
  total: 0,
  nextOffset: 0,
  hasMore: false,
  signature: "",
  renderFrame: 0,
};

function setScreenrecordStatus(message, tone = "") {
  const status = document.getElementById("screenrecordStatus");
  if (!status) return;
  status.textContent = message || "";
  status.hidden = !message;
  status.classList.toggle("is-error", tone === "error");
}

function screenrecordApiPath(kind, fileId) {
  return `/api/screenrecord/${kind}/${encodeURIComponent(fileId)}`;
}

function screenrecordVideosSignature(videos) {
  return (videos || []).map((video) => [
    video.id || "",
    video.name || "",
    video.modifiedLabel || "",
    video.size || 0,
  ].join("|")).join("\n") + "|" + (typeof LANG !== "undefined" ? LANG : "");
}

// Selection — a flat Set of video ids, independent of the virtualized window
// (a video stays "selected" whether or not its row is currently mounted).
function screenrecordSelectedVideos() {
  const videos = screenrecordState.videos || [];
  return videos.filter((video) => screenrecordState.selected.has(String(video?.id || "")));
}

function pruneScreenrecordSelection(videos) {
  const present = new Set((videos || []).map((video) => String(video?.id || "")));
  for (const id of Array.from(screenrecordState.selected)) {
    if (!present.has(id)) screenrecordState.selected.delete(id);
  }
}

function screenrecordShouldLoadMore(scroller) {
  if (!scroller || !screenrecordState.hasMore || screenrecordState.loading || screenrecordState.loadingMore) return false;
  const remaining = scroller.scrollHeight - scroller.scrollTop - scroller.clientHeight;
  return remaining <= SCREENRECORD_LOAD_AHEAD_PX;
}

function screenrecordWindowFor(host, count) {
  const rowHeight = Math.max(48, Number(screenrecordState.rowHeight) || 80);
  const viewportHeight = Math.max(1, host?.clientHeight || rowHeight * 8);
  const scrollTop = Math.max(0, host?.scrollTop || 0);
  const visibleRows = Math.ceil(viewportHeight / rowHeight);
  const start = Math.max(0, Math.floor(scrollTop / rowHeight) - SCREENRECORD_WINDOW_OVERSCAN);
  const end = Math.min(count, start + visibleRows + (SCREENRECORD_WINDOW_OVERSCAN * 2));
  return { start, end, rowHeight };
}

function screenrecordMeasureRowHeight(host) {
  const row = host?.querySelector?.(".screenrecord-row");
  if (!row) return;
  const styles = window.getComputedStyle?.(host);
  const gap = Number.parseFloat(styles?.rowGap || styles?.gap || "0") || 0;
  const nextHeight = Math.max(48, row.getBoundingClientRect().height + gap);
  if (Math.abs(nextHeight - screenrecordState.rowHeight) < 1) return;
  screenrecordState.rowHeight = nextHeight;
}

function screenrecordSpacerNode(height, position) {
  if (height <= 0) return null;
  const node = document.createElement("div");
  node.className = "screenrecord-virtual-spacer";
  node.dataset.spacer = position;
  node.style.height = `${Math.round(height)}px`;
  return node;
}

function screenrecordRowNode(video, index, existingRows) {
  const id = String(video?.id || "");
  const existing = id ? existingRows.get(id) : null;
  if (existing) {
    existing.style.setProperty("--i", String(index));
    existing.classList.remove("ui-stagger-item");
    return existing;
  }
  const template = document.createElement("template");
  template.innerHTML = screenrecordVideoRowHtml(video, index);
  return template.content.firstElementChild;
}

function patchScreenrecordWindow(host, videos, view) {
  const existingRows = new Map(
    Array.from(host.querySelectorAll(".screenrecord-row"))
      .map((node) => [node.dataset.id || "", node])
      .filter(([id]) => Boolean(id))
  );
  const frag = document.createDocumentFragment();
  const topSpacer = screenrecordSpacerNode(view.start * view.rowHeight, "top");
  const bottomSpacer = screenrecordSpacerNode((videos.length - view.end) * view.rowHeight, "bottom");
  if (topSpacer) frag.appendChild(topSpacer);
  videos.slice(view.start, view.end).forEach((video, offset) => {
    const row = screenrecordRowNode(video, view.start + offset, existingRows);
    if (row) frag.appendChild(row);
  });
  if (bottomSpacer) frag.appendChild(bottomSpacer);
  unobserveLogsLazyImages(host);
  host.replaceChildren(frag);
}

function setScreenrecordLoadingMoreUi(active) {
  const host = document.getElementById("screenrecordVideos");
  if (!host) return;
  host.classList.toggle("is-loading-more", Boolean(active));
}

function scheduleScreenrecordWindowRender() {
  if (screenrecordState.renderFrame) return;
  screenrecordState.renderFrame = requestAnimationFrame(() => {
    screenrecordState.renderFrame = 0;
    renderScreenrecordVideos({ preserve: true });
  });
}

function openScreenrecordPlayer(id, name) {
  if (!id) return;
  const videos = screenrecordState.videos || [];
  const position = videos.findIndex((video) => String(video?.id || "") === String(id));
  const previous = position > 0 ? videos[position - 1] : null;
  const next = position >= 0 && position < videos.length - 1 ? videos[position + 1] : null;
  openLogsVideoPlayer(name || getUIText("logs_screenrecord", "Screen Record"), screenrecordApiPath("video", id), {
    kind: "screenrecord",
    onPrevious: previous ? ({ close } = {}) => {
      close?.();
      openScreenrecordPlayer(previous.id || "", previous.name || "");
    } : null,
    onNext: next ? ({ close } = {}) => {
      close?.();
      openScreenrecordPlayer(next.id || "", next.name || "");
    } : null,
  });
}

function screenrecordVideoRowHtml(video, index = 0) {
  const id = escapeHtml(video.id || "");
  const name = escapeHtml(video.name || "-");
  const date = escapeHtml(formatRelativeEpoch(video.modifiedEpoch) || localizeRelativeLabel(video.modifiedLabel || video.relativeModifiedLabel) || "-");
  const size = escapeHtml(formatLogBytes(video.size));
  const ext = escapeHtml((video.ext || "video").toUpperCase());
  const checked = screenrecordState.selected.has(String(video?.id || "")) ? " checked" : "";
  return `<article class="screenrecord-row ui-stagger-item" style="--i:${index}" data-action="play-screenrecord" data-id="${id}" data-name="${name}">
    <label class="dashcam-segment-inline-check" title="${escapeHtml(getUIText("select_all", "Select"))}" onclick="event.stopPropagation()">
      <input type="checkbox" data-action="select-screenrecord" data-id="${id}"${checked}>
    </label>
    <div class="screenrecord-row__thumb" aria-hidden="true">
      <img class="logs-lazy-img" loading="lazy" decoding="async" fetchpriority="low" data-src="${screenrecordApiPath("thumbnail", video.id || "")}" alt="">
    </div>
    <div class="screenrecord-row__main">
      <div class="screenrecord-row__name">${name}</div>
      <div class="screenrecord-row__meta">
        <span>${date}</span>
        <span>${size}</span>
        <span>${ext}</span>
      </div>
    </div>
    <button class="screenrecord-download" type="button" data-action="download-screenrecord" data-id="${id}" aria-label="${escapeHtml(getUIText("download", "Download"))}" title="${escapeHtml(getUIText("download", "Download"))}">
      <svg viewBox="0 0 24 24"><path fill="currentColor" d="M5 20h14v-2H5m14-9h-4V3H9v6H5l7 7z"/></svg>
    </button>
    <button class="screenrecord-download" type="button" data-action="upload-screenrecord" data-id="${id}" aria-label="${escapeHtml(getUIText("upload_send", "Send"))}" title="${escapeHtml(getUIText("upload_send", "Send"))}">
      <svg viewBox="0 0 24 24"><path fill="currentColor" d="M5 4h14v2H5m7 3 5 5h-3v6h-4v-6H7z"/></svg>
    </button>
  </article>`;
}

// Toolbar above the (virtualized) video list — mirrors dashcam's per-route
// selection row, but flat (one toolbar for the whole list, no route grouping).
function renderScreenrecordToolbar() {
  const wrap = document.getElementById("screenrecordToolbarWrap");
  const toolbar = document.getElementById("screenrecordToolbar");
  if (!wrap || !toolbar) return;
  const videos = screenrecordState.videos || [];
  if (!videos.length) {
    wrap.hidden = true;
    return;
  }
  wrap.hidden = false;
  const selectedCount = screenrecordState.selected.size;
  const allSelected = videos.length > 0 && selectedCount === videos.length;

  const countEl = document.getElementById("screenrecordSelectionCount");
  if (countEl) countEl.textContent = getUIText("selected_count", "{count} selected", { count: selectedCount });

  const selectBtn = toolbar.querySelector('[data-action="select-all-screenrecord"]');
  if (selectBtn) {
    selectBtn.dataset.selected = allSelected ? "1" : "0";
    selectBtn.textContent = allSelected
      ? getUIText("deselect_all", "Deselect all")
      : getUIText("select_all", "Select all");
  }

  const downloadBtn = toolbar.querySelector('[data-action="download-selected-screenrecord"]');
  if (downloadBtn) {
    downloadBtn.textContent = getUIText("download_selected", "Download selected");
    downloadBtn.disabled = selectedCount === 0;
  }

  const uploadBtn = toolbar.querySelector('[data-action="upload-selected-screenrecord"]');
  if (uploadBtn) {
    uploadBtn.textContent = getUIText("upload_selected", "Upload selected");
    uploadBtn.disabled = selectedCount === 0;
  }
}

// Bulk state changes (select-all/deselect-all) don't recreate already-mounted
// rows (patchScreenrecordWindow reuses existing nodes by id), so their
// checkboxes need an explicit sync; a single row's own checkbox toggle
// doesn't need this — the browser already reflects the click natively.
function syncScreenrecordRowCheckboxes() {
  const host = document.getElementById("screenrecordVideos");
  if (!host) return;
  host.querySelectorAll('input[data-action="select-screenrecord"]').forEach((input) => {
    const id = input.dataset.id || "";
    input.checked = screenrecordState.selected.has(id);
  });
}

function toggleScreenrecordSelection(id, checked) {
  const key = String(id || "");
  if (!key) return;
  if (checked) screenrecordState.selected.add(key);
  else screenrecordState.selected.delete(key);
  renderScreenrecordToolbar();
}

function toggleScreenrecordSelectAll(shouldClear) {
  if (shouldClear) {
    screenrecordState.selected.clear();
  } else {
    (screenrecordState.videos || []).forEach((video) => {
      const id = String(video?.id || "");
      if (id) screenrecordState.selected.add(id);
    });
  }
  syncScreenrecordRowCheckboxes();
  renderScreenrecordToolbar();
}

function screenrecordUploadConfirmHtml(videos) {
  const totalBytes = videos.reduce((sum, video) => sum + (Number(video?.size) || 0), 0);
  const fileCountLabel = getUIText("upload_file_count", "{count} files", { count: videos.length });
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

function screenrecordUploadResultHtml(result) {
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

// Synchronous, per-file sequential upload (no job/polling): the user
// explicitly chose this over the dashcam-style zip+job flow because screen
// recordings are already single files and expected to be few/short-lived
// selections, at the cost of no cancel and no live progress bar.
async function uploadScreenrecordVideos(ids) {
  const targets = Array.from(new Set(ids || [])).filter(Boolean);
  if (!targets.length) {
    showAppToast(getUIText("no_selected_recordings", "No recordings selected."), { tone: "error" });
    return;
  }
  const videos = (screenrecordState.videos || []).filter((video) => targets.includes(String(video?.id || "")));

  const ok = await appConfirm("", {
    title: getUIText("screenrecord_upload", "Upload Recording"),
    html: true,
    messageHtml: screenrecordUploadConfirmHtml(videos.length ? videos : targets.map((id) => ({ id, size: 0 }))),
    confirmLabel: getUIText("upload_send", "Send"),
  });
  if (!ok) return;

  const activityId = typeof beginAppActivity === "function"
    ? beginAppActivity("logs", getUIText("log_uploading", "Uploading logs"))
    : null;
  try {
    const result = await postJson("/api/screenrecord/upload", { ids: targets });
    const message = getUIText("upload_complete_count", "Upload complete {uploaded}/{total}", {
      uploaded: Number(result?.uploaded || 0),
      total: Number(result?.total || targets.length),
    });
    showAppToast(message, { tone: result?.ok ? "default" : "error", duration: 3600 });
    await openAppDialog({
      mode: "choice",
      title: getUIText("log_upload_result", "Upload Result"),
      html: true,
      messageHtml: screenrecordUploadResultHtml(result),
      cancelLabel: getUIText("close", "Close"),
    });
  } catch (e) {
    showAppToast(`${getUIText("screenrecord_upload", "Upload Recording")} ${getUIText("error", "Error")}: ${e.message || e}`, {
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
function downloadScreenrecordVideos(ids) {
  const targets = Array.from(new Set(ids || [])).filter(Boolean);
  if (!targets.length) {
    showAppToast(getUIText("no_selected_recordings", "No recordings selected."), { tone: "error" });
    return;
  }
  targets.forEach((id) => {
    const link = document.createElement("a");
    link.href = screenrecordApiPath("download", id);
    link.rel = "noopener";
    document.body.appendChild(link);
    link.click();
    link.remove();
  });
}

function renderScreenrecordVideos(options = {}) {
  const host = document.getElementById("screenrecordVideos");
  if (!host) return;
  if (!isLogsPageActive()) return;
  const preserve = options.preserve === true;
  const videos = screenrecordState.videos || [];
  renderScreenrecordToolbar();
  if (screenrecordState.loading && !videos.length) {
    setScreenrecordStatus("");
    host.innerHTML = logsLoadingSkeletonHtml("screen");
    host.dataset.signature = "";
    host.dataset.renderCount = "0";
    return;
  }
  if (!videos.length) {
    host.innerHTML = logsEmptyStateHtml("screen");
    host.dataset.signature = "";
    host.dataset.renderCount = "0";
    setScreenrecordStatus("");
    return;
  }
  setScreenrecordStatus("");
  const view = screenrecordWindowFor(host, videos.length);
  const nextSignature = `${screenrecordState.signature || screenrecordVideosSignature(videos)}|${view.start}:${view.end}|${screenrecordState.loadingMore ? "more" : ""}`;
  if (preserve && host.dataset.signature === nextSignature) {
    hydrateLogsLazyImages(host);
    return;
  }
  patchScreenrecordWindow(host, videos, view);
  host.dataset.signature = nextSignature;
  host.dataset.renderCount = String(view.end - view.start);
  screenrecordState.windowStart = view.start;
  screenrecordState.windowEnd = view.end;
  setScreenrecordLoadingMoreUi(screenrecordState.loadingMore);
  hydrateLogsLazyImages(host);
  requestAnimationFrame(() => screenrecordMeasureRowHeight(host));
}

async function loadScreenrecordVideos({ silent = false, append = false } = {}) {
  if (append && (!screenrecordState.hasMore || screenrecordState.loading || screenrecordState.loadingMore)) return;
  const seq = ++screenrecordState.loadSeq;
  if (append) {
    screenrecordState.loadingMore = true;
    setScreenrecordLoadingMoreUi(true);
  } else if (!silent) {
    screenrecordState.loading = true;
    screenrecordState.loadingMore = false;
    setScreenrecordLoadingMoreUi(false);
    renderScreenrecordVideos();
  }
  try {
    const offset = append ? (screenrecordState.nextOffset || screenrecordState.videos.length || 0) : 0;
    const limit = append ? SCREENRECORD_PAGE_SIZE : Math.max(SCREENRECORD_PAGE_SIZE, screenrecordState.videos.length || 0);
    const json = await getJson(`/api/screenrecord/videos?offset=${offset}&limit=${limit}`);
    if (seq !== screenrecordState.loadSeq) return;
    if (!isLogsPageActive()) {
      screenrecordState.loading = false;
      screenrecordState.loadingMore = false;
      setScreenrecordLoadingMoreUi(false);
      return;
    }
    const incoming = Array.isArray(json.videos) ? json.videos : [];
    const videos = append ? screenrecordState.videos.concat(incoming) : incoming;
    const nextSignature = screenrecordVideosSignature(videos);
    if (silent && nextSignature === screenrecordState.signature) {
      screenrecordState.loading = false;
      screenrecordState.loadingMore = false;
      setScreenrecordLoadingMoreUi(false);
      return;
    }
    screenrecordState.videos = videos;
    pruneScreenrecordSelection(videos);
    screenrecordState.signature = nextSignature;
    screenrecordState.total = Number.isFinite(Number(json.total)) ? Number(json.total) : videos.length;
    screenrecordState.nextOffset = json.nextOffset == null ? videos.length : Number(json.nextOffset) || videos.length;
    screenrecordState.hasMore = Boolean(json.hasMore);
    screenrecordState.loading = false;
    screenrecordState.loadingMore = false;
    setScreenrecordLoadingMoreUi(false);
    renderScreenrecordVideos({ animate: !silent });
    if (!silent && logsScrollTops.screen === 0) restoreLogsScrollTop("screen", { reset: true });
  } catch (e) {
    if (seq !== screenrecordState.loadSeq) return;
    screenrecordState.loading = false;
    screenrecordState.loadingMore = false;
    setScreenrecordLoadingMoreUi(false);
    if (!silent && isLogsPageActive()) {
      setScreenrecordStatus(`${getUIText("screenrecord_load_failed", "Failed to load screen recordings")}: ${e.message || e}`, "error");
      showAppToast(e.message || getUIText("screenrecord_load_failed", "Failed to load screen recordings"), { tone: "error" });
    }
  }
}

export {
  downloadScreenrecordVideos,
  loadScreenrecordVideos,
  openScreenrecordPlayer,
  renderScreenrecordToolbar,
  renderScreenrecordVideos,
  scheduleScreenrecordWindowRender,
  screenrecordApiPath,
  screenrecordSelectedVideos,
  screenrecordShouldLoadMore,
  screenrecordState,
  toggleScreenrecordSelectAll,
  toggleScreenrecordSelection,
  uploadScreenrecordVideos,
};
