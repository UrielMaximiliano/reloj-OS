(() => {
  "use strict";

  const state = {
    devices: [],
    selectedDevice: null,
    captures: [],
    busy: new Set(),
  };

  const $ = (id) => document.getElementById(id);

  const elements = {
    alert: $("appAlert"),
    scanButton: $("scanButton"),
    scanStatus: $("scanStatus"),
    scanStatusDot: $("scanStatusDot"),
    devicesList: $("devicesList"),
    deviceEmpty: $("deviceEmpty"),
    deviceDetails: $("deviceDetails"),
    selectedState: $("selectedState"),
    selectedName: $("selectedName"),
    selectedAddress: $("selectedAddress"),
    selectedRssi: $("selectedRssi"),
    selectedProfile: $("selectedProfile"),
    inspectButton: $("inspectButton"),
    batteryButton: $("batteryButton"),
    batteryResult: $("batteryResult"),
    gattResult: $("gattResult"),
    refreshCapturesButton: $("refreshCapturesButton"),
    capturesList: $("capturesList"),
    capturePreviewMeta: $("capturePreviewMeta"),
    captureData: $("captureData"),
  };

  function setBusy(key, busy) {
    if (busy) {
      state.busy.add(key);
    } else {
      state.busy.delete(key);
    }
    elements.scanButton.disabled = state.busy.has("scan");
    elements.inspectButton.disabled = state.busy.has("inspect");
    elements.batteryButton.disabled = state.busy.has("battery");
    elements.refreshCapturesButton.disabled = state.busy.has("captures");
  }

  function showAlert(message, tone = "error") {
    elements.alert.textContent = message;
    elements.alert.dataset.tone = tone;
    elements.alert.hidden = false;
  }

  function clearAlert() {
    elements.alert.textContent = "";
    elements.alert.hidden = true;
  }

  function setScanStatus(message, tone = "muted") {
    elements.scanStatus.textContent = message;
    elements.scanStatusDot.className = `status-dot ${tone}`;
  }

  function setButtonLabel(button, label) {
    const text = button.querySelector("span:last-child");
    if (text) text.textContent = label;
  }

  function displayName(device) {
    return device.name || device.local_name || "Unnamed device";
  }

  function addressFor(device) {
    return device.address || device.identifier || "Unknown identifier";
  }

  function formatRssi(value) {
    return typeof value === "number" ? `${value} dBm` : "—";
  }

  function text(value, fallback = "—") {
    if (value === null || value === undefined || value === "") return fallback;
    return String(value);
  }

  async function api(path, options = {}) {
    const controller = new AbortController();
    const timer = window.setTimeout(() => controller.abort(), options.timeout || 30000);
    try {
      const response = await fetch(path, {
        ...options,
        signal: controller.signal,
        headers: { Accept: "application/json", ...(options.headers || {}) },
      });
      const contentType = response.headers.get("content-type") || "";
      const payload = contentType.includes("json") ? await response.json() : await response.text();
      if (!response.ok) {
        const errorMessage = payload && payload.error && payload.error.message
          ? payload.error.message
          : payload && payload.detail
            ? typeof payload.detail === "string" ? payload.detail : "The server rejected the request."
            : `Request failed with HTTP ${response.status}.`;
        throw new Error(errorMessage);
      }
      return payload;
    } catch (error) {
      if (error.name === "AbortError") throw new Error("The local backend did not respond in time.");
      if (error instanceof TypeError) throw new Error("The Windows backend is unreachable. Check the LAN address and that uvicorn is running.");
      throw error;
    } finally {
      window.clearTimeout(timer);
    }
  }

  function emptyState(title, detail, glyph = "⌁") {
    const wrapper = document.createElement("div");
    wrapper.className = "empty-state";
    const mark = document.createElement("span");
    mark.className = "empty-glyph";
    mark.setAttribute("aria-hidden", "true");
    mark.textContent = glyph;
    const heading = document.createElement("strong");
    heading.textContent = title;
    const copy = document.createElement("span");
    copy.textContent = detail;
    wrapper.append(mark, heading, copy);
    return wrapper;
  }

  function renderDevices(devices) {
    elements.devicesList.replaceChildren();
    if (!devices.length) {
      elements.devicesList.append(emptyState("No devices in view", "The scan completed without nearby advertisements."));
      return;
    }
    devices.forEach((device, index) => {
      const item = document.createElement("article");
      item.className = "device-row";
      const info = document.createElement("div");
      info.className = "device-row-info";
      const name = document.createElement("strong");
      name.textContent = displayName(device);
      const address = document.createElement("span");
      address.textContent = addressFor(device);
      info.append(name, address);
      const meta = document.createElement("div");
      meta.className = "device-row-meta";
      const rssi = document.createElement("span");
      rssi.textContent = formatRssi(device.rssi);
      const candidate = document.createElement("span");
      candidate.className = device.possible_candidate ? "candidate-badge" : "quiet-badge";
      candidate.textContent = device.possible_candidate ? "CANDIDATE" : "SEEN";
      meta.append(rssi, candidate);
      const button = document.createElement("button");
      button.type = "button";
      button.className = "device-row-action";
      button.textContent = "Select";
      button.dataset.deviceIndex = String(index);
      button.addEventListener("click", () => selectDevice(device));
      item.append(info, meta, button);
      elements.devicesList.append(item);
    });
  }

  function selectDevice(device) {
    state.selectedDevice = device;
    elements.deviceEmpty.hidden = true;
    elements.deviceDetails.hidden = false;
    elements.selectedState.textContent = "SELECTED / IDLE";
    elements.selectedName.textContent = displayName(device);
    elements.selectedAddress.textContent = addressFor(device);
    elements.selectedRssi.textContent = formatRssi(device.rssi);
    elements.selectedProfile.textContent = device.possible_candidate ? "FORGE CANDIDATE" : "BLE ADVERTISEMENT";
    elements.batteryResult.replaceChildren();
    elements.gattResult.replaceChildren();
    elements.gattResult.append(resultPlaceholder("GATT map appears here after inspection."));
    clearAlert();
    elements.inspectButton.focus();
  }

  function resultPlaceholder(message) {
    const wrapper = document.createElement("div");
    wrapper.className = "result-placeholder";
    const lineOne = document.createElement("span");
    lineOne.className = "result-placeholder-line";
    const lineTwo = document.createElement("span");
    lineTwo.className = "result-placeholder-line short";
    const copy = document.createElement("small");
    copy.textContent = message;
    wrapper.append(lineOne, lineTwo, copy);
    return wrapper;
  }

  function devicePath(suffix = "") {
    if (!state.selectedDevice) throw new Error("Select a device first.");
    return `/devices/${encodeURIComponent(addressFor(state.selectedDevice))}${suffix}`;
  }

  function renderSummary(summary) {
    const wrapper = document.createElement("div");
    wrapper.className = "summary-grid";
    [
      ["Services", summary && summary.services],
      ["Custom", summary && summary.custom_services],
      ["Characteristics", summary && summary.characteristics],
      ["Readable", summary && summary.read],
      ["Writable", summary && summary.write],
      ["Notify", summary && summary.notify],
    ].forEach(([label, value]) => {
      const cell = document.createElement("div");
      const small = document.createElement("small");
      small.textContent = label;
      const strong = document.createElement("strong");
      strong.textContent = text(value, "0");
      cell.append(small, strong);
      wrapper.append(cell);
    });
    return wrapper;
  }

  function renderGATT(payload) {
    elements.gattResult.replaceChildren();
    if (payload.summary) elements.gattResult.append(renderSummary(payload.summary));
    const services = Array.isArray(payload.services) ? payload.services : [];
    if (!services.length) {
      elements.gattResult.append(emptyState("No GATT services returned", "The backend connected but returned no service metadata.", "∅"));
      return;
    }
    services.forEach((service) => {
      const details = document.createElement("details");
      details.className = "gatt-service";
      const summary = document.createElement("summary");
      const name = document.createElement("strong");
      name.textContent = service.name || service.description || "Unknown service";
      const uuid = document.createElement("code");
      uuid.textContent = text(service.uuid);
      summary.append(name, uuid);
      details.append(summary);
      const serviceMeta = document.createElement("p");
      serviceMeta.className = "muted-copy";
      serviceMeta.textContent = `${text(service.service_type, "UNKNOWN")} · ${text(service.description, "No description")}`;
      details.append(serviceMeta);
      const chars = Array.isArray(service.characteristics) ? service.characteristics : [];
      chars.forEach((characteristic) => {
        const row = document.createElement("div");
        row.className = "characteristic-row";
        const heading = document.createElement("strong");
        heading.textContent = characteristic.description || characteristic.uuid || "Characteristic";
        const uuidLine = document.createElement("code");
        uuidLine.textContent = text(characteristic.uuid);
        const props = document.createElement("span");
        props.className = "property-list";
        props.textContent = Array.isArray(characteristic.properties) ? characteristic.properties.join(" · ").toUpperCase() : "NO PROPERTIES";
        row.append(heading, uuidLine, props);
        details.append(row);
      });
      elements.gattResult.append(details);
    });
  }

  function renderBattery(payload) {
    elements.batteryResult.replaceChildren();
    const card = document.createElement("div");
    card.className = "read-result";
    const title = document.createElement("strong");
    title.textContent = "Battery read result";
    card.append(title);
    if (payload && payload.available === false) {
      const reason = document.createElement("p");
      reason.textContent = `Unavailable: ${text(payload.reason, "the device did not expose a safe Battery Level")}`;
      card.append(reason);
    } else {
      const percent = payload && payload.interpreted && payload.interpreted.battery_percent;
      const value = document.createElement("div");
      value.className = "battery-value";
      value.textContent = typeof percent === "number" && percent >= 0 && percent <= 100 ? `${percent}%` : "READ COMPLETE";
      card.append(value);
      const detail = document.createElement("p");
      detail.textContent = `${text(payload && payload.timestamp, "Timestamp unavailable")} · ${text(payload && payload.raw_hex, "raw bytes unavailable")}`;
      card.append(detail);
    }
    elements.batteryResult.append(card);
  }

  function formatCapture(payload) {
    if (!payload) return "No capture data returned.";
    if (payload.format === "jsonl" && Array.isArray(payload.rows)) return JSON.stringify(payload.rows, null, 2);
    if (Object.prototype.hasOwnProperty.call(payload, "data")) return JSON.stringify(payload.data, null, 2);
    return JSON.stringify(payload, null, 2);
  }

  function renderCaptures(captures) {
    elements.capturesList.replaceChildren();
    if (!captures.length) {
      elements.capturesList.append(emptyState("No captures loaded", "Local JSON and JSONL observations will appear here.", "▱"));
      return;
    }
    captures.forEach((capture) => {
      const row = document.createElement("button");
      row.type = "button";
      row.className = "capture-row";
      const name = document.createElement("strong");
      name.textContent = capture.id || "Unnamed capture";
      const meta = document.createElement("span");
      meta.textContent = `${text(capture.type, "unknown").toUpperCase()} · ${text(capture.size, "?")} bytes`;
      row.append(name, meta);
      row.addEventListener("click", () => openCapture(capture.id));
      elements.capturesList.append(row);
    });
  }

  async function openCapture(id) {
    if (!id) return;
    try {
      clearAlert();
      const payload = await api(`/captures/${encodeURIComponent(id)}`);
      elements.capturePreviewMeta.textContent = payload.format ? payload.format.toUpperCase() : "OPEN";
      elements.captureData.textContent = formatCapture(payload);
    } catch (error) {
      showAlert(`Could not open capture: ${error.message}`);
    }
  }

  async function scan() {
    setBusy("scan", true);
    setScanStatus("Scanning nearby advertisements…", "active");
    setButtonLabel(elements.scanButton, "Scanning…");
    clearAlert();
    try {
      const devices = await api("/devices", { timeout: 25000 });
      state.devices = Array.isArray(devices) ? devices : [];
      renderDevices(state.devices);
      setScanStatus(`${state.devices.length} device${state.devices.length === 1 ? "" : "s"} found.`, "ready");
    } catch (error) {
      state.devices = [];
      renderDevices([]);
      setScanStatus("Scan failed. The local backend needs attention.", "error");
      showAlert(`Scan unavailable: ${error.message}`);
    } finally {
      setBusy("scan", false);
      setButtonLabel(elements.scanButton, "Scan");
    }
  }

  async function inspect() {
    setBusy("inspect", true);
    elements.selectedState.textContent = "INSPECTING…";
    elements.gattResult.replaceChildren(resultPlaceholder("Connecting and enumerating GATT…"));
    clearAlert();
    try {
      renderGATT(await api(devicePath("/services"), { timeout: 30000 }));
      elements.selectedState.textContent = "INSPECTED / DISCONNECTED";
    } catch (error) {
      elements.selectedState.textContent = "INSPECTION FAILED";
      elements.gattResult.replaceChildren(emptyState("GATT inspection failed", error.message, "!"));
      showAlert(`GATT inspection failed: ${error.message}`);
    } finally {
      setBusy("inspect", false);
    }
  }

  async function readBattery() {
    setBusy("battery", true);
    elements.selectedState.textContent = "READING BATTERY…";
    elements.batteryResult.replaceChildren(resultPlaceholder("Performing one safe read through Windows…"));
    clearAlert();
    try {
      renderBattery(await api(devicePath("/battery"), { timeout: 30000 }));
      elements.selectedState.textContent = "READ COMPLETE / DISCONNECTED";
    } catch (error) {
      elements.selectedState.textContent = "BATTERY READ FAILED";
      elements.batteryResult.replaceChildren(emptyState("Battery read failed", error.message, "!"));
      showAlert(`Battery read failed: ${error.message}`);
    } finally {
      setBusy("battery", false);
    }
  }

  async function loadCaptures() {
    setBusy("captures", true);
    try {
      const captures = await api("/captures");
      state.captures = Array.isArray(captures) ? captures : [];
      renderCaptures(state.captures);
    } catch (error) {
      renderCaptures([]);
      showAlert(`Capture browser unavailable: ${error.message}`);
    } finally {
      setBusy("captures", false);
    }
  }

  elements.scanButton.addEventListener("click", scan);
  elements.inspectButton.addEventListener("click", inspect);
  elements.batteryButton.addEventListener("click", readBattery);
  elements.refreshCapturesButton.addEventListener("click", loadCaptures);
  window.addEventListener("online", () => showAlert("Network connection restored. Retry the last observation when ready.", "success"));
  window.addEventListener("offline", () => showAlert("Safari is offline. The Windows backend must be reachable on the local network."));

  if ("serviceWorker" in navigator && (window.location.protocol === "https:" || window.location.hostname === "localhost")) {
    navigator.serviceWorker.register("/service-worker.js").catch(() => undefined);
  }
  loadCaptures();
})();
