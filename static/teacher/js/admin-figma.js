/* Theme toggle, mobile drawer, active nav, toast dismiss, delete-confirm dialog.
   Pure front-end: it never sends requests or touches your Django views. */
(function () {
  var d = document, r = d.documentElement;

  function setTheme(t) {
    r.setAttribute("data-sp-theme", t);
    try { localStorage.setItem("sp-theme", t); } catch (e) {}
    d.querySelectorAll("[data-sp-theme-toggle]").forEach(function (b) { b.setAttribute("aria-pressed", t === "dark"); });
  }

  // Confirm dialog: add data-sp-confirm="Message" to any <form> that deletes something.
  var dlg = d.getElementById("sp-confirm");
  function ask(msg, label, ok) {
    if (!dlg || !dlg.showModal) { if (window.confirm(msg)) ok(); return; }
    d.getElementById("sp-confirm-msg").textContent = msg;
    d.getElementById("sp-confirm-yes").textContent = label || "Delete";
    dlg.returnValue = "";
    dlg.addEventListener("close", function h() {
      dlg.removeEventListener("close", h);
      if (dlg.returnValue === "yes") ok();
    });
    dlg.showModal();
  }

  d.addEventListener("click", function (e) {
    var t = e.target;
    if (t.closest("[data-sp-theme-toggle]")) {
      var cur = r.getAttribute("data-sp-theme") || (matchMedia("(prefers-color-scheme:dark)").matches ? "dark" : "light");
      setTheme(cur === "dark" ? "light" : "dark");
    } else if (t.closest("[data-sp-open]")) { d.body.classList.add("sp-nav-open"); }
    else if (t.closest("[data-sp-close]")) { d.body.classList.remove("sp-nav-open"); }
    else if (t.closest("[data-sp-dismiss]")) { t.closest(".sp-toast").remove(); }
  });
  d.addEventListener("keydown", function (e) { if (e.key === "Escape") d.body.classList.remove("sp-nav-open"); });

  d.addEventListener("submit", function (e) {
    var f = e.target, msg = f.getAttribute && f.getAttribute("data-sp-confirm");
    if (!msg || f._spOk) return;
    e.preventDefault();
    ask(msg, f.getAttribute("data-sp-confirm-label"), function () { f._spOk = true; f.requestSubmit(e.submitter || undefined); });
  });

  // Highlight the longest nav link matching the current path (Overview must match exactly).
  var p = location.pathname, best = null, len = -1;
  d.querySelectorAll(".sp-nav a[href]").forEach(function (a) {
    var h = a.getAttribute("href");
    if (!h || h.charAt(0) !== "/") return;
    var hit = a.hasAttribute("data-exact") ? p === h : (p === h || p.indexOf(h) === 0);
    if (hit && h.length > len) { best = a; len = h.length; }
  });
  if (best) best.setAttribute("aria-current", "page");

  // Success messages fade out after 5s; errors stay until dismissed.
  setTimeout(function () { d.querySelectorAll(".sp-toast--success,.sp-toast--info").forEach(function (n) { n.remove(); }); }, 5000);
})();
