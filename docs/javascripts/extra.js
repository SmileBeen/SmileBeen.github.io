/* 허브 거르기 버튼 · 태그 선택. Material의 instant loading을 쓰지 않으니 페이지마다 한 번 실행돼요. */
(function () {
  function setup() {
    // 프로젝트 · 부품 거르기: data-filter="status|proj", data-target="#목록"
    var targets = {};
    document.querySelectorAll(".hb-filter[data-filter]").forEach(function (g) {
      var sel = g.getAttribute("data-target");
      (targets[sel] = targets[sel] || []).push(g);
      g.addEventListener("click", function (ev) {
        var b = ev.target.closest("button[data-v]");
        if (!b) return;
        g.querySelectorAll("button[data-v]").forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
        apply(sel);
      });
    });
    function apply(sel) {
      var root = document.querySelector(sel);
      if (!root) return;
      var want = {};
      targets[sel].forEach(function (g) {
        var on = g.querySelector('button[aria-pressed="true"]');
        want[g.getAttribute("data-filter")] = on ? on.getAttribute("data-v") : "all";
      });
      var shown = 0;
      root.querySelectorAll("[data-status]").forEach(function (el) {
        var ok = Object.keys(want).every(function (k) {
          var v = want[k];
          if (v === "all") return true;
          var have = (el.getAttribute("data-" + k) || "").split(" ");
          return have.indexOf(v) >= 0 || el.getAttribute("data-" + k) === v;
        });
        el.hidden = !ok;
        if (ok) shown++;
      });
      root.querySelectorAll(".hb-pgroup").forEach(function (sec) {
        sec.hidden = !sec.querySelector("[data-status]:not([hidden])");
      });
      var empty = root.parentNode.querySelector(":scope > .hb-empty");
      if (empty) empty.hidden = shown > 0;
    }

    // 태그 페이지: 버튼 하나 고르면 그 패널만 보여요. 주소 #태그 로도 열려요.
    var pick = document.getElementById("hb-tagpick");
    if (pick) {
      var btns = pick.querySelectorAll(".hb-tagbtn");
      var panels = document.querySelectorAll(".hb-tagpanel");
      function show(name) {
        var found = false;
        btns.forEach(function (b) { var on = b.getAttribute("data-tag") === name; b.setAttribute("aria-pressed", on ? "true" : "false"); found = found || on; });
        panels.forEach(function (p) { p.hidden = p.getAttribute("data-tag") !== name; });
        return found;
      }
      pick.addEventListener("click", function (ev) {
        var b = ev.target.closest(".hb-tagbtn");
        if (!b) return;
        var name = b.getAttribute("data-tag");
        show(name);
        try { history.replaceState(null, "", "#" + encodeURIComponent(name)); } catch (e) {}
      });
      var h = decodeURIComponent((location.hash || "").slice(1));
      if (!h || !show(h)) show(btns.length ? btns[0].getAttribute("data-tag") : "");
    }
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", setup); else setup();
})();

/* 로드맵 지도: 한글/EN 전환(기본 한글, 브라우저에 기억) · 표시 거르기 */
(function () {
  function setup() {
    var saved = null;
    try { saved = localStorage.getItem("hb-rm-lang"); } catch (e) {}
    document.querySelectorAll(".rm").forEach(function (rm) {
      function lang(v) {
        rm.setAttribute("data-lang", v);
        rm.querySelectorAll("[data-rm-lang]").forEach(function (b) { b.setAttribute("aria-pressed", b.getAttribute("data-rm-lang") === v ? "true" : "false"); });
      }
      if (saved === "en") lang("en");
      rm.addEventListener("click", function (ev) {
        var b = ev.target.closest("[data-rm-lang]");
        if (b) {
          var v = b.getAttribute("data-rm-lang");
          lang(v);
          try { localStorage.setItem("hb-rm-lang", v); } catch (e) {}
          return;
        }
        var w = ev.target.closest("[data-rm-view]");
        if (w) {
          rm.setAttribute("data-view", w.getAttribute("data-rm-view"));
          rm.querySelectorAll("[data-rm-view]").forEach(function (x) { x.setAttribute("aria-pressed", x === w ? "true" : "false"); });
        }
      });
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", setup); else setup();
})();
