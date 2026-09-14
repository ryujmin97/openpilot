"use strict";

import { getWebSettingByKey, setWebSettingsByKeys } from "./state.js";

// Registry for compound preference controls. Generic bool/enum rows remain in
// The generic renderer handles bool/enum rows; multi-key controls register here independently.
globalThis.WebSettingsComponents = (() => {
  const components = new Map();

  function register(name, definition) {
    const key = String(name || "").trim();
    if (!key || !definition || typeof definition.render !== "function") {
      throw new TypeError("WebSettingsComponents.register requires a renderable component");
    }
    if (components.has(key)) throw new Error(`Web settings component already registered: ${key}`);
    components.set(key, Object.freeze({ ...definition }));
  }

  function definition(name) {
    return components.get(String(name || "")) || null;
  }

  function isVisible(name, fields, item = null) {
    const component = definition(name);
    if (!component) return false;
    if (typeof component.isVisible === "function") {
      return component.isVisible(item, fields) === true;
    }
    return (component.settingKeys || []).every((key) => Boolean(fields[key]));
  }

  function render(name, item) {
    return definition(name)?.render(item) || "";
  }

  function bind(root = document) {
    for (const component of components.values()) component.bind?.(root);
  }

  return Object.freeze({ register, isVisible, render, bind });
})();

globalThis.WebSettingsComponents.register("web-upload", {
  settingKeys: ["log_upload_target", "web_upload_url", "toss_upload_url", "toss_upload_token"],
  render() {
    const text = (key, fallback) => getUIText(key) || fallback;
    const target = String(getWebSettingByKey("log_upload_target", "carrot") || "carrot");
    const field = (targetName, key, type, titleKey, titleFallback, descKey, descFallback) => `
      <label class="web-settings-row web-settings-row--field" data-web-upload-target-fields="${targetName}" ${target === targetName ? "" : "hidden"}>
        <span class="web-settings-row__copy">
          <span class="web-settings-row__title">${escapeHtml(text(titleKey, titleFallback))}</span>
          <span class="web-settings-row__desc">${escapeHtml(text(descKey, descFallback))}</span>
        </span>
        <input class="web-settings-text" data-web-upload-field="${key}" type="${type}"
          ${type === "url" ? "inputmode=\"url\"" : "autocomplete=\"new-password\""}
          value="${escapeHtml(String(getWebSettingByKey(key, "") || ""))}" />
      </label>`;
    return `
      <div class="web-upload-settings" data-upload-target="${escapeHtml(target)}">
        <label class="web-settings-row web-settings-row--field">
          <span class="web-settings-row__copy">
            <span class="web-settings-row__title">${escapeHtml(text("web_log_upload_target", "Upload server"))}</span>
            <span class="web-settings-row__desc">${escapeHtml(text("web_log_upload_target_desc", "Choose where logs are uploaded."))}</span>
          </span>
          <select class="web-settings-select" data-web-upload-target aria-label="${escapeHtml(text("web_log_upload_target", "Upload server"))}">
            <option value="carrot" ${target === "carrot" ? "selected" : ""}>${escapeHtml(text("web_log_upload_target_carrot", "Carrot server"))}</option>
            <option value="toss" ${target === "toss" ? "selected" : ""}>${escapeHtml(text("web_log_upload_target_toss", "Toss server"))}</option>
            <option value="gdrive" ${target === "gdrive" ? "selected" : ""}>${escapeHtml(text("web_log_upload_target_gdrive", "Google Drive"))}</option>
          </select>
        </label>
        ${field("carrot", "web_upload_url", "url", "web_upload_url", "Carrot upload server", "web_upload_url_desc", "Carrot HTTPS API base URL with automatic sessions")}
        ${field("toss", "toss_upload_url", "url", "web_toss_upload_url", "Toss server URL", "web_toss_upload_url_desc", "Toss HTTPS API base URL")}
        ${field("toss", "toss_upload_token", "password", "web_toss_upload_token", "Toss access token", "web_toss_upload_token_desc", "Bearer token issued by the Toss server")}
        <div class="web-upload-settings__actions">
          <button class="btn btn-secondary web-upload-settings__test" type="button">${escapeHtml(text("web_upload_test", "Test connection"))}</button>
          <span class="web-upload-settings__status" aria-live="polite"></span>
        </div>
      </div>`;
  },
  bind(root = document) {
    const container = root.querySelector(".web-upload-settings");
    if (!container || container.dataset.bound === "1") return;
    container.dataset.bound = "1";
    const targetSelect = container.querySelector("[data-web-upload-target]");
    const fields = [...container.querySelectorAll("[data-web-upload-field]")];
    const status = container.querySelector(".web-upload-settings__status");
    const button = container.querySelector(".web-upload-settings__test");
    const currentTarget = () => {
      const value = targetSelect?.value;
      return value === "toss" || value === "gdrive" ? value : "carrot";
    };
    const syncTargetVisibility = () => {
      const target = currentTarget();
      container.dataset.uploadTarget = target;
      container.querySelectorAll("[data-web-upload-target-fields]").forEach((row) => {
        row.hidden = row.dataset.webUploadTargetFields !== target;
      });
    };
    const selectedValues = () => {
      const target = currentTarget();
      const values = { log_upload_target: target };
      fields.filter((input) => input.closest("[data-web-upload-target-fields]")?.dataset.webUploadTargetFields === target)
        .forEach((input) => { values[input.dataset.webUploadField] = input.value.trim(); });
      return values;
    };
    const saveSelected = () => setWebSettingsByKeys(selectedValues());

    targetSelect?.addEventListener("change", () => {
      syncTargetVisibility();
      saveSelected().catch((err) => {
        if (status) status.textContent = err?.message || String(err);
      });
    });
    fields.forEach((input) => {
      input.addEventListener("change", () => setWebSettingsByKeys({ [input.dataset.webUploadField]: input.value.trim() }).catch((err) => {
        if (status) status.textContent = err?.message || String(err);
      }));
    });
    button?.addEventListener("click", async () => {
      button.disabled = true;
      if (status) status.textContent = getUIText("web_upload_testing") || "Testing...";
      try {
        await saveSelected();
        const response = await fetch("/api/dashcam/upload/test", { method: "POST" });
        const payload = await response.json();
        if (!response.ok || payload?.ok === false) throw new Error(payload?.error || `HTTP ${response.status}`);
        const targetLabelKey = currentTarget() === "toss"
          ? "web_log_upload_target_toss"
          : currentTarget() === "gdrive"
            ? "web_log_upload_target_gdrive"
            : "web_log_upload_target_carrot";
        const targetLabel = getUIText(targetLabelKey) || currentTarget();
        if (status) status.textContent = `${targetLabel}: ${getUIText("web_upload_test_ok") || "Connection OK"}`;
      } catch (err) {
        if (status) status.textContent = `${getUIText("web_upload_test_failed") || "Connection failed"}: ${err?.message || err}`;
      } finally {
        button.disabled = false;
      }
    });
    syncTargetVisibility();
  },
});

