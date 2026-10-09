const icons = {
  road: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M8 3 5 21M16 3l3 18M12 5v3m0 3v3m0 3v2"/></svg>`,
  home: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="m3 10 9-7 9 7v10a1 1 0 0 1-1 1h-5v-7H9v7H4a1 1 0 0 1-1-1Z"/></svg>`,
  camera: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 7h3l2-3h6l2 3h3a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V9a2 2 0 0 1 2-2Z"/><circle cx="12" cy="13" r="4"/></svg>`,
  list: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/></svg>`,
  map: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="m3 6 6-3 6 3 6-3v15l-6 3-6-3-6 3Z"/><path d="M9 3v15M15 6v15"/></svg>`,
  bot: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="4" y="7" width="16" height="13" rx="3"/><path d="M9 12h.01M15 12h.01M9 16h6M12 7V3M9 3h6"/></svg>`,
  settings: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .34 1.88l.06.06-2.83 2.83-.06-.06a1.7 1.7 0 0 0-1.88-.34 1.7 1.7 0 0 0-1 1.55V21h-4v-.08a1.7 1.7 0 0 0-1-1.55 1.7 1.7 0 0 0-1.88.34l-.06.06-2.83-2.83.06-.06A1.7 1.7 0 0 0 4.6 15a1.7 1.7 0 0 0-1.55-1H3v-4h.08a1.7 1.7 0 0 0 1.55-1 1.7 1.7 0 0 0-.34-1.88l-.06-.06 2.83-2.83.06.06A1.7 1.7 0 0 0 9 4.6a1.7 1.7 0 0 0 1-1.55V3h4v.08a1.7 1.7 0 0 0 1 1.55 1.7 1.7 0 0 0 1.88-.34l.06-.06 2.83 2.83-.06.06A1.7 1.7 0 0 0 19.4 9a1.7 1.7 0 0 0 1.55 1H21v4h-.08a1.7 1.7 0 0 0-1.55 1Z"/></svg>`,
  dashboard: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>`,
  chart: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/></svg>`,
  bell: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9M10 21h4"/></svg>`,
  search: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/></svg>`,
  plus: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 5v14M5 12h14"/></svg>`,
  arrow: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="m9 18 6-6-6-6"/></svg>`,
  pin: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M20 10c0 5-8 11-8 11S4 15 4 10a8 8 0 1 1 16 0Z"/><circle cx="12" cy="10" r="2.5"/></svg>`,
  clock: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>`,
  shield: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 3 4 6v6c0 5 3.5 8 8 9 4.5-1 8-4 8-9V6Z"/><path d="m9 12 2 2 4-4"/></svg>`,
  cloud: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M6 18h12a4 4 0 0 0 .5-8 7 7 0 0 0-13-1A4.5 4.5 0 0 0 6 18Z"/><path d="m9 14 3-3 3 3M12 11v8"/></svg>`,
  check: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m5 12 4 4L19 6"/></svg>`,
  upload: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 16V4m0 0L7 9m5-5 5 5M4 15v4a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-4"/></svg>`,
  x: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="m6 6 12 12M18 6 6 18"/></svg>`,
  send: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/></svg>`,
  eye: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/></svg>`,
  spark: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="m12 3 1.6 4.4L18 9l-4.4 1.6L12 15l-1.6-4.4L6 9l4.4-1.6ZM19 15l.8 2.2L22 18l-2.2.8L19 21l-.8-2.2L16 18l2.2-.8Z"/></svg>`,
  offline: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="m3 3 18 18M8.5 8.5A6 6 0 0 1 18 12M5 12a7 7 0 0 1 .7-3M8 16h8M11 20h2"/></svg>`,
  sun: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>`,
  menu: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 7h16M4 12h16M4 17h16"/></svg>`,
};

const seedReports = [
  { id: "RD-2026-00142", type: "Pothole", severity: "HIGH", confidence: 94, priority: "P1", status: "IN_PROGRESS", sync: "SYNCED", address: "Outer Ring Rd, Mahadevapura", zone: "East Zone", lat: 12.9964, lng: 77.6968, accuracy: 7.4, time: "Today, 10:42 AM", image: "pothole", assignee: "Arjun Rao", initials: "AR", supports: 6, lighting: "Day", comments: ["Crew scheduled for the afternoon shift."], created: "24 Aug 2026" },
  { id: "RD-2026-00139", type: "Linear crack", severity: "MEDIUM", confidence: 87, priority: "P2", status: "ASSIGNED", sync: "SYNCED", address: "MG Road, Ashok Nagar", zone: "Central Zone", lat: 12.9756, lng: 77.6064, accuracy: 5.8, time: "Today, 9:18 AM", image: "crack", assignee: "Meera S.", initials: "MS", supports: 3, lighting: "Night / low light", comments: ["Low-light evidence manually reviewed."], created: "24 Aug 2026" },
  { id: "RD-2026-00136", type: "Pothole", severity: "LOW", confidence: 91, priority: "P3", status: "SUBMITTED", sync: "SYNCED", address: "8th Main, Indiranagar", zone: "East Zone", lat: 12.9783, lng: 77.6408, accuracy: 8.1, time: "Yesterday, 6:34 PM", image: "pothole", assignee: "Unassigned", initials: "--", supports: 1, lighting: "Day", comments: [], created: "23 Aug 2026" },
  { id: "RD-2026-00131", type: "Alligator crack", severity: "HIGH", confidence: 89, priority: "P1", status: "VERIFIED", sync: "SYNCED", address: "Mysore Road, Bapuji Nagar", zone: "West Zone", lat: 12.9534, lng: 77.5432, accuracy: 6.2, time: "22 Aug, 4:12 PM", image: "crack", assignee: "Neha K.", initials: "NK", supports: 8, lighting: "Night / low light", comments: ["Repair evidence accepted."], created: "22 Aug 2026" },
  { id: "RD-2026-00127", type: "Pothole", severity: "MEDIUM", confidence: 84, priority: "P2", status: "CLOSED", sync: "SYNCED", address: "Bellary Rd, Hebbal", zone: "North Zone", lat: 13.0358, lng: 77.597, accuracy: 9.5, time: "20 Aug, 11:30 AM", image: "pothole", assignee: "Arjun Rao", initials: "AR", supports: 4, lighting: "Day", comments: ["Repair verified and case closed."], created: "20 Aug 2026" },
];

const stored = (() => {
  try { return JSON.parse(localStorage.getItem("roadlens-demo") || "null"); } catch { return null; }
})();

const state = Object.assign({
  role: "field",
  view: "home",
  reports: seedReports,
  selectedReportId: null,
  reportSearch: "",
  severityFilter: "ALL",
  statusFilter: "ALL",
  captureMode: "pothole",
  customImage: null,
  analysisStage: "idle",
  analysisFile: null,
  analysisResult: null,
  analysisError: null,
  evidenceMode: "annotated",
  online: true,
  autoSync: true,
  nightEnhance: true,
  cvrLabel: "Not configured",
  language: "English",
  messages: [
    { from: "bot", text: "Hi Priya. I can explain the active inspection using only its saved details. What would you like to know?", time: "10:44 AM" },
  ],
}, stored || {});

