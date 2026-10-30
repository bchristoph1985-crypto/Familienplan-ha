/* Sternchenplan · interactive demo and gentle fade-in animations (English). No external resources. */
(function () {
  "use strict";
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* Fade in on scroll */
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
        { id: "muell", name: "Take out the trash", due: "today 7:00 PM", pts: 2, state: "open" },
        { id: "zimmer", name: "Tidy your room", due: "today 7:00 PM", pts: 3, state: "open", photo: true },
        { id: "tisch", name: "Set the table", due: "today 6:30 PM", pts: 1, state: "open" }
      ],
      rewards: [
        { id: "film", emoji: "🎬", name: "Pick movie night", cost: 40 },
        { id: "bild", emoji: "🎮", name: "30 min extra screen time", cost: 15 }
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
    var h = '<div class="d-hero"><div class="d-avatar">M</div><div><b>Hi Mia 👋</b><small>' +
      (left ? left + " left for today" : "All done for today 🎉") +
      '</small><span class="d-pts" id="d-pts">⭐ ' + s.points + " stars</span></div>" + ring(doneCount(), s.tasks.length) + "</div>";
    h += '<p class="d-title">Today</p><ul class="d-tasks">';
    s.tasks.forEach(function (t) {
      h += '<li class="d-task ' + t.state + '"><div><b>' + esc(t.name) + (t.photo ? " 📷" : "") + "</b><small>" +
        (t.state === "done" ? "done ✓" : t.state === "wait" ? "waiting for approval" : esc(t.due)) +
        '</small></div><span class="d-plus">+' + t.pts + "</span>";
      if (t.state === "open") {
        h += '<button type="button" data-act="claim" data-id="' + t.id + '">' + (t.photo ? "📷 Photo &amp; done" : "✓ Done") + "</button>";
      } else if (t.state === "wait") {
        h += '<span class="d-chip">⏳</span>';
      } else {
        h += '<span class="d-chip ok">✓</span>';
      }
      h += "</li>";
    });
    h += '</ul><p class="d-title">🎁 Rewards</p><div class="d-rewards">';
    s.rewards.forEach(function (r) {
      var pend = s.pending.some(function (p) { return p.kind === "reward" && p.id === r.id; });
      var pct = Math.min(100, Math.round(s.points / r.cost * 100));
      var ok = s.points >= r.cost;
      h += '<div class="d-reward' + (ok ? " ready" : "") + '"><span class="d-emoji">' + r.emoji + "</span><b>" + esc(r.name) + "</b><small>⭐ " + r.cost +
        '</small><span class="d-bar"><i style="width:' + pct + '%"></i></span>' +
        (pend ? '<span class="d-note">waiting for Mum or Dad</span>' :
          ok ? '<button type="button" data-act="redeem" data-id="' + r.id + '">Redeem</button>' :
            '<span class="d-note">' + (r.cost - s.points) + " stars to go</span>") + "</div>";
    });
    return h + "</div>";
  }

  function parentView() {
    var h = '<p class="d-title">Approvals' + (s.pending.length ? ' <span class="d-badge">' + s.pending.length + "</span>" : "") + "</p>";
    if (!s.pending.length) {
      h += '<p class="d-empty">Nothing to do. Switch to Mia and tick something off or redeem a reward.</p>';
    } else {
      h += '<ul class="d-tasks">';
      s.pending.forEach(function (p, i) {
        h += '<li class="d-task ask"><div><b>' + esc(p.label) + "</b><small>" + esc(p.sub) + "</small></div>" +
          (p.kind === "task" ? '<span class="d-photo" aria-hidden="true">🧸</span>' : "") +
          '<span class="d-acts"><button type="button" class="d-ghost" data-act="reject" data-i="' + i + '">Reject</button>' +
          '<button type="button" data-act="approve" data-i="' + i + '">Approve</button></span></li>';
      });
      h += "</ul>";
    }
    h += '<p class="d-title">Internet lock</p><div class="d-lock ' + (s.locked ? "on" : "") + '">' +
      '<span class="d-emoji">🎮</span><div><b>Mia&#39;s console</b><small>' +
      (s.locked ? "Locked, " + openCount() + " chore(s) open" : s.evening ? "Online, all done" : "Online") + "</small></div>" +
      (s.evening ? "" : '<button type="button" data-act="evening">Simulate 8 PM</button>') + "</div>";
    if (s.locked) h += '<p class="d-empty">Switch to Mia and finish the rest. The internet comes back on by itself.</p>';
    return h;
  }

  function render() {
    var tabs = '<div class="d-tabs" role="tablist">' +
      '<button type="button" role="tab" aria-selected="' + (s.view === "kind") + '" data-act="view" data-v="kind">👧 Mia</button>' +
      '<button type="button" role="tab" aria-selected="' + (s.view === "eltern") + '" data-act="view" data-v="eltern">👪 Parents' +
      (s.pending.length ? ' <span class="d-badge">' + s.pending.length + "</span>" : "") + "</button></div>";
    root.innerHTML = tabs + '<div class="d-body">' + (s.view === "kind" ? kidView() : parentView()) + "</div>" +
      '<div class="d-foot"><span class="d-toast" role="status" aria-live="polite">' + esc(s.toast) + '</span><button type="button" class="d-ghost" data-act="reset">Start over</button></div>';
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
        s.pending.push({ kind: "task", id: t.id, label: t.name, sub: "Mia · with photo · +" + t.pts + " stars" });
        s.toast = "📸 Photo sent. Now approve it as a parent.";
        relock(); render(); return;
      }
      t.state = "done"; s.points += t.pts; relock();
      s.toast = openCount() ? "+" + t.pts + " stars for Mia" : "All done! 🎉";
      rect = btn; render(); celebrate(root.querySelector(".d-hero .d-ring") || rect, "Great!"); bumpPoints(); return;
    }
    else if (act === "redeem") {
      var r = s.rewards.filter(function (x) { return x.id === btn.getAttribute("data-id"); })[0];
      s.points -= r.cost;
      s.pending.push({ kind: "reward", id: r.id, cost: r.cost, label: r.emoji + " " + r.name, sub: "Mia wants to redeem · " + r.cost + " stars" });
      s.toast = "Redeemed. Mum or Dad get a notification.";
    }
    else if (act === "approve" || act === "reject") {
      var p = s.pending.splice(+btn.getAttribute("data-i"), 1)[0];
      if (p.kind === "task") {
        var tk = s.tasks.filter(function (x) { return x.id === p.id; })[0];
        if (act === "approve") { tk.state = "done"; s.points += tk.pts; s.toast = "Approved: +" + tk.pts + " stars for Mia"; }
        else { tk.state = "open"; s.toast = "Rejected. Mia needs another go."; }
        relock();
      } else {
        if (act === "reject") { s.points += p.cost; s.toast = "Rejected. The stars are refunded."; }
        else { s.toast = "Enjoy: " + p.label.replace(/^\S+\s/, "") + "!"; }
      }
      render();
      if (act === "approve") celebrate(root.querySelector(".d-tabs"), "✓");
      return;
    }
    else if (act === "evening") {
      s.evening = true; relock();
      s.toast = s.locked ? "8 PM: Chores still open, the console is offline." : "8 PM: All done, the console stays online.";
    }
    render();
  });

  render();
})();
