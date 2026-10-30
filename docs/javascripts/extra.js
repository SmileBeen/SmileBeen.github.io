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
      // 좁은 화면: 지도 전체를 화면 폭에 맞춰 축소, 버튼으로 원래 크기(옆으로 스크롤)
      var map = rm.querySelector(".rm-map"), sc = rm.querySelector(".rm-scroll"), zb = rm.querySelector("[data-rm-zoom]");
      function fit(on) {
        if (!map || !sc) return;
        var narrow = window.matchMedia("(max-width: 1000px)").matches;
        if (!narrow) { map.style.zoom = ""; rm.removeAttribute("data-fit"); return; }
        if (on) { map.style.zoom = String(Math.min(1, (sc.clientWidth - 32) / 1180)); rm.setAttribute("data-fit", "1"); }
        else { map.style.zoom = ""; rm.removeAttribute("data-fit"); }
        if (zb) zb.innerHTML = on ? '<span class="rm-ko">크게 보기</span><span class="rm-en" lang="en">Enlarge</span>' : '<span class="rm-ko">한눈에 보기</span><span class="rm-en" lang="en">Fit</span>';
      }
      fit(true);
      window.addEventListener("resize", function () { fit(rm.getAttribute("data-fit") === "1" || !window.matchMedia("(max-width: 1000px)").matches); });
      if (zb) zb.addEventListener("click", function () { fit(rm.getAttribute("data-fit") !== "1"); });
      // 칸을 누르면 연결된 회차 목록이 펼쳐져요. 지도가 옆으로 밀리거나 축소돼도 안 잘리게 fixed 로 띄워요.
      var pop = rm.querySelector("[data-rm-pop]"), body = pop && pop.querySelector(".rm-pop__body"), open = null;
      function place() {
        if (!open || !pop) return;
        var r = open.getBoundingClientRect();
        if (r.bottom < 0 || r.top > window.innerHeight) { close(); return; }
        var w = pop.offsetWidth, h = pop.offsetHeight, pad = 8;
        var left = Math.min(Math.max(pad, r.left + r.width / 2 - w / 2), window.innerWidth - w - pad);
        var top = r.bottom + 10;
        if (top + h > window.innerHeight - pad) top = Math.max(pad, r.top - h - 10);
        pop.style.left = left + "px";
        pop.style.top = top + "px";
      }
      function close() {
        if (!open || !pop) return;
        open.setAttribute("aria-expanded", "false");
        open = null;
        pop.hidden = true;
      }
      function show(btn) {
        if (!pop || !body) return;
        if (open === btn) { close(); return; }
        close();
        var tpl = btn.querySelector(".rm-item__data");
        if (!tpl) return;
        body.innerHTML = "";
        body.appendChild(tpl.content.cloneNode(true));
        open = btn;
        btn.setAttribute("aria-expanded", "true");
        pop.hidden = false;
        place();
      }
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
          close();
          return;
        }
        if (ev.target.closest("[data-rm-pop-close]")) { close(); return; }
        var it = ev.target.closest("[data-rm-item]");
        if (it && rm.contains(it)) { show(it); return; }
      });
      document.addEventListener("keydown", function (ev) { if (ev.key === "Escape") close(); });
      document.addEventListener("click", function (ev) {
        if (!open) return;
        if (ev.target.closest("[data-rm-pop]") || ev.target.closest("[data-rm-item]")) return;
        close();
      });
      window.addEventListener("resize", place);
      window.addEventListener("scroll", place, true);

      // 주소에 #rm-<칸 주소> 로 오면 그 칸을 찾아 펼쳐요 (회차 페이지의 '채우는 칸' 칩이 이렇게 보냅니다).
      // 칸 주소에 점이 들어가서 querySelector 의 #id 로는 못 찾아요 — id 를 직접 맞춰 봐요.
      function fromHash() {
        var id = "";
        try { id = decodeURIComponent((location.hash || "").slice(1)); } catch (e) { return; }
        if (id.indexOf("rm-") !== 0) return;
        var el = null;
        rm.querySelectorAll("[id]").forEach(function (x) { if (x.id === id) el = x; });
        if (!el) return;
        rm.querySelectorAll(".is-hit").forEach(function (x) { x.classList.remove("is-hit"); });
        if (el.scrollIntoView) el.scrollIntoView({ block: "center", inline: "center" });
        el.classList.add("is-hit");
        if (el.hasAttribute("data-rm-item")) setTimeout(function () { show(el); }, 80);
      }
      fromHash();
      window.addEventListener("hashchange", fromHash);
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", setup); else setup();
})();