state.customImage = null;
state.analysisStage = "idle";
state.analysisFile = null;
state.analysisResult = null;
state.analysisError = null;
state.selectedReportId = null;

const app = document.querySelector("#app");
const toastRegion = document.querySelector("#toast-region");
history.scrollRestoration = "manual";
window.addEventListener("load", () => window.scrollTo(0, 0), { once: true });

const pageInfo = {
  home: ["Field overview", "Road inspections at a glance"],
  capture: ["New inspection", "Capture, locate and assess road damage"],
  inspections: ["Inspections", "Evidence and synchronization history"],
  map: ["Damage map", "Location-aware view of reported damage"],
  assistant: ["RoadLens assistant", "Grounded answers in your selected inspection"],
  settings: ["Settings", "Offline behavior, language and configuration"],
  overview: ["Authority command center", "Bengaluru roads · Monday, 24 August"],
  reports: ["Reports", "Review, assign and resolve submitted cases"],
  analytics: ["Operations analytics", "Damage trends and resolution performance"],
};

const fieldNav = [
  ["home", "Overview", "home"], ["capture", "New inspection", "camera"], ["inspections", "Inspections", "list"],
  ["map", "Damage map", "map"], ["assistant", "AI assistant", "bot"], ["settings", "Settings", "settings"],
];
const authorityNav = [
  ["overview", "Command center", "dashboard"], ["reports", "Reports", "list"], ["map", "Damage map", "map"],
  ["analytics", "Analytics", "chart"], ["settings", "Settings", "settings"],
];

function save() {
  const safe = { ...state, customImage: null, analysisFile: null, analysisResult: null, analysisError: null, analysisStage: "idle", selectedReportId: null };
  localStorage.setItem("roadlens-demo", JSON.stringify(safe));
}

