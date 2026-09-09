// WinMarket AI — Historique page: client-side filtering of server-rendered data.
(function () {
  "use strict";
  const root = document.getElementById("history-root");
  if (!root) return;

  const records = window.WM_HISTORY || [];
  const list = document.getElementById("history-list");
  const countLabel = document.getElementById("history-count");
  const decisionFilter = document.getElementById("filter-decision");
  const scoreFilter = document.getElementById("filter-score");
  const scoreOut = document.getElementById("filter-score-out");
  const searchFilter = document.getElementById("filter-search");

  function decisionClass(decision) {
    if (decision === "GO") return "go";
    if ((decision || "").toUpperCase().includes("RESERVE")) return "reserve";
    return "nogo";
  }

  function render() {
    const decision = decisionFilter.value;
    const minScore = Number(scoreFilter.value);
    const query = searchFilter.value.trim().toLowerCase();
    scoreOut.textContent = minScore;

    const filtered = records.filter((r) => {
      if (decision !== "Toutes" && !(r.decision || "").toUpperCase().includes(decision.toUpperCase().replace("É", "E"))) return false;
      if ((r.score || 0) < minScore) return false;
      if (query) {
        const haystack = [r.titre, r.client, ...(r.techs || [])].join(" ").toLowerCase();
        if (!haystack.includes(query)) return false;
      }
      return true;
    });

    countLabel.textContent = `${filtered.length} appel(s) d'offres affiché(s) sur ${records.length}`;
    list.innerHTML = filtered
      .slice()
      .reverse()
      .map((r) => {
        const cls = decisionClass(r.decision);
        const budget = r.budget ? `${Number(r.budget).toLocaleString("fr-FR")} €` : "–";
        const techs = (r.techs || []).join(", ") || "–";
        const link = r.job_id ? `/app/resultats/${r.job_id}` : null;
        const inner = `
          <div>
            <div class="list-row-title">${escapeHtml(r.titre || "–")}</div>
            <div class="list-row-meta">${escapeHtml(r.client || "–")} · ${escapeHtml(r.secteur || "–")} · Budget : ${budget}<br>
              Technologies : ${escapeHtml(techs)} · Analysé le ${escapeHtml(r.date || "–")}</div>
          </div>
          <div style="text-align:right;min-width:110px">
            <div class="badge badge-${cls}" style="font-size:.72rem;padding:.25rem .7rem">${escapeHtml(r.decision || "–")}</div>
            <div class="font-mono" style="margin-top:.4rem;font-weight:700">${r.score ?? "–"}/100</div>
          </div>`;
        return link
          ? `<a class="list-row" href="${link}" style="text-decoration:none">${inner}</a>`
          : `<div class="list-row">${inner}</div>`;
      })
      .join("");
  }

  function escapeHtml(str) {
    return String(str).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }

  [decisionFilter, scoreFilter, searchFilter].forEach((el) => el && el.addEventListener("input", render));
  render();
})();