globalThis.WebSettingsComponents.register("web-gdrive-connect", {
  render() {
    const text = (key, fallback) => getUIText(key) || fallback;
    return `
      <div class="web-gdrive-settings" data-gdrive-status="unknown">
        <label class="web-settings-row web-settings-row--field">
          <span class="web-settings-row__copy">
            <span class="web-settings-row__title">${escapeHtml(text("web_gdrive_client_id", "Client ID"))}</span>
            <span class="web-settings-row__desc">${escapeHtml(text("web_gdrive_client_id_desc", "Google Cloud OAuth client ID (Desktop app type)."))}</span>
          </span>
          <input class="web-settings-text" data-gdrive-field="client_id" type="text" autocomplete="off" />
        </label>
        <label class="web-settings-row web-settings-row--field">
          <span class="web-settings-row__copy">
            <span class="web-settings-row__title">${escapeHtml(text("web_gdrive_client_secret", "Client Secret"))}</span>
            <span class="web-settings-row__desc">${escapeHtml(text("web_gdrive_client_secret_desc", "OAuth client secret issued with the client ID."))}</span>
          </span>
          <input class="web-settings-text" data-gdrive-field="client_secret" type="password" autocomplete="new-password" />
        </label>
        <div class="web-gdrive-settings__actions">
          <button class="btn btn-secondary web-gdrive-settings__connect" type="button">${escapeHtml(text("web_gdrive_connect", "Connect Google account"))}</button>
          <button class="btn btn-secondary web-gdrive-settings__disconnect" type="button" hidden>${escapeHtml(text("web_gdrive_disconnect", "Disconnect"))}</button>
        </div>
        <div class="web-gdrive-settings__code" hidden>
          <span class="web-gdrive-settings__code-label">${escapeHtml(text("web_gdrive_code_hint", "Go to the link below and enter this code:"))}</span>
          <span class="web-gdrive-settings__code-value" data-gdrive-code></span>
          <a class="web-gdrive-settings__code-link" data-gdrive-link href="https://www.google.com/device" target="_blank" rel="noopener">${escapeHtml(text("web_gdrive_open_link", "Open verification page"))}</a>
        </div>
        <span class="web-gdrive-settings__status" aria-live="polite"></span>
      </div>`;
  },
  bind(root = document) {
    const container = root.querySelector(".web-gdrive-settings");
    if (!container || container.dataset.bound === "1") return;
    container.dataset.bound = "1";

    const clientIdInput = container.querySelector('[data-gdrive-field="client_id"]');
    const clientSecretInput = container.querySelector('[data-gdrive-field="client_secret"]');
    const connectBtn = container.querySelector(".web-gdrive-settings__connect");
    const disconnectBtn = container.querySelector(".web-gdrive-settings__disconnect");
    const codeBox = container.querySelector(".web-gdrive-settings__code");
    const codeValue = container.querySelector("[data-gdrive-code]");
    const codeLink = container.querySelector("[data-gdrive-link]");
    const status = container.querySelector(".web-gdrive-settings__status");

    let pollTimer = null;
    const stopPolling = () => {
      if (pollTimer) { clearTimeout(pollTimer); pollTimer = null; }
    };
    const setStatusText = (msg) => { if (status) status.textContent = msg || ""; };

    const applyStatus = (data) => {
      const connected = Boolean(data?.connected);
      container.dataset.gdriveStatus = connected ? "connected" : (data?.status || "disconnected");
      if (connectBtn) connectBtn.hidden = connected;
      if (disconnectBtn) disconnectBtn.hidden = !connected;
      if (connected) {
        if (codeBox) codeBox.hidden = true;
        stopPolling();
        setStatusText(getUIText("web_gdrive_connected") || "Google Drive connected");
      } else if (data?.status === "pending" && data?.user_code) {
        if (codeBox) codeBox.hidden = false;
        if (codeValue) codeValue.textContent = data.user_code;
        if (codeLink && data.verification_uri) codeLink.href = data.verification_uri;
        setStatusText(getUIText("web_gdrive_waiting") || "Waiting for Google authorization...");
      } else {
        if (codeBox) codeBox.hidden = true;
        setStatusText(data?.last_error || "");
      }
    };

    const fetchStatus = async () => {
      try {
        const res = await fetch("/api/gdrive/status");
        const data = await res.json();
        applyStatus(data);
        return data;
      } catch (err) {
        setStatusText(err?.message || String(err));
        return null;
      }
    };

    const pollToken = (deviceCode, intervalSec) => {
      stopPolling();
      pollTimer = setTimeout(async () => {
        try {
          const res = await fetch("/api/gdrive/token", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ device_code: deviceCode }),
          });
          const data = await res.json();
          if (data?.connected) {
            applyStatus(data);
            return;
          }
          if (data?.expired) {
            if (codeBox) codeBox.hidden = true;
            setStatusText(getUIText("web_gdrive_expired") || "The code has expired. Please try connecting again.");
            return;
          }
          if (data?.pending) {
            pollToken(deviceCode, intervalSec);
            return;
          }
          setStatusText(data?.error || (getUIText("web_gdrive_connect_failed") || "Connection failed"));
        } catch (_err) {
          pollToken(deviceCode, intervalSec);
        }
      }, Math.max(2, Number(intervalSec) || 5) * 1000);
    };

    connectBtn?.addEventListener("click", async () => {
      const clientId = clientIdInput?.value.trim() || "";
      const clientSecret = clientSecretInput?.value.trim() || "";
      if (!clientId) {
        setStatusText(getUIText("web_gdrive_missing_client_id") || "Enter the client ID first.");
        return;
      }
      connectBtn.disabled = true;
      setStatusText(getUIText("web_gdrive_requesting") || "Requesting a code...");
      try {
        const res = await fetch("/api/gdrive/device", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ client_id: clientId, client_secret: clientSecret }),
        });
        const data = await res.json();
        if (!res.ok || data?.ok === false) throw new Error(data?.error || `HTTP ${res.status}`);
        if (codeBox) codeBox.hidden = false;
        if (codeValue) codeValue.textContent = data.user_code || "";
        if (codeLink && data.verification_uri) codeLink.href = data.verification_uri;
        setStatusText(getUIText("web_gdrive_waiting") || "Waiting for Google authorization...");
        pollToken(data.device_code, data.interval);
      } catch (err) {
        setStatusText(err?.message || String(err));
      } finally {
        connectBtn.disabled = false;
      }
    });

    disconnectBtn?.addEventListener("click", async () => {
      disconnectBtn.disabled = true;
      try {
        await fetch("/api/gdrive/disconnect", { method: "POST" });
      } catch (_err) {
        // ignore network error; status refresh below reflects actual server state
      } finally {
        disconnectBtn.disabled = false;
        stopPolling();
        fetchStatus();
      }
    });

    fetchStatus();
  },
});
