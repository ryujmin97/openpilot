"use strict";

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
  ].join("|")).join("\n");
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