function esc(value) {
  return String(value).replace(/[&<>'"]/g, char => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" }[char]));
}

function pill(value) {
  const label = value.replaceAll("_", " ");
  return `<span class="pill ${value.toLowerCase()}">${label}</span>`;
}

function imageStyle(reportOrMode) {
  const mode = typeof reportOrMode === "string" ? reportOrMode : reportOrMode.image;
  return mode === "crack" ? "assets/crack-night-evidence.png" : "assets/pothole-evidence.png";
}

function navMarkup() {
  const nav = state.role === "field" ? fieldNav : authorityNav;
  return nav.map(([view, label, icon]) => `
    <button class="nav-item ${state.view === view ? "active" : ""}" data-view="${view}">
      <span class="nav-icon">${icons[icon]}</span><span>${label}</span>
      ${view === "inspections" && state.reports.some(r => r.sync === "PENDING") ? `<span class="nav-badge">${state.reports.filter(r => r.sync === "PENDING").length}</span>` : ""}
    </button>`).join("");
}

function sidebar() {
  return `<aside class="sidebar" id="sidebar">
    <div class="brand"><span class="brand-mark">${icons.road}</span><span class="brand-name">Road<span>Lens</span></span></div>
    <div class="nav-label">${state.role === "field" ? "Field workspace" : "Authority workspace"}</div>
    <nav class="side-nav" aria-label="Primary navigation">${navMarkup()}</nav>
    <div class="mobile-workspace">
      <div class="nav-label">Switch workspace</div>
      <div class="role-switch">
        <button class="role-option ${state.role === "field" ? "active" : ""}" data-role="field">Field app</button>
        <button class="role-option ${state.role === "authority" ? "active" : ""}" data-role="authority">Authority</button>
      </div>
    </div>
    <div class="sidebar-bottom">
      <div class="sync-card">
        <div class="sync-row"><span class="sync-title"><i class="pulse-dot"></i>${state.online ? "Online · Synced" : "Offline mode"}</span><button class="text-button" style="color:#acd5c4" data-action="toggle-online">${state.online ? "Go offline" : "Reconnect"}</button></div>
        <p>${state.online ? "Last sync moments ago · all records secure" : `${state.reports.filter(r => r.sync === "PENDING").length} inspection waiting to sync`}</p>
      </div>
    </div>
  </aside>`;
}

function topbar() {
  const [title, subtitle] = pageInfo[state.view] || ["RoadLens", "Road operations"];
  return `<header class="topbar">
    <button class="icon-button mobile-menu" data-action="toggle-menu" aria-label="Open menu">${icons.menu}</button>
    <div class="page-heading"><h1>${title}</h1><p>${subtitle}</p></div>
    <div class="top-actions">
      <div class="role-switch" aria-label="Switch workspace">
        <button class="role-option ${state.role === "field" ? "active" : ""}" data-role="field">Field app</button>
        <button class="role-option ${state.role === "authority" ? "active" : ""}" data-role="authority">Authority</button>
      </div>
      <button class="icon-button" data-action="notifications" aria-label="Notifications">${icons.bell}<i class="notification-dot"></i></button>
      <div class="avatar" title="Priya Nair">PN</div>
    </div>
  </header>`;
}

function mobileBottom() {
  const items = state.role === "field"
    ? [["home","home"],["inspections","list"],["capture","camera"],["map","map"],["assistant","bot"]]
    : [["overview","dashboard"],["reports","list"],["map","map"],["analytics","chart"],["settings","settings"]];
  return `<nav class="mobile-bottom" aria-label="Mobile navigation">${items.map(([view, icon], i) => `<button aria-label="${view}" class="mobile-nav ${view === state.view ? "active" : ""} ${state.role === "field" && i === 2 ? "capture-main" : ""}" data-view="${view}">${icons[icon]}</button>`).join("")}</nav>`;
}

function statCard(label, value, note, icon, tint = "var(--mint)") {
  return `<article class="stat-card" style="--tint:${tint}"><div class="stat-top"><span class="stat-label">${label}</span><span class="stat-icon">${icons[icon]}</span></div><div class="stat-value">${value}</div><div class="stat-note">${note}</div></article>`;
}

function inspectionCard(report) {
  return `<article class="inspection-card" data-report="${report.id}">
    <div class="inspection-photo" style="background-image:url('${imageStyle(report)}')">${pill(report.severity)}<span class="inspection-id">${report.id}</span></div>
    <div class="card-body"><div class="card-title-row"><h3>${report.type}</h3>${pill(report.status)}</div>
    <p>${report.address}</p><div class="card-meta"><span>${report.confidence}% confidence</span><span>${report.time}</span></div></div>
  </article>`;
}

function fieldHome() {
  const pending = state.reports.filter(r => r.sync === "PENDING").length;
  return `<section>
    <p class="eyebrow">Good morning, Priya</p><h2 class="display-title">Every safer street starts with a clear signal.</h2>
    <p class="display-subtitle">Capture road damage, verify the AI result, and send structured evidence to the right maintenance team—even when the network drops.</p>
    <div class="grid stats-grid">
      ${statCard("Inspections", state.reports.length + 19, `<span class="trend-up">+12%</span> this week`, "camera")}
      ${statCard("Pending sync", pending, pending ? "Saved safely on this device" : "Everything is up to date", "cloud", "#fff0cf")}
      ${statCard("High severity", state.reports.filter(r=>r.severity==="HIGH").length + 3, "Requires prompt review", "shield", "#fde0da")}
      ${statCard("Resolution rate", "78%", "14 cases closed this month", "check", "#dceaf0")}
    </div>
    <div class="grid home-grid">
      <article class="panel hero-scan"><div class="scan-gridlines"></div><div class="hero-content">
        <span class="hero-chip"><i class="pulse-dot"></i> Real ONNX model ready</span><h2>See damage.<br/>Start the fix.</h2>
        <p>The exact selected image is decoded, letterboxed, analyzed, filtered and mapped back to its original coordinates.</p>
        <div class="hero-actions"><button class="button primary" data-view="capture">${icons.camera} Start inspection</button><button class="button light" data-action="demo-night">${icons.sun} Try low-light sample</button></div>
      </div></article>
      <article class="panel activity-panel"><div class="panel-inner"><div class="mini-head"><h3>Live activity</h3><button class="text-button" data-view="inspections">View all</button></div>
        <div class="activity-list">
          <div class="activity-item"><span class="activity-icon">${icons.check}</span><div class="activity-copy"><strong>Inspection synced</strong><span>RD-2026-00142 · just now</span></div></div>
          <div class="activity-item"><span class="activity-icon coral">${icons.shield}</span><div class="activity-copy"><strong>High severity flagged</strong><span>Outer Ring Rd · 18 min ago</span></div></div>
          <div class="activity-item"><span class="activity-icon">${icons.bot}</span><div class="activity-copy"><strong>Authority response</strong><span>Repair assigned · 42 min ago</span></div></div>
          <div class="activity-item"><span class="activity-icon">${icons.cloud}</span><div class="activity-copy"><strong>Background sync complete</strong><span>8 inspections uploaded</span></div></div>
        </div>
      </div></article>
    </div>
    <div class="section-head"><div><h2>Recent inspections</h2><p>Your latest field evidence and its current status</p></div><button class="text-button" data-view="inspections">See inspection history →</button></div>
    <div class="grid recent-grid">${state.reports.slice(0,3).map(inspectionCard).join("")}</div>
  </section>`;
}

function captureView() {
  if (state.analysisStage === "success") return resultView();
  if (["noDetection", "invalidImage", "error"].includes(state.analysisStage)) return analysisOutcomeView();
  const isNight = state.captureMode === "crack";
  const bg = state.customImage ? `style="background-image:url('${state.customImage}')"` : "";
  const scanning = state.analysisStage === "loading";
  return `<section>
    <p class="eyebrow">Real-model inspection</p><h2 class="display-title">Choose the road image the model should analyze.</h2>
    <p class="display-subtitle">RoadLens validates and decodes the exact selected file, applies model-matched letterboxing, then runs the packaged ONNX detector and NMS.</p>
    <div class="grid capture-layout">
      <div class="camera-card ${scanning ? "scanning" : ""}">
        <div class="camera-media ${isNight ? "night" : ""}" ${bg}></div><div class="camera-overlay"></div><div class="scan-line"></div>
        <div class="focus-frame ${scanning ? "visible" : ""}"><span class="focus-label">ONNX · analyzing pixels</span></div>
        <div class="camera-top"><div class="camera-status"><i class="pulse-dot"></i>Local ONNX inference server</div><div class="camera-tools"><button class="icon-button" data-action="toggle-night" aria-label="Toggle sample image">${icons.sun}</button></div></div>
        <div class="camera-bottom"><div class="gps-chip"><strong>12.9964° N, 77.6968° E</strong><span>Accuracy ±7.4 m · GPS locked</span></div>
          <button class="shutter" data-action="analyze" aria-label="Capture and analyze" ${scanning ? "disabled" : ""}></button>
          <label class="upload-trigger" aria-label="Capture or upload road image">${icons.upload}<input id="image-upload" type="file" accept="image/png,image/jpeg,image/webp" capture="environment" hidden /></label>
        </div>
      </div>
      <div class="capture-side">
        <article class="panel step-card"><div class="mini-head"><h3>Inspection readiness</h3>${pill(state.online ? "SYNCED" : "OFFLINE")}</div>
          <div class="stepper">
            <div class="step-row done"><span class="step-dot">${icons.check}</span><div class="step-copy"><strong>Location acquired</strong><span>GPS accuracy ±7.4 metres</span></div></div>
            <div class="step-row done"><span class="step-dot">${icons.check}</span><div class="step-copy"><strong>Image source ready</strong><span>${state.analysisFile ? esc(state.analysisFile.name) : isNight ? "Packaged low-light crack sample" : "Packaged pothole sample"}</span></div></div>
            <div class="step-row ${scanning ? "current" : ""}"><span class="step-dot">3</span><div class="step-copy"><strong>Real AI inference</strong><span>${scanning ? "Preprocessing, inference and NMS in progress…" : "No result is generated until the model returns"}</span></div></div>
            <div class="step-row"><span class="step-dot">4</span><div class="step-copy"><strong>Review and save</strong><span>Confirm before report submission</span></div></div>
          </div>
          <button class="button primary full" data-action="analyze" ${scanning ? "disabled" : ""}>${scanning ? `${icons.spark} Running real inference…` : `${icons.camera} Analyze selected image`}</button>
        </article>
        <article class="panel quality-card"><div class="mini-head"><h3>Image quality</h3><span class="trend-up">Good</span></div><div class="quality-meter"><i class="on"></i><i class="on"></i><i class="on"></i><i class="on"></i><i></i></div><p>Hold steady and include visible road surface around the damaged area.</p></article>
      </div>
    </div>
  </section>`;
}

function resultView() {
  const result = state.analysisResult;
  const detections = result?.detections || [];
  const primary = detections.reduce((best, item) => !best || item.confidence > best.confidence ? item : best, null);
  const annotated = state.evidenceMode === "annotated";
  const confidence = Math.round((primary?.confidence || 0) * 100);
  const dimensions = result.image;
  const boxes = annotated ? detections.map(detection => {
    const box = detection.bbox;
    const left = box.x1 / dimensions.width * 100;
    const top = box.y1 / dimensions.height * 100;
    const width = (box.x2 - box.x1) / dimensions.width * 100;
    const height = (box.y2 - box.y1) / dimensions.height * 100;
    return `<div class="bounding-box" style="left:${left}%;top:${top}%;width:${width}%;height:${height}%"><span class="bounding-label">${esc(detection.damage_type)} · ${Math.round(detection.confidence * 100)}%</span></div>`;
  }).join("") : "";
  return `<section>
    <p class="eyebrow">Real inference complete · ${detections.length} damage region${detections.length === 1 ? "" : "s"} found</p><h2 class="display-title">Review the model result before you report it.</h2>
    <div class="grid result-layout">
      <article class="panel evidence-viewer"><div class="evidence-image ${state.captureMode === "crack" ? "night" : ""}" ${state.customImage ? `style="background-image:url('${state.customImage}')"` : ""}>${boxes}</div>
        <div class="evidence-footer"><div class="toggle-group"><button class="${annotated ? "active" : ""}" data-evidence="annotated">Annotated</button><button class="${!annotated ? "active" : ""}" data-evidence="original">Original</button></div><span style="font-size:9px;color:var(--muted)">${result.quality.lighting.replace("_", " ")} · brightness ${result.quality.brightness}</span></div></article>
      <article class="panel result-summary"><div class="result-heading"><div><p class="eyebrow">Highest-confidence detection</p><h2>${esc(primary.damage_type)}</h2><p>YOLOv8s ONNX · ${result.timing_ms.inference} ms inference</p></div><div class="confidence-ring" style="background:conic-gradient(var(--pine) 0 ${confidence}%, #e2e5dd ${confidence}% 100%)"><span>${confidence}%</span></div></div>
        <div class="detail-list">
          <div class="detail-row">${icons.shield}<span>Severity</span><strong>${pill(result.severity.level)}</strong></div>
          <div class="detail-row">${icons.pin}<span>Location</span><strong>Outer Ring Rd, Mahadevapura</strong></div>
          <div class="detail-row">${icons.clock}<span>Timestamp</span><strong>24 Aug 2026 · 10:42 AM IST</strong></div>
          <div class="detail-row">${icons.sun}<span>Image / lighting</span><strong>${dimensions.width}×${dimensions.height} · ${result.quality.lighting.replace("_", " ")}</strong></div>
          <div class="detail-row">${icons.cloud}<span>Sync status</span><strong>${pill(state.online ? "SYNCED" : "PENDING")}</strong></div>
          <div class="detail-row">${icons.list}<span>CVR-ID / custom field</span><strong>${esc(state.cvrLabel)}</strong></div>
        </div>
        <div class="result-actions"><button class="button outline" data-action="retake">Retake</button><button class="button dark" data-action="save-inspection">${icons.check} Save inspection</button><button class="button primary" style="grid-column:1/-1" data-action="submit-report">${icons.send} Save & submit report</button></div>
        <div class="ai-note"><strong>How severity was estimated:</strong> ${esc(result.severity.method)} using measured bounding-box area ratio (${(result.severity.damage_area_ratio * 100).toFixed(2)}%) and detection count. It is separate from confidence and is not a validated civil-engineering rating.</div>
        <div class="ai-note"><strong>Debug timing:</strong> preprocess ${result.timing_ms.preprocessing} ms · inference ${result.timing_ms.inference} ms · postprocess ${result.timing_ms.postprocessing} ms · total ${result.timing_ms.total} ms.</div>
      </article>
    </div>
  </section>`;
}

function analysisOutcomeView() {
  const result = state.analysisResult;
  const noDetection = state.analysisStage === "noDetection";
  const title = noDetection ? "No supported road damage detected." : state.analysisStage === "invalidImage" ? "This image cannot be analyzed reliably." : "Image analysis could not complete.";
  const message = noDetection ? result.message : state.analysisError?.message || "Start the local inference server and try again.";
  const highest = result?.debug?.highest_confidence;
  return `<section><p class="eyebrow">${noDetection ? "Valid no-detection result" : "Analysis stopped safely"}</p><h2 class="display-title">${title}</h2><p class="display-subtitle">${esc(message)} The app has not substituted a sample prediction or fabricated a damage result.</p>
    <div class="grid result-layout"><article class="panel evidence-viewer"><div class="evidence-image ${state.captureMode === "crack" ? "night" : ""}" ${state.customImage ? `style="background-image:url('${state.customImage}')"` : ""}></div><div class="evidence-footer"><strong style="font-size:10px">${noDetection ? "Detections: 0" : esc(state.analysisError?.code || "INFERENCE_FAILED")}</strong><span style="font-size:9px;color:var(--muted)">${highest != null ? `Highest raw confidence ${(highest * 100).toFixed(1)}% (debug)` : "No result payload"}</span></div></article>
      <article class="panel result-summary"><div class="result-heading"><div><p class="eyebrow">Outcome</p><h2>${noDetection ? "No damage" : "Not analyzed"}</h2><p>${noDetection ? `${result.image.width}×${result.image.height} · ${result.timing_ms.total} ms total` : "See the technical server log for details"}</p></div><span class="stat-icon">${noDetection ? icons.check : icons.x}</span></div>
        ${noDetection ? `<div class="detail-list"><div class="detail-row">${icons.sun}<span>Lighting</span><strong>${result.quality.lighting.replace("_", " ")}</strong></div><div class="detail-row">${icons.spark}<span>Model outputs</span><strong>${result.debug.output_tensor_shapes.map(shape => shape.join("×")).join(" · ")}</strong></div><div class="detail-row">${icons.shield}<span>Severity</span><strong>Not applicable</strong></div></div>` : `<div class="ai-note"><strong>${esc(state.analysisError?.code || "INFERENCE_FAILED")}</strong><br/>${esc(state.analysisError?.detail || "The backend did not return a successful inference response.")}</div>`}
        <div class="result-actions"><button class="button outline" data-action="retake">Choose another image</button><button class="button dark" data-action="reanalyze">Run again</button></div>
      </article></div></section>`;
}

function filteredReports() {
  return state.reports.filter(r => {
    const query = state.reportSearch.trim().toLowerCase();
    return (!query || `${r.id} ${r.type} ${r.address} ${r.zone}`.toLowerCase().includes(query)) &&
      (state.severityFilter === "ALL" || r.severity === state.severityFilter) &&
      (state.statusFilter === "ALL" || r.status === state.statusFilter);
  });
}

function reportsTable() {
  const reports = filteredReports();
  return `<article class="panel table-panel">${reports.length ? `<table class="data-table"><thead><tr><th>Ticket</th><th>Damage</th><th>Location</th><th>Severity</th><th>Status</th><th>Assigned to</th><th>Reported</th></tr></thead><tbody>${reports.map(r => `<tr data-report="${r.id}"><td class="table-id">${r.id.replace("RD-2026-", "#")}</td><td>${r.type}<br/><span style="color:var(--muted);font-size:9px">${r.confidence}% confidence</span></td><td class="table-location"><strong>${r.address}</strong><span>${r.zone}</span></td><td>${pill(r.severity)}</td><td>${pill(r.status)}</td><td><span class="assignee"><i class="mini-avatar">${r.initials}</i>${r.assignee}</span></td><td>${r.time}</td></tr>`).join("")}</tbody></table>` : `<div class="empty-state">${icons.search}<p>No reports match these filters.</p><button class="button outline" data-action="clear-filters">Clear filters</button></div>`}</article>`;
}

function reportsToolbar(includeCreate = false) {
  return `<div class="toolbar"><label class="search-box">${icons.search}<input id="report-search" value="${esc(state.reportSearch)}" placeholder="Search ticket, road or location" /></label>
    <select class="field" id="severity-filter" aria-label="Severity"><option value="ALL">All severity</option>${["HIGH","MEDIUM","LOW"].map(x=>`<option ${state.severityFilter===x?"selected":""}>${x}</option>`).join("")}</select>
    <select class="field" id="status-filter" aria-label="Status"><option value="ALL">All status</option>${["SUBMITTED","ASSIGNED","IN_PROGRESS","VERIFIED","CLOSED"].map(x=>`<option ${state.statusFilter===x?"selected":""} value="${x}">${x.replaceAll("_"," ")}</option>`).join("")}</select>
    ${includeCreate ? `<button class="button primary" data-view="capture">${icons.plus} New inspection</button>` : `<button class="button outline" data-action="export">${icons.upload} Export CSV</button>`}
  </div>`;
}

function inspectionsView() {
  return `<section><p class="eyebrow">Offline-first history</p><h2 class="display-title">Evidence you can trust, online or off.</h2><p class="display-subtitle">Each inspection keeps its image, detection, GPS accuracy, timestamp and synchronization state together.</p>${reportsToolbar(true)}${reportsTable()}</section>`;
}

function authorityOverview(analyticsOnly = false) {
  return `<section><p class="eyebrow">${analyticsOnly ? "City performance" : "Bengaluru road maintenance"}</p><h2 class="display-title">${analyticsOnly ? "Turn field evidence into operational clarity." : "Focus the day where it matters most."}</h2>
    <p class="display-subtitle">Priorities combine configured severity, confidence, supporting reports, road importance and time unresolved.</p>
    <div class="grid stats-grid">
      ${statCard("Open reports", "142", `<span class="trend-up">18 new</span> today`, "list")}
      ${statCard("P1 critical", "12", "4 unassigned", "shield", "#fde0da")}
      ${statCard("In progress", "47", "Across 9 field teams", "chart", "#dceaf0")}
      ${statCard("Median resolution", "2.4d", `<span class="trend-up">↓ 11%</span> this month`, "clock", "#fff0cf")}
    </div>
    <div class="grid authority-grid">
      <article class="panel chart-panel"><div class="mini-head"><div><h3>Damage reports · 7 days</h3><p style="margin:4px 0 0;color:var(--muted);font-size:9px">New reports vs resolved cases</p></div><div class="chart-legend"><span><i class="legend-dot"></i>Reported</span><span><i class="legend-dot green"></i>Resolved</span></div></div>
        <div class="bar-chart">${[[62,38],[72,44],[51,48],[85,52],[70,59],[94,68],[76,72]].map((pair,i)=>`<div class="bar-group"><i class="bar" style="height:${pair[0]}%"></i><i class="bar alt" style="height:${pair[1]}%"></i><span class="bar-label">${["M","T","W","T","F","S","S"][i]}</span></div>`).join("")}</div>
      </article>
      <article class="panel priority-panel"><div class="mini-head"><div><h3>Highest priority</h3><p style="margin:4px 0 0;color:var(--muted);font-size:9px">Review next</p></div><button class="text-button" data-view="reports">All reports →</button></div>
        <div class="priority-list">${state.reports.filter(r=>r.priority==="P1").concat(state.reports.filter(r=>r.priority==="P2")).slice(0,4).map(r=>`<div class="priority-row" data-report="${r.id}"><span class="priority-score">${r.priority}</span><div class="priority-copy"><strong>${r.type} · ${r.address.split(",")[0]}</strong><span>${r.supports} supporting reports · ${r.time}</span></div><span class="priority-arrow">${icons.arrow}</span></div>`).join("")}</div>
      </article>
    </div>
    <div class="section-head"><div><h2>Latest reports</h2><p>Evidence awaiting authority action</p></div><button class="text-button" data-view="reports">Open report queue →</button></div>
    ${reportsTable()}
  </section>`;
}

function reportsView() {
  return `<section><p class="eyebrow">Authority workflow</p><h2 class="display-title">One queue from detection to closure.</h2><p class="display-subtitle">Review evidence, assign accountable teams, update status and preserve a transparent case timeline.</p>${reportsToolbar(false)}${reportsTable()}</section>`;
}

function mapView() {
  const selected = state.reports.find(r=>r.id===state.selectedReportId) || state.reports[0];
  const positions = [[66,36],[37,48],[55,66],[24,30],[76,72]];
  return `<section><p class="eyebrow">Location intelligence</p><h2 class="display-title">See where attention is accumulating.</h2><p class="display-subtitle">Map markers use severity colors and can be filtered by damage type, date, status, location and authority.</p>
    <div class="toolbar"><select class="field"><option>All damage types</option><option>Pothole</option><option>Crack</option></select><select class="field"><option>All severity</option><option>High</option><option>Medium</option><option>Low</option></select><select class="field"><option>All zones</option><option>Central Zone</option><option>East Zone</option></select><button class="button outline" data-action="heatmap">${icons.chart} Heatmap preview</button></div>
    <div class="grid map-layout"><article class="panel map-canvas">
      <span class="map-label" style="left:21%;top:18%">Malleshwaram</span><span class="map-label" style="left:62%;top:20%">Indiranagar</span><span class="map-label" style="left:43%;top:57%">Ashok Nagar</span><span class="map-label" style="left:68%;top:78%">Koramangala</span>
      ${state.reports.map((r,i)=>`<button class="marker ${r.severity.toLowerCase()} ${selected.id===r.id?"active":""}" style="left:${positions[i%positions.length][0]}%;top:${positions[i%positions.length][1]}%" data-report="${r.id}" aria-label="${r.type} at ${r.address}"><span>${r.priority}</span></button>`).join("")}
      <div class="map-controls"><button aria-label="Zoom in">+</button><button aria-label="Zoom out">−</button><button aria-label="My location">⌾</button></div>
    </article><aside class="map-side">
      <article class="panel map-summary"><h3>Visible damage</h3><div class="severity-legend"><div class="severity-line"><span class="severity-label"><i></i>High severity</span><strong>12</strong></div><div class="severity-line"><span class="severity-label"><i class="medium"></i>Medium severity</span><strong>28</strong></div><div class="severity-line"><span class="severity-label"><i class="low"></i>Low severity</span><strong>19</strong></div></div></article>
      <article class="panel selected-report"><div class="selected-thumb" style="background-image:url('${imageStyle(selected)}')"></div><div class="selected-copy">${pill(selected.severity)}<h3>${selected.type}</h3><p>${selected.address}<br/>${selected.confidence}% confidence · ${selected.supports} supporting reports</p><button class="button dark full" style="margin-top:14px" data-report="${selected.id}">Open ${selected.id.replace("RD-2026-", "#")}</button></div></article>
    </aside></div>
  </section>`;
}

function assistantView() {
  const current = state.reports[0];
  return `<section><p class="eyebrow">Multilingual · inspection-grounded</p><h2 class="display-title">Ask about the evidence, not the unknowns.</h2><p class="display-subtitle">The assistant explains saved inspection data and workflow status. It does not make unsupported civil-engineering claims.</p>
    <div class="grid assistant-layout"><article class="panel chat-panel"><div class="chat-header"><span class="assistant-orb">${icons.bot}</span><div><strong>RoadLens assistant</strong><span><i class="pulse-dot" style="display:inline-block;margin-right:5px;width:6px;height:6px"></i>Context loaded · ${current.id}</span></div><select id="language-select" class="field language-select"><option ${state.language==="English"?"selected":""}>English</option><option ${state.language==="Hindi"?"selected":""}>Hindi</option><option ${state.language==="Kannada"?"selected":""}>Kannada</option></select></div>
      <div class="messages" id="messages">${state.messages.map(m=>`<div class="message ${m.from}">${esc(m.text)}<small>${m.time}</small></div>`).join("")}</div>
      <form class="chat-composer" id="chat-form"><textarea id="chat-input" placeholder="Ask about severity, confidence, location or status…" aria-label="Message"></textarea><button class="button primary" aria-label="Send">${icons.send}</button></form></article>
      <aside class="panel context-panel"><div class="mini-head"><h3>Active context</h3>${pill(current.status)}</div><div class="context-card"><div class="context-image"></div><div class="context-copy"><strong>${current.type} · ${current.severity}</strong><span>${current.address}<br/>${current.confidence}% confidence</span></div></div><div class="suggestions"><button class="suggestion" data-question="What does the severity mean?">What does the severity mean?</button><button class="suggestion" data-question="Has this report been assigned?">Has this report been assigned?</button><button class="suggestion" data-question="Explain the confidence score.">Explain the confidence score.</button></div></aside>
    </div>
  </section>`;
}

function settingsView() {
  return `<section><p class="eyebrow">Device & workflow</p><h2 class="display-title">Reliable by default. Configurable by design.</h2><p class="display-subtitle">Control offline behavior, low-light processing and the source document’s undefined CVR-ID/custom field without inventing its meaning.</p>
    <div class="grid settings-grid"><article class="panel settings-card"><h3>Field operations</h3><p>Applies to capture, analysis and synchronization on this device.</p>
      <div class="setting-row"><div class="setting-copy"><strong>Automatic synchronization</strong><span>Upload pending inspections when online</span></div><button class="switch ${state.autoSync?"on":""}" data-setting="autoSync" aria-label="Toggle automatic synchronization"></button></div>
      <div class="setting-row"><div class="setting-copy"><strong>Low-light enhancement</strong><span>Improve eligible night images before detection</span></div><button class="switch ${state.nightEnhance?"on":""}" data-setting="nightEnhance" aria-label="Toggle low-light enhancement"></button></div>
      <div class="setting-row"><div class="setting-copy"><strong>Connectivity simulation</strong><span>Test offline capture and retry behavior</span></div><button class="switch ${state.online?"on":""}" data-action="toggle-online" aria-label="Toggle connectivity"></button></div>
    </article>
    <article class="panel settings-card"><h3>Configurable inspection field</h3><p>The PRD mentions “CVR-ID/severity” but does not define CVR-ID. This demo keeps it explicitly configurable.</p><div class="cvr-field"><label for="cvr-input">CVR-ID label or value</label><input id="cvr-input" class="field" value="${esc(state.cvrLabel)}" placeholder="Not configured" /></div><button class="button dark" style="margin-top:11px" data-action="save-cvr">Save configuration</button>
      <div class="setting-row" style="margin-top:15px"><div class="setting-copy"><strong>Data storage</strong><span>Mock records persist in this browser only</span></div><button class="text-button" data-action="reset-demo">Reset demo</button></div>
    </article></div>
  </section>`;
}

function drawer() {
  const report = state.reports.find(r => r.id === state.selectedReportId);
  if (!report) return `<div class="drawer-backdrop" id="drawer-backdrop"></div>`;
  const statusOrder = ["DETECTED","REVIEWED","SUBMITTED","ASSIGNED","IN_PROGRESS","REPAIRED","VERIFIED","CLOSED"];
  const completedIndex = Math.max(statusOrder.indexOf(report.status), 2);
  const timeline = [
    ["Detection confirmed", `${report.confidence}% confidence · ${report.created}`],
    ["Report submitted", `Routed to Bengaluru authority · ${report.created}`],
    ...(completedIndex >= 3 ? [["Case assigned", `${report.assignee} · Field maintenance`]] : []),
    ...(completedIndex >= 4 ? [["Repair in progress", "Status updated by authority officer"]] : []),
    ...(completedIndex >= 6 ? [["Repair verified", "Evidence review complete"]] : []),
    ...(completedIndex >= 7 ? [["Case closed", "Resolution recorded in audit trail"]] : []),
  ];
  return `<div class="drawer-backdrop open" id="drawer-backdrop"><aside class="drawer" role="dialog" aria-modal="true" aria-label="Report details">
    <div class="drawer-top"><div><p>${report.id}</p><h2>${report.type} · ${report.priority}</h2></div><button class="icon-button" data-action="close-drawer" aria-label="Close details">${icons.x}</button></div>
    <div class="drawer-evidence" style="background-image:url('${imageStyle(report)}')">${pill(report.severity)}</div>
    <div class="drawer-section"><h3>Inspection details</h3><div class="detail-list">
      <div class="detail-row">${icons.pin}<span>Location</span><strong>${report.address}</strong></div><div class="detail-row">${icons.spark}<span>AI result</span><strong>${report.type} · ${report.confidence}%</strong></div><div class="detail-row">${icons.clock}<span>Captured</span><strong>${report.time}</strong></div><div class="detail-row">${icons.sun}<span>Lighting</span><strong>${report.lighting}</strong></div><div class="detail-row">${icons.cloud}<span>Sync</span><strong>${pill(report.sync)}</strong></div>
    </div></div>
    <div class="drawer-section"><h3>Authority workflow</h3><div class="form-grid"><div class="form-field"><label for="drawer-status">Status</label><select id="drawer-status" class="field">${["SUBMITTED","ASSIGNED","IN_PROGRESS","REPAIRED","VERIFIED","CLOSED"].map(x=>`<option value="${x}" ${report.status===x?"selected":""}>${x.replaceAll("_"," ")}</option>`).join("")}</select></div><div class="form-field"><label for="drawer-assignee">Assigned team</label><select id="drawer-assignee" class="field">${["Unassigned","Arjun Rao","Meera S.","Neha K."].map(x=>`<option ${report.assignee===x?"selected":""}>${x}</option>`).join("")}</select></div></div></div>
    <div class="drawer-section"><h3>Case timeline</h3><div class="timeline">${timeline.map(x=>`<div class="timeline-row"><span class="timeline-dot">${icons.check}</span><div class="timeline-copy"><strong>${x[0]}</strong><span>${x[1]}</span></div></div>`).join("")}</div></div>
    <div class="drawer-section"><h3>Comments</h3>${report.comments.map(c=>`<div class="ai-note" style="margin:0 0 8px">${esc(c)}</div>`).join("")}<div class="comment-box"><input id="comment-input" class="field" placeholder="Add an operational note…"/><button class="button dark" data-action="add-comment">Add</button></div></div>
    ${report.status !== "CLOSED" ? `<button class="button primary full" style="margin-top:20px" data-action="advance-case">${icons.check} Advance case status</button>` : `<button class="button soft full" style="margin-top:20px" disabled>${icons.check} Case closed</button>`}
  </aside></div>`;
}

function contentForView() {
  switch (state.view) {
    case "home": return fieldHome();
    case "capture": return captureView();
    case "inspections": return inspectionsView();
    case "map": return mapView();
    case "assistant": return assistantView();
    case "settings": return settingsView();
    case "overview": return authorityOverview(false);
    case "analytics": return authorityOverview(true);
    case "reports": return reportsView();
    default: return state.role === "field" ? fieldHome() : authorityOverview(false);
  }
}

function render() {
  app.innerHTML = `<div class="app-shell">${sidebar()}<main class="main-shell">${topbar()}<div class="content">${contentForView()}</div></main>${mobileBottom()}${drawer()}</div>`;
  const messages = document.querySelector("#messages");
  if (messages) messages.scrollTop = messages.scrollHeight;
}

function toast(message) {
  const node = document.createElement("div");
  node.className = "toast";
  node.innerHTML = `${icons.check}<span>${esc(message)}</span>`;
  toastRegion.appendChild(node);
  setTimeout(() => node.remove(), 3200);
}

function openReport(id) {
  state.selectedReportId = id;
  render();
}

function syncPending() {
  if (!state.online || !state.autoSync) return;
  let changed = false;
  state.reports = state.reports.map(r => {
    if (r.sync === "PENDING") { changed = true; return { ...r, sync: "SYNCED" }; }
    return r;
  });
  if (changed) toast("Pending inspection synchronized");
}

function addAnalyzedReport(submitted) {
  const result = state.analysisResult;
  if (!result?.detected || !result.detections?.length) {
    toast("Only a confirmed model detection can become a damage report");
    return;
  }
  const primary = result.detections.reduce((best, item) => !best || item.confidence > best.confidence ? item : best, null);
  const severity = result.severity.level;
  const next = state.reports.length + 143;
  const report = {
    id: `RD-2026-00${next}`, type: primary.damage_type, severity,
    confidence: Math.round(primary.confidence * 100), priority: severity === "HIGH" ? "P1" : severity === "MEDIUM" ? "P2" : "P3", status: submitted ? "SUBMITTED" : "DETECTED",
    sync: state.online ? "SYNCED" : "PENDING", address: "Outer Ring Rd, Mahadevapura", zone: "East Zone",
    lat: 12.9964, lng: 77.6968, accuracy: 7.4, time: "Just now", image: primary.damage_type.includes("Crack") ? "crack" : "pothole",
    assignee: "Unassigned", initials: "--", supports: 1, lighting: result.quality.lighting.replace("_", " / "), comments: [], created: "24 Aug 2026",
  };
  state.reports = [report, ...state.reports];
  state.analysisStage = "idle";
  state.analysisFile = null;
  state.analysisResult = null;
  state.analysisError = null;
  state.customImage = null;
  state.view = "inspections";
  save(); render(); toast(submitted ? `Report ${report.id} submitted` : "Inspection saved to this device");
}

async function getAnalysisFile() {
  if (state.analysisFile) return state.analysisFile;
  const source = state.captureMode === "crack" ? "assets/crack-night-evidence.png" : "assets/pothole-evidence.png";
  const response = await fetch(source);
  if (!response.ok) throw new Error(`Could not read the captured image (${response.status}).`);
  const blob = await response.blob();
  return new File([blob], source.split("/").pop(), { type: blob.type || "image/png" });
}

async function analyzeSelectedImage() {
  if (state.analysisStage === "loading") return;
  state.analysisStage = "loading";
  state.analysisResult = null;
  state.analysisError = null;
  render();
  try {
    const file = await getAnalysisFile();
    if (!file.size) throw Object.assign(new Error("The selected image is empty."), { code: "INVALID_IMAGE" });
    if (!/^image\/(jpeg|png|webp)$/.test(file.type)) throw Object.assign(new Error("Choose a JPEG, PNG, or WebP road image."), { code: "INVALID_IMAGE" });
    const form = new FormData();
    form.append("file", file, file.name);
    const response = await fetch("/api/analyze", { method: "POST", body: form });
    const payload = await response.json().catch(() => null);
    if (!response.ok || !payload?.success) {
      const error = payload?.error || payload?.detail || {};
      throw Object.assign(new Error(error.message || "The inference service returned an error."), { code: error.code || (response.status === 422 ? "INVALID_IMAGE" : "SERVER_ERROR"), detail: error.detail });
    }
    state.analysisResult = payload;
    state.evidenceMode = "annotated";
    state.analysisStage = payload.detected ? "success" : "noDetection";
    console.info("RoadLens inference", { image: payload.image, quality: payload.quality, timing_ms: payload.timing_ms, debug: payload.debug, detections: payload.detections });
    render();
    toast(payload.detected ? `${payload.detections.length} real model detection${payload.detections.length === 1 ? "" : "s"}` : "Valid result · no supported damage detected");
  } catch (error) {
    const code = error.code || (error instanceof TypeError ? "NETWORK_ERROR" : "INFERENCE_FAILED");
    state.analysisError = { code, message: error.message || "Image analysis failed.", detail: error.detail || (code === "NETWORK_ERROR" ? "Run start_app.ps1 so the local model API is available." : "") };
    state.analysisStage = ["INVALID_IMAGE", "IMAGE_DECODE_FAILED"].includes(code) ? "invalidImage" : "error";
    render();
    toast(`${code} · no result fabricated`);
  }
}

function resetAnalysis({ keepImage = false } = {}) {
  state.analysisStage = "idle";
  state.analysisResult = null;
  state.analysisError = null;
  if (!keepImage) {
    if (state.customImage?.startsWith("blob:")) URL.revokeObjectURL(state.customImage);
    state.customImage = null;
    state.analysisFile = null;
  }
}

function answerQuestion(question) {
  const q = question.toLowerCase();
  const current = state.reports[0];
  const replies = {
    English: q.includes("severity") ? `This inspection is marked ${current.severity} by the deterministic baseline severity heuristic. Severity is separate from the ${current.confidence}% model confidence.` : q.includes("assigned") ? `${current.id} is assigned to ${current.assignee} and is currently ${current.status.replaceAll("_", " ")}.` : q.includes("confidence") ? `The ${current.confidence}% confidence is the model score for ${current.type}. It is not a measure of repair urgency or severity.` : `The active inspection is ${current.type} at ${current.address}, with ${current.confidence}% confidence and status ${current.status.replaceAll("_", " ")}.`,
    Hindi: `${current.id} में ${current.type} का परिणाम ${current.confidence}% मॉडल कॉन्फ़िडेंस के साथ दर्ज है। स्थिति ${current.status.replaceAll("_", " ")} है।`,
    Kannada: `${current.id} ವರದಿಯಲ್ಲಿ ${current.type} ಫಲಿತಾಂಶವು ${current.confidence}% ಮಾದರಿ ವಿಶ್ವಾಸದೊಂದಿಗೆ ದಾಖಲಾಗಿದೆ. ಸ್ಥಿತಿ ${current.status.replaceAll("_", " ")} ಆಗಿದೆ.`,
  };
  state.messages.push({ from: "user", text: question, time: "Now" });
  state.messages.push({ from: "bot", text: replies[state.language], time: "Now" });
  save(); render();
}

document.addEventListener("click", event => {
  const viewTarget = event.target.closest("[data-view]");
  if (viewTarget) {
    state.view = viewTarget.dataset.view;
    state.selectedReportId = null;
    state.analysisStage = "idle";
    save(); render(); window.scrollTo({ top: 0, behavior: "instant" }); return;
  }
  const roleTarget = event.target.closest("[data-role]");
  if (roleTarget) {
    state.role = roleTarget.dataset.role;
    state.view = state.role === "field" ? "home" : "overview";
    state.selectedReportId = null;
    save(); render(); window.scrollTo({ top: 0, behavior: "instant" }); toast(`${state.role === "field" ? "Field app" : "Authority dashboard"} opened`); return;
  }
  const reportTarget = event.target.closest("[data-report]");
  if (reportTarget) { openReport(reportTarget.dataset.report); return; }
  const questionTarget = event.target.closest("[data-question]");
  if (questionTarget) { answerQuestion(questionTarget.dataset.question); return; }
  const evidenceTarget = event.target.closest("[data-evidence]");
  if (evidenceTarget) { state.evidenceMode = evidenceTarget.dataset.evidence; render(); return; }
  const settingTarget = event.target.closest("[data-setting]");
  if (settingTarget) { state[settingTarget.dataset.setting] = !state[settingTarget.dataset.setting]; save(); render(); toast("Setting updated"); return; }
  const action = event.target.closest("[data-action]")?.dataset.action;
  if (!action) {
    if (event.target.id === "drawer-backdrop") { state.selectedReportId = null; render(); }
    return;
  }
  if (action === "toggle-menu") document.querySelector("#sidebar")?.classList.toggle("open");
  if (action === "notifications") toast("3 updates · latest repair assignment 18 minutes ago");
  if (action === "toggle-online") { state.online = !state.online; syncPending(); save(); render(); toast(state.online ? "Connection restored · sync checked" : "Offline mode enabled"); }
  if (action === "demo-night") { resetAnalysis(); state.captureMode = "crack"; state.view = "capture"; render(); }
  if (action === "toggle-night") { resetAnalysis(); state.captureMode = state.captureMode === "crack" ? "pothole" : "crack"; render(); toast(state.captureMode === "crack" ? "Low-light sample selected" : "Daylight sample selected"); }
  if (action === "analyze") analyzeSelectedImage();
  if (action === "reanalyze") { resetAnalysis({ keepImage: true }); analyzeSelectedImage(); }
  if (action === "retake") { resetAnalysis(); render(); }
  if (action === "save-inspection") addAnalyzedReport(false);
  if (action === "submit-report") addAnalyzedReport(true);
  if (action === "clear-filters") { state.reportSearch=""; state.severityFilter="ALL"; state.statusFilter="ALL"; render(); }
  if (action === "export") { const rows = ["ticket,type,severity,status,location", ...filteredReports().map(r=>`${r.id},${r.type},${r.severity},${r.status},\"${r.address}\"`)]; const blob=new Blob([rows.join("\n")],{type:"text/csv"}); const a=document.createElement("a"); a.href=URL.createObjectURL(blob); a.download="roadlens-reports.csv"; a.click(); URL.revokeObjectURL(a.href); toast("CSV export prepared"); }
  if (action === "heatmap") toast("Heatmap preview uses visible report density");
  if (action === "close-drawer") { state.selectedReportId=null; render(); }
  if (action === "add-comment") { const input=document.querySelector("#comment-input"); const report=state.reports.find(r=>r.id===state.selectedReportId); if(input?.value.trim()&&report){report.comments.push(input.value.trim());save();render();toast("Comment added to audit trail");} }
  if (action === "advance-case") { const report=state.reports.find(r=>r.id===state.selectedReportId); const order=["SUBMITTED","ASSIGNED","IN_PROGRESS","REPAIRED","VERIFIED","CLOSED"]; if(report){ const i=Math.max(0,order.indexOf(report.status)); report.status=order[Math.min(i+1,order.length-1)]; save();render();toast(`Case advanced to ${report.status.replaceAll("_"," ")}`);} }
  if (action === "save-cvr") { state.cvrLabel=document.querySelector("#cvr-input")?.value.trim()||"Not configured";save();render();toast("Configurable field saved"); }
  if (action === "reset-demo") { localStorage.removeItem("roadlens-demo"); location.reload(); }
});

document.addEventListener("change", event => {
  if (event.target.id === "severity-filter") { state.severityFilter=event.target.value;save();render(); }
  if (event.target.id === "status-filter") { state.statusFilter=event.target.value;save();render(); }
  if (event.target.id === "language-select") { state.language=event.target.value;save();render();toast(`Assistant language set to ${state.language}`); }
  if (event.target.id === "drawer-status") { const r=state.reports.find(x=>x.id===state.selectedReportId);if(r){r.status=event.target.value;save();render();toast("Report status updated");} }
  if (event.target.id === "drawer-assignee") { const r=state.reports.find(x=>x.id===state.selectedReportId);if(r){r.assignee=event.target.value;r.initials=r.assignee==="Unassigned"?"--":r.assignee.split(/\s/).map(x=>x[0]).join("").slice(0,2).toUpperCase();if(r.status==="SUBMITTED")r.status="ASSIGNED";save();render();toast("Assignment updated");} }
  if (event.target.id === "image-upload") { const file=event.target.files?.[0]; if(file){ if(file.size>15*1024*1024){toast("Image must be smaller than 15 MB");return;} resetAnalysis(); state.analysisFile=file;state.customImage=URL.createObjectURL(file);render();toast(`Exact file selected · ${file.name}`);} }
});

document.addEventListener("input", event => {
  if (event.target.id === "report-search") { state.reportSearch=event.target.value; const panel=document.querySelector(".table-panel"); if(panel){ const wrap=document.createElement("div"); wrap.innerHTML=reportsTable(); panel.replaceWith(wrap.firstElementChild); } }
});

document.addEventListener("submit", event => {
  if (event.target.id === "chat-form") { event.preventDefault(); const input=document.querySelector("#chat-input"); if(input?.value.trim()) answerQuestion(input.value.trim()); }
});

render();
