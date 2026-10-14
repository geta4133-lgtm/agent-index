/* ===== app.js ===== */
(function () {
  "use strict";

  // ---- theme ----
  var root = document.documentElement;
  function readTheme() {
    try { return localStorage.getItem("uc-theme"); } catch (e) { return null; }
  }
  function applyTheme(t) {
    if (t === "light" || t === "dark") root.setAttribute("data-theme", t);
    else root.removeAttribute("data-theme");
    var btn = document.getElementById("themeToggle");
    if (btn) btn.setAttribute("aria-label", t === "dark" ? "Switch to light mode" : "Switch to dark mode");
  }
  var stored = readTheme();
  if (stored) applyTheme(stored);

  var tt = document.getElementById("themeToggle");
  if (tt) {
    tt.addEventListener("click", function () {
      var cur = root.getAttribute("data-theme");
      if (!cur) cur = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
      var next = cur === "dark" ? "light" : "dark";
      applyTheme(next);
      try { localStorage.setItem("uc-theme", next); } catch (e) {}
    });
  }

  // ---- sponsor dismiss ----
  var sc = document.getElementById("sponsorClose");
  if (sc) {
    sc.addEventListener("click", function () {
      root.setAttribute("data-sponsor-hidden", "");
      try { localStorage.setItem("uc-sponsor-hidden", String(Date.now() + 86400000)); } catch (e) {}
    });
  }

  // ---- copy prompt ----
  document.querySelectorAll("[data-copy]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var sel = btn.getAttribute("data-copy");
      var src = document.querySelector(sel);
      if (!src) return;
      var text = src.innerText;
      var done = function () {
        var old = btn.textContent;
        btn.textContent = "Copied";
        setTimeout(function () { btn.textContent = old; }, 1400);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done, done);
      } else {
        var ta = document.createElement("textarea");
        ta.value = text; document.body.appendChild(ta); ta.select();
        try { document.execCommand("copy"); } catch (e) {}
        document.body.removeChild(ta); done();
      }
    });
  });

  // ---- client-side search (index page) ----
  var si = document.getElementById("searchInput");
  if (si) {
    var items = [], __loading = false, __wait = null;
    function ensureIndex(cb) {
      if (items.length) return cb();
      __wait = cb;
      if (__loading) return;
      __loading = true;
      fetch(si.getAttribute("data-index") || "search-index.json")
        .then(function (r) { return r.json(); })
        .then(function (j) { items = j; __loading = false; if (__wait) __wait(); })
        .catch(function () { __loading = false; });
    }
    var list = document.getElementById("caseList");
    var counter = document.getElementById("resultCount");
    var none = document.getElementById("noResults");
    function render(q) {
      q = (q || "").trim().toLowerCase();
      var out = [];
      for (var i = 0; i < items.length; i++) {
        var it = items[i];
        if (!q || it.h.indexOf(q) !== -1) out.push(it);
        if (out.length >= 120) break;
      }
      var html = "";
      for (var j = 0; j < out.length; j++) {
        var it2 = out[j];
        html += '<li><a class="row" href="' + it2.u + '">' +
          '<span class="mark" style="background:' + it2.c + '">' + it2.a + "</span>" +
          '<span class="body"><h3>' + esc(it2.t) + "</h3><p>" + esc(it2.s) + "</p>" +
          '<span class="meta"><span>' + esc(it2.g) + "</span><span class=\"sep\">/</span>" +
          "<span>" + esc(it2.n) + "</span></span></span></a></li>";
      }
      if (list) list.innerHTML = html;
      if (none) none.style.display = out.length ? "none" : "block";
      if (counter) counter.textContent = out.length + (q ? " match" : " shown");
    }
    function esc(s) {
      return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
        return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
      });
    }
    var t;
    si.addEventListener("input", function () {
      clearTimeout(t);
      t = setTimeout(function () { ensureIndex(function () { render(si.value); }); }, 110);
    });
    var qp = new URLSearchParams(location.search).get("q");
    if (qp) { si.value = qp; ensureIndex(function () { render(qp); }); }
  }

  // ---- newsletter form ----
  var nf = document.getElementById("nlForm");
  if (nf) {
    nf.addEventListener("submit", function (e) {
      e.preventDefault();
      var msg = document.getElementById("nlMsg");
      var em = nf.querySelector("input[type=email]");
      var val = (em && em.value || "").trim();
      if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(val)) {
        if (msg) { msg.className = "formmsg err"; msg.textContent = "Enter a valid email address."; }
        return;
      }
      var action = nf.getAttribute("data-action");
      if (!action || action === "#") {
        if (msg) { msg.className = "formmsg ok"; msg.textContent = "Saved locally. Connect a provider to go live."; }
        try {
          var list = JSON.parse(localStorage.getItem("uc-subs") || "[]");
          list.push(val); localStorage.setItem("uc-subs", JSON.stringify(list));
        } catch (err) {}
        em.value = "";
        return;
      }
      if (msg) { msg.className = "formmsg"; msg.textContent = "Subscribing..."; }
      fetch(action, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: val })
      }).then(function (r) {
        if (!r.ok) throw new Error("bad status");
        if (msg) { msg.className = "formmsg ok"; msg.textContent = "You are in. Check your inbox."; }
        em.value = "";
      }).catch(function () {
        if (msg) { msg.className = "formmsg err"; msg.textContent = "Could not subscribe. Try again."; }
      });
    });
  }
})();