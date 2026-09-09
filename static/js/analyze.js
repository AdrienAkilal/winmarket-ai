// WinMarket AI — "Nouvelle analyse" page
// Handles source selection, capacity panel and analysis progress polling.
// No business rule lives here: this file only calls /api/analyze and
// /api/capacity and reflects the JSON the server returns.
(function () {
  "use strict";

  const form = document.getElementById("analyze-form");
  if (!form) return;

  const STEP_LABELS = window.WM_STEPS || [];

  /* ── Element lookups (all upfront, so functions below never hit a
     temporal-dead-zone reference before the rest of the script runs) ── */
  const modeInputs = form.querySelectorAll('input[name="mode"]');
  const panels = {
    stock: document.getElementById("panel-stock"),
    upload: document.getElementById("panel-upload"),
    paste: document.getElementById("panel-paste"),
  };
  const exampleSelect = document.getElementById("example-select");
  const examplePreview = document.getElementById("example-preview");
  const dropzone = document.getElementById("dropzone");
  const fileInput = document.getElementById("file-input");
  const fileNameLabel = document.getElementById("file-name");
  const pasteArea = document.getElementById("paste-textarea");
  const submitBtn = document.getElementById("submit-analyze");

  const capacityBtn = document.getElementById("capacity-open");
  const capacityModal = document.getElementById("capacity-modal");
  const capacityClose = document.getElementById("capacity-close");
  const capacityForm = document.getElementById("capacity-form");
  const capacityPoles = document.getElementById("capacity-poles");
  const chargeRange = document.getElementById("cap-charge");

  const formPanel = document.getElementById("analyze-form-panel");
  const progressPanel = document.getElementById("progress-panel");
  const errorPanel = document.getElementById("analyze-error");
  const progressMessage = document.getElementById("progress-message");
  const progressSteps = document.getElementById("progress-steps");
  const progressBarFill = document.getElementById("progress-bar-fill");

  /* ── Source mode switching ── */
  function applyMode(mode) {
    Object.entries(panels).forEach(([key, el]) => {
      if (!el) return;
      el.hidden = key !== mode;
    });
    form.querySelectorAll(".option-card").forEach((card) => {
      card.classList.toggle("active", card.dataset.mode === mode);
    });
    updateSubmitState();
  }

  function currentMode() {
    const checked = form.querySelector('input[name="mode"]:checked');
    return checked ? checked.value : null;
  }

  function updateSubmitState() {
    const mode = currentMode();
    let ready = false;
    if (mode === "stock") ready = !!(exampleSelect && exampleSelect.value);
    if (mode === "upload") ready = !!(fileInput && fileInput.files && fileInput.files.length);
    if (mode === "paste") ready = !!(pasteArea && pasteArea.value.trim().length > 0);
    if (submitBtn) submitBtn.disabled = !ready;
  }

  function reflectFileName() {
    if (fileInput.files && fileInput.files[0]) {
      fileNameLabel.textContent = fileInput.files[0].name;
      fileNameLabel.hidden = false;
    } else {
      fileNameLabel.hidden = true;
    }
    updateSubmitState();
  }

  modeInputs.forEach((input) => {
    input.addEventListener("change", () => applyMode(input.value));
  });

  /* ── Stock example preview ── */
  if (exampleSelect) {
    exampleSelect.addEventListener("change", async () => {
      if (!exampleSelect.value) {
        examplePreview.hidden = true;
        updateSubmitState();
        return;
      }
      try {
        const res = await fetch(`/api/examples/${encodeURIComponent(exampleSelect.value)}`);
        if (!res.ok) throw new Error("fetch failed");
        const data = await res.json();
        examplePreview.textContent = data.text.slice(0, 2500) + (data.text.length > 2500 ? "…" : "");
        examplePreview.hidden = false;
      } catch {
        examplePreview.hidden = true;
      }
      updateSubmitState();
    });
  }

  /* ── Upload dropzone ── */
  if (dropzone && fileInput) {
    dropzone.addEventListener("click", () => fileInput.click());
    dropzone.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); fileInput.click(); }
    });
    ["dragenter", "dragover"].forEach((evt) =>
      dropzone.addEventListener(evt, (e) => { e.preventDefault(); dropzone.classList.add("dragover"); })
    );
    ["dragleave", "drop"].forEach((evt) =>
      dropzone.addEventListener(evt, (e) => { e.preventDefault(); dropzone.classList.remove("dragover"); })
    );
    dropzone.addEventListener("drop", (e) => {
      const dropped = e.dataTransfer.files;
      if (dropped && dropped.length) {
        fileInput.files = dropped;
        reflectFileName();
      }
    });
    fileInput.addEventListener("change", reflectFileName);
  }

  /* ── Paste textarea ── */
  if (pasteArea) pasteArea.addEventListener("input", updateSubmitState);

  /* ── Capacity panel ── */
  async function loadCapacityIntoStrip() {
    try {
      const res = await fetch("/api/capacity");
      const data = await res.json();
      const chargeEl = document.getElementById("capacity-charge-value");
      const dispoEl = document.getElementById("capacity-dispo-value");
      const projEl = document.getElementById("capacity-projects-value");
      if (chargeEl) chargeEl.textContent = `${data.charge_globale_pct}%`;
      if (dispoEl) dispoEl.textContent = `${data.disponibilite_pct}%`;
      if (projEl) projEl.textContent = data.nombre_projets_en_cours;
      return data;
    } catch {
      return null;
    }
  }

  function renderCapacityForm(data) {
    document.getElementById("cap-charge").value = data.charge_globale_pct;
    document.getElementById("cap-charge-out").textContent = data.charge_globale_pct + " %";
    document.getElementById("cap-projects-count").value = data.nombre_projets_en_cours;
    document.getElementById("cap-projects-list").value = (data.projets_en_cours || []).join("\n");
    capacityPoles.innerHTML = "";
    Object.entries(data.capacites_par_pole || {}).forEach(([pole, value]) => {
      const row = document.createElement("div");
      row.className = "field";
      row.innerHTML = `
        <label>${pole}</label>
        <div class="range-row">
          <input type="range" min="0" max="100" value="${value}" data-pole="${pole}">
          <span class="range-value">${value}%</span>
        </div>`;
      const range = row.querySelector("input[type=range]");
      const out = row.querySelector(".range-value");
      range.addEventListener("input", () => (out.textContent = range.value + "%"));
      capacityPoles.appendChild(row);
    });
  }

  if (capacityBtn && capacityModal) {
    capacityBtn.addEventListener("click", async () => {
      capacityModal.hidden = false;
      const data = await loadCapacityIntoStrip();
      if (data) renderCapacityForm(data);
    });
    capacityClose.addEventListener("click", () => (capacityModal.hidden = true));
    capacityModal.addEventListener("click", (e) => {
      if (e.target === capacityModal) capacityModal.hidden = true;
    });
  }

  if (chargeRange) {
    chargeRange.addEventListener("input", () => {
      document.getElementById("cap-charge-out").textContent = chargeRange.value + " %";
    });
  }

  if (capacityForm) {
    capacityForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const poles = {};
      capacityPoles.querySelectorAll("input[type=range]").forEach((r) => {
        poles[r.dataset.pole] = Number(r.value);
      });
      const payload = {
        charge_globale_pct: Number(document.getElementById("cap-charge").value),
        nombre_projets_en_cours: Number(document.getElementById("cap-projects-count").value),
        projets_en_cours: document.getElementById("cap-projects-list").value.split("\n").map((s) => s.trim()).filter(Boolean),
        capacites_par_pole: poles,
      };
      const saveBtn = capacityForm.querySelector('button[type="submit"]');
      saveBtn.disabled = true;
      saveBtn.textContent = "Enregistrement...";
      try {
        await fetch("/api/capacity", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        await loadCapacityIntoStrip();
        capacityModal.hidden = true;
      } finally {
        saveBtn.disabled = false;
        saveBtn.textContent = "Enregistrer les disponibilités";
      }
    });
  }

  /* ── Submit analysis ── */
  function renderSteps(activeIndex) {
    if (!progressSteps) return;
    progressSteps.innerHTML = STEP_LABELS.map((label, i) => {
      const cls = i < activeIndex ? "done" : i === activeIndex ? "active" : "";
      return `<div class="step-pill ${cls}">${i < activeIndex ? "✓ " : ""}${label}</div>`;
    }).join("");
  }

  const MAX_POLL_FAILURES = 15; // ~30s of transient network errors before giving up

  async function pollStatus(jobId, failureCount = 0) {
    let res;
    try {
      res = await fetch(`/api/analyze/${jobId}/status`);
    } catch {
      if (failureCount >= MAX_POLL_FAILURES) {
        showError("Impossible de contacter le serveur WinMarket AI.");
        return;
      }
      setTimeout(() => pollStatus(jobId, failureCount + 1), 2000);
      return;
    }

    if (!res.ok) {
      // A non-2xx response (404 = job unknown to the server, e.g. after a
      // restart) will never resolve itself — stop polling instead of
      // retrying forever.
      const body = await res.json().catch(() => ({}));
      showError(body.detail || "Cette analyse n'est plus disponible sur le serveur.");
      return;
    }

    const data = await res.json();
    if (data.status === "error") {
      showError(data.error || "Une erreur est survenue pendant l'analyse.");
      return;
    }
    renderSteps(data.step_index);
    progressMessage.textContent = data.message;
    progressBarFill.style.width = `${((data.step_index + 1) / data.total_steps) * 100}%`;
    if (data.status === "done" && data.redirect_url) {
      window.location.href = data.redirect_url;
      return;
    }
    setTimeout(() => pollStatus(jobId), 1100);
  }

  function showError(message) {
    progressPanel.hidden = true;
    errorPanel.hidden = false;
    document.getElementById("analyze-error-message").textContent = message;
  }

  document.getElementById("analyze-retry")?.addEventListener("click", () => {
    errorPanel.hidden = true;
    formPanel.hidden = false;
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const mode = currentMode();
    const fd = new FormData();
    fd.append("mode", mode);
    if (mode === "stock") fd.append("example_id", exampleSelect.value);
    if (mode === "upload") fd.append("file", fileInput.files[0]);
    if (mode === "paste") fd.append("text", pasteArea.value);

    formPanel.hidden = true;
    errorPanel.hidden = true;
    progressPanel.hidden = false;
    renderSteps(0);
    progressMessage.textContent = "Initialisation...";
    progressBarFill.style.width = "4%";

    try {
      const res = await fetch("/api/analyze", { method: "POST", body: fd });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        showError(err.detail || "Impossible de démarrer l'analyse.");
        return;
      }
      const data = await res.json();
      pollStatus(data.job_id);
    } catch {
      showError("Impossible de contacter le serveur WinMarket AI.");
    }
  });

  /* ── Initial state ── */
  const initialMode = form.querySelector('input[name="mode"]:checked');
  if (initialMode) applyMode(initialMode.value);
  updateSubmitState();
  loadCapacityIntoStrip();
})();
