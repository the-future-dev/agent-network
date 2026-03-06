// Agora dashboard micro-animations
// This file is loaded via Streamlit components as a progressive enhancement.

(function () {
  function onReady(callback) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", callback, { once: true });
    } else {
      callback();
    }
  }

  function injectStyles() {
    if (document.getElementById("agora-dashboard-animations")) return;

    var style = document.createElement("style");
    style.id = "agora-dashboard-animations";
    style.textContent = [
      ".agora-fade-in-up {",
      "  opacity: 0;",
      "  transform: translateY(6px);",
      "  animation: agora-fade-in-up 320ms ease-out forwards;",
      "}",
      "",
      "@keyframes agora-fade-in-up {",
      "  from {",
      "    opacity: 0;",
      "    transform: translateY(6px);",
      "  }",
      "  to {",
      "    opacity: 1;",
      "    transform: translateY(0);",
      "  }",
      "}",
      "",
      ".agora-stagger {",
      "  will-change: opacity, transform;",
      "}"
    ].join("\n");

    document.head.appendChild(style);
  }

  function animateMetrics() {
    var nodes = document.querySelectorAll('[data-testid="stMetricValue"]');
    if (!nodes.length) return;

    nodes.forEach(function (node) {
      var raw = node.textContent || "";
      var numeric = parseFloat(raw.replace(/,/g, ""));
      if (!isFinite(numeric) || numeric <= 0) return;

      var duration = 600;
      var start = performance.now();

      function tick(now) {
        var progress = Math.min((now - start) / duration, 1);
        var eased = 1 - Math.pow(1 - progress, 3); // easeOutCubic
        var value = Math.round(numeric * eased);
        node.textContent = value.toLocaleString();
        if (progress < 1) {
          requestAnimationFrame(tick);
        }
      }

      requestAnimationFrame(tick);
    });
  }

  function animateCollection(selector, baseDelay) {
    var items = document.querySelectorAll(selector);
    if (!items.length) return;

    items.forEach(function (item, index) {
      item.classList.add("agora-fade-in-up", "agora-stagger");
      item.style.animationDelay = (index * baseDelay) + "ms";
    });
  }

  onReady(function () {
    try {
      document.body.classList.add("agora-js-enabled");
      injectStyles();
      animateMetrics();
      animateCollection(".post-card", 40);
      animateCollection(".activity-item", 30);
    } catch (e) {
      // Fail silently so the UI still works if anything goes wrong.
      console.error("[Agora dashboard.js] enhancement failed:", e);
    }
  });
})();

// Agora dashboard micro-interactions (progressive enhancement only).
// This file is intentionally minimal for now; it can be extended
// in later tasks with animations and other effects.

(function () {
  if (typeof window === "undefined") return;
  // Placeholder hook so we can verify the script is loaded if needed.
  window.__agoraDashboardLoaded = true;
})();

