// WinMarket AI — Base de connaissances page: reload + test search.
(function () {
  "use strict";
  const root = document.getElementById("knowledge-root");
  if (!root) return;

  const reloadBtn = document.getElementById("knowledge-reload");
  const totalDocsEl = document.getElementById("knowledge-total-docs");
  const totalKbEl = document.getElementById("knowledge-total-kb");
  const groupsEl = document.getElementById("knowledge-groups");

  function renderGroups(groups) {
    groupsEl.innerHTML = groups
      .map(
        (g) => `
      <details class="card card-tight" style="margin-bottom:12px">
        <summary style="cursor:pointer;font-weight:600">📁 ${escapeHtml(g.folder)} (${g.documents.length} documents)</summary>
        <div style="margin-top:12px">
          ${g.documents
            .map((d) => `<div class="text-tertiary" style="font-size:.8rem;padding:.2rem 0">📄 ${escapeHtml(d.source)} <span>(${d.chars.toLocaleString("fr-FR")} caractères)</span></div>`)
            .join("")}
        </div>
      </details>`
      )
      .join("");
  }

  function escapeHtml(str) {
    return String(str).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }

  if (reloadBtn) {
    reloadBtn.addEventListener("click", async () => {
      reloadBtn.disabled = true;
      reloadBtn.textContent = "Rechargement...";
      try {
        const res = await fetch("/api/knowledge/reload", { method: "POST" });
        const data = await res.json();
        totalDocsEl.textContent = data.total_documents;
        totalKbEl.textContent = `${data.total_kb} Ko`;
        renderGroups(data.groups);
      } finally {
        reloadBtn.disabled = false;
        reloadBtn.textContent = "🔄 Recharger la base de référence";
      }
    });
  }

  const searchInput = document.getElementById("knowledge-search");
  const searchResults = document.getElementById("knowledge-search-results");
  let debounceTimer;
  if (searchInput) {
    searchInput.addEventListener("input", () => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(runSearch, 350);
    });
  }

  async function runSearch() {
    const q = searchInput.value.trim();
    if (!q) {
      searchResults.innerHTML = "";
      return;
    }
    const res = await fetch(`/api/knowledge/search?q=${encodeURIComponent(q)}`);
    const data = await res.json();
    if (!data.results.length) {
      searchResults.innerHTML = `<p class="text-tertiary">Aucun résultat.</p>`;
      return;
    }
    searchResults.innerHTML =
      `<p class="text-tertiary" style="margin-bottom:12px">${data.results.length} résultat(s)</p>` +
      data.results
        .map(
          (r) => `
        <details class="card card-tight" style="margin-bottom:10px">
          <summary style="cursor:pointer;font-weight:600">📄 ${escapeHtml(r.source)} — pertinence : ${r.relevance_pct}%</summary>
          <div class="score-track" style="margin:10px 0"><div class="score-fill high" style="width:${r.relevance_pct}%"></div></div>
          <p class="text-secondary" style="font-size:.85rem;white-space:pre-wrap">${escapeHtml(r.excerpt)}</p>
        </details>`
        )
        .join("");
  }
})();
