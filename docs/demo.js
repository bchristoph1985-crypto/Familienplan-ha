/* Sternchenplan · Demo zum Ausprobieren und sanfte Einblend-Animationen. Keine externen Ressourcen. */
(function () {
  "use strict";
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* Einblenden beim Scrollen */
  var targets = document.querySelectorAll(".section-head, .steps article, .gallery figure, .plan, .day li, .price-card, details, .demo-shell");
  if (!reduce && "IntersectionObserver" in window) {
    document.documentElement.classList.add("anim");
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add("shown"); io.unobserve(e.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px" });
    targets.forEach(function (t, i) { t.style.transitionDelay = (i % 3) * 70 + "ms"; io.observe(t); });
  }

  /* Demo */
  var root = document.getElementById("demo-app");
  if (!root) return;

  var start = function () {
    return {
      view: "kind",
      points: 32,
      tasks: [
        { id: "muell", name: "Müll rausbringen", due: "heute 19:00", pts: 2, state: "open" },
        { id: "zimmer", name: "Zimmer aufräumen", due: "heute 19:00", pts: 3, state: "open", photo: true },
        { id: "tisch", name: "Tisch decken", due: "heute 18:30", pts: 1, state: "open" }
      ],
      rewards: [
        { id: "film", emoji: "🎬", name: "Filmabend aussuchen", cost: 40 },
        { id: "bild", emoji: "🎮", name: "30 Min. extra Bildschirmzeit", cost: 15 }
      ],
      pending: [],
      locked: false,
      evening: false,
      toast: ""
    };
  };
  var s = start();

  function esc(t) { return String(t).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function openCount() { return s.tasks.filter(function (t) { return t.state === "open"; }).length; }
  function doneCount() { return s.tasks.filter(function (t) { return t.state === "done"; }).length; }

  function ring(done, total) {
    var r = 26, c = 2 * Math.PI * r, f = total ? done / total : 0;
    return '<svg class="d-ring" viewBox="0 0 64 64" aria-hidden="true"><circle cx="32" cy="32" r="' + r + '" class="d-ring-bg"/>' +
      (f > 0 ? '<circle cx="32" cy="32" r="' + r + '" class="d-ring-fg" stroke-dasharray="' + (c * f) + ' ' + c + '"/>' : "") +
      '<text x="32" y="37" text-anchor="middle">' + done + "/" + total + "</text></svg>";
  }

  function kidView() {
    var left = openCount();
    var h = '<div class="d-hero"><div class="d-avatar">M</div><div><b>Hallo Mia 👋</b><small>' +
      (left ? "Noch " + left + " für heute" : "Alles geschafft für heute 🎉") +
      '</small><span class="d-pts" id="d-pts">⭐ ' + s.points + " Sterne</span></div>" + ring(doneCount(), s.tasks.length) + "</div>";
    h += '<p class="d-title">Heute</p><ul class="d-tasks">';
    s.tasks.forEach(function (t) {
      h += '<li class="d-task ' + t.state + '"><div><b>' + esc(t.name) + (t.photo ? " 📷" : "") + "</b><small>" +
        (t.state === "done" ? "erledigt ✓" : t.state === "wait" ? "wartet auf Freigabe" : esc(t.due)) +
        '</small></div><span class="d-plus">+' + t.pts + "</span>";
      if (t.state === "open") {
        h += '<button type="button" data-act="claim" data-id="' + t.id + '">' + (t.photo ? "📷 Foto &amp; erledigt" : "✓ Erledigt") + "</button>";
      } else if (t.state === "wait") {
        h += '<span class="d-chip">⏳</span>';
      } else {
        h += '<span class="d-chip ok">✓</span>';
      }
      h += "</li>";
    });
    h += '</ul><p class="d-title">🎁 Belohnungen</p><div class="d-rewards">';
    s.rewards.forEach(function (r) {
      var pend = s.pending.some(function (p) { return p.kind === "reward" && p.id === r.id; });
      var pct = Math.min(100, Math.round(s.points / r.cost * 100));
      var ok = s.points >= r.cost;
      h += '<div class="d-reward' + (ok ? " ready" : "") + '"><span class="d-emoji">' + r.emoji + "</span><b>" + esc(r.name) + "</b><small>⭐ " + r.cost +
        '</small><span class="d-bar"><i style="width:' + pct + '%"></i></span>' +
        (pend ? '<span class="d-note">wartet auf Mama oder Papa</span>' :
          ok ? '<button type="button" data-act="redeem" data-id="' + r.id + '">Einlösen</button>' :
            '<span class="d-note">noch ' + (r.cost - s.points) + " Sterne</span>") + "</div>";
    });
    return h + "</div>";
  }

  function parentView() {
    var h = '<p class="d-title">Freigaben' + (s.pending.length ? ' <span class="d-badge">' + s.pending.length + "</span>" : "") + "</p>";
    if (!s.pending.length) {
      h += '<p class="d-empty">Nichts zu tun. Wechsle zu Mia und hake etwas ab oder löse eine Belohnung ein.</p>';
    } else {
      h += '<ul class="d-tasks">';
      s.pending.forEach(function (p, i) {
        h += '<li class="d-task ask"><div><b>' + esc(p.label) + "</b><small>" + esc(p.sub) + "</small></div>" +
          (p.kind === "task" ? '<span class="d-photo" aria-hidden="true">🧸</span>' : "") +
          '<span class="d-acts"><button type="button" class="d-ghost" data-act="reject" data-i="' + i + '">Ablehnen</button>' +
          '<button type="button" data-act="approve" data-i="' + i + '">Bestätigen</button></span></li>';
      });
      h += "</ul>";
    }
    h += '<p class="d-title">Internetsperre</p><div class="d-lock ' + (s.locked ? "on" : "") + '">' +
      '<span class="d-emoji">🎮</span><div><b>Konsole von Mia</b><small>' +
      (s.locked ? "Gesperrt, " + openCount() + " Aufgabe(n) offen" : s.evening ? "Online, alles erledigt" : "Online") + "</small></div>" +
      (s.evening ? "" : '<button type="button" data-act="evening">20:00 simulieren</button>') + "</div>";
    if (s.locked) h += '<p class="d-empty">Wechsle zu Mia und erledige den Rest. Dann geht das Internet von selbst wieder an.</p>';
    return h;
  }

  function render() {
    var tabs = '<div class="d-tabs" role="tablist">' +
      '<button type="button" role="tab" aria-selected="' + (s.view === "kind") + '" data-act="view" data-v="kind">👧 Mia</button>' +
      '<button type="button" role="tab" aria-selected="' + (s.view === "eltern") + '" data-act="view" data-v="eltern">👪 Eltern' +
      (s.pending.length ? ' <span class="d-badge">' + s.pending.length + "</span>" : "") + "</button></div>";
    root.innerHTML = tabs + '<div class="d-body">' + (s.view === "kind" ? kidView() : parentView()) + "</div>" +
      '<div class="d-foot"><span class="d-toast" role="status" aria-live="polite">' + esc(s.toast) + '</span><button type="button" class="d-ghost" data-act="reset">Neu starten</button></div>';
  }

  function celebrate(btn, text) {
    if (reduce || !btn) return;
    var fx = document.createElement("div");
    fx.className = "d-fx";
    var box = root.getBoundingClientRect(), b = btn.getBoundingClientRect();
    fx.style.left = (b.left - box.left + b.width / 2) + "px";
    fx.style.top = (b.top - box.top) + "px";
    var colors = ["#4f7cff", "#ff7a45", "#22a565", "#a259ff", "#e5a100", "#f0508c"];
    var html = '<b class="d-fx-text">' + text + "</b>";
    for (var i = 0; i < 18; i++) {
      var a = Math.random() * Math.PI * 2, d = 40 + Math.random() * 50;
      html += '<i style="--x:' + Math.cos(a) * d + "px;--y:" + (Math.sin(a) * d - 20) + "px;background:" + colors[i % colors.length] + ";animation-delay:" + (i * 8) + 'ms"></i>';
    }
    fx.innerHTML = html;
    root.appendChild(fx);
    setTimeout(function () { fx.remove(); }, 1000);
  }

  function bumpPoints() {
    var el = document.getElementById("d-pts");
    if (el && !reduce) { el.classList.remove("bump"); void el.offsetWidth; el.classList.add("bump"); }
  }

  function relock() { if (s.evening) s.locked = openCount() > 0; }

  root.addEventListener("click", function (ev) {
    var btn = ev.target.closest("button[data-act]");
    if (!btn) return;
    var act = btn.getAttribute("data-act");
    var rect = null;
    if (act === "view") { s.view = btn.getAttribute("data-v"); s.toast = ""; }
    else if (act === "reset") { s = start(); }
    else if (act === "claim") {
      var t = s.tasks.filter(function (x) { return x.id === btn.getAttribute("data-id"); })[0];
      if (t.photo) {
        t.state = "wait";
        s.pending.push({ kind: "task", id: t.id, label: t.name, sub: "Mia · mit Foto · +" + t.pts + " Sterne" });
        s.toast = "📸 Foto geschickt. Jetzt bei den Eltern freigeben.";
        relock(); render(); return;
      }
      t.state = "done"; s.points += t.pts; relock();
      s.toast = openCount() ? "+" + t.pts + " Sterne für Mia" : "Alles erledigt! 🎉";
      rect = btn; render(); celebrate(root.querySelector(".d-hero .d-ring") || rect, "Super!"); bumpPoints(); return;
    }
    else if (act === "redeem") {
      var r = s.rewards.filter(function (x) { return x.id === btn.getAttribute("data-id"); })[0];
      s.points -= r.cost;
      s.pending.push({ kind: "reward", id: r.id, cost: r.cost, label: r.emoji + " " + r.name, sub: "Mia möchte einlösen · " + r.cost + " Sterne" });
      s.toast = "Eingelöst. Mama oder Papa bekommen eine Nachricht.";
    }
    else if (act === "approve" || act === "reject") {
      var p = s.pending.splice(+btn.getAttribute("data-i"), 1)[0];
      if (p.kind === "task") {
        var tk = s.tasks.filter(function (x) { return x.id === p.id; })[0];
        if (act === "approve") { tk.state = "done"; s.points += tk.pts; s.toast = "Bestätigt: +" + tk.pts + " Sterne für Mia"; }
        else { tk.state = "open"; s.toast = "Abgelehnt. Mia muss nochmal ran."; }
        relock();
      } else {
        if (act === "reject") { s.points += p.cost; s.toast = "Abgelehnt. Die Sterne gibt es zurück."; }
        else { s.toast = "Viel Spaß beim " + p.label.replace(/^\S+\s/, "") + "!"; }
      }
      render();
      if (act === "approve") celebrate(root.querySelector(".d-tabs"), "✓");
      return;
    }
    else if (act === "evening") {
      s.evening = true; relock();
      s.toast = s.locked ? "20:00: Noch Aufgaben offen, die Konsole ist offline." : "20:00: Alles erledigt, die Konsole bleibt online.";
    }
    render();
  });

  render();
})();
