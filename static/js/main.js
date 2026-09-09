// WinMarket AI — shared UI behaviour (header scroll state, mobile nav, tabs)
(function () {
  "use strict";

  const header = document.querySelector(".site-header");
  if (header) {
    const onScroll = () => header.classList.toggle("scrolled", window.scrollY > 8);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  const navToggle = document.querySelector(".nav-toggle");
  const mainNav = document.querySelector(".main-nav");
  if (navToggle && mainNav) {
    navToggle.addEventListener("click", () => {
      const open = mainNav.classList.toggle("nav-open");
      navToggle.setAttribute("aria-expanded", String(open));
    });
  }

  // "Accédez à WinMarket AI" modal — shown instead of navigating straight to
  // /app for anyone who isn't an active Starter user (see site_header.html).
  const accessModal = document.getElementById("access-modal");
  if (accessModal) {
    document.querySelectorAll("[data-access-modal-trigger]").forEach((btn) => {
      btn.addEventListener("click", () => (accessModal.hidden = false));
    });
    document.getElementById("access-modal-close")?.addEventListener("click", () => (accessModal.hidden = true));
    accessModal.addEventListener("click", (e) => {
      if (e.target === accessModal) accessModal.hidden = true;
    });
  }

  // Generic tabs: any .tabs with [data-tab] buttons controlling sibling .tab-panel[data-tab-panel]
  document.querySelectorAll("[data-tabs]").forEach((wrapper) => {
    const buttons = wrapper.querySelectorAll(".tab-btn");
    const panels = wrapper.querySelectorAll(".tab-panel");
    buttons.forEach((btn) => {
      btn.addEventListener("click", () => {
        buttons.forEach((b) => b.classList.remove("active"));
        panels.forEach((p) => p.classList.remove("active"));
        btn.classList.add("active");
        const target = wrapper.querySelector(`.tab-panel[data-tab-panel="${btn.dataset.tab}"]`);
        if (target) target.classList.add("active");
      });
    });
  });
})();
