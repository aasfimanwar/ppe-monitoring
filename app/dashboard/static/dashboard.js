const REFRESH_MS = 3000;

async function fetchJSON(url, options) {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(`${url} failed: ${res.status}`);
  return res.json();
}

function renderCameras(cameras) {
  const el = document.getElementById("camera-list");
  el.innerHTML = cameras.map(c => `
    <div class="camera-card">
      <span>${c.name} (${c.zone})</span>
      <span class="status-badge status-${c.status}">${c.status}</span>
    </div>
  `).join("");
}

function renderViolations(violations) {
  const el = document.getElementById("violation-list");
  el.innerHTML = violations.map(v => `
    <div class="violation-card ${v.resolved ? "resolved" : "unresolved"}">
      <img class="thumb" src="/api/violations/${v.id}/evidence" alt="evidence">
      <div class="violation-info">
        <div class="violation-class">
          ${v.violation_class}
          ${v.escalated ? '<span class="status-badge status-error">ESCALATED</span>' : ""}
        </div>
        <div class="violation-meta">${v.camera_id} - ${v.zone} - ${new Date(v.timestamp).toLocaleString()}</div>
        <div class="violation-meta">Confidence: ${(v.confidence * 100).toFixed(0)}%</div>
        ${v.escalated ? '<div class="violation-meta">Repeat violations in this zone - identify the worker from the photo and act per policy.</div>' : ""}
      </div>
      <div>
        ${v.resolved
          ? `<span class="status-badge status-online">Resolved by ${v.resolved_by}</span>`
          : `<button class="resolve-btn" data-id="${v.id}">Mark Resolved</button>`}
      </div>
    </div>
  `).join("");

  document.querySelectorAll(".resolve-btn").forEach(btn => {
    btn.addEventListener("click", () => resolveViolation(btn.dataset.id));
  });
}
async function resolveViolation(id) {
  const resolvedBy = prompt("Your name:");
  if (!resolvedBy) return;
  await fetchJSON(`/api/violations/${id}/resolve`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ resolved_by: resolvedBy }),
  });
  refresh();
}

async function refresh() {
  try {
    const [violations, cameras] = await Promise.all([
      fetchJSON("/api/violations"),
      fetchJSON("/api/cameras"),
    ]);
    renderViolations(violations);
    renderCameras(cameras);
  } catch (err) {
    console.error("Refresh failed:", err);
  }
}

refresh();
setInterval(refresh, REFRESH_MS);