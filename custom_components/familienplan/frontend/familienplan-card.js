/*
 * Familienplan-Karte für das Home-Assistant-Dashboard.
 *
 *   type: custom:familienplan-card
 *   mode: auto        # auto | kind | eltern  (auto: Eltern sehen die Eltern-Ansicht)
 *   member: Lucas     # optional: immer dieses Kind zeigen (z. B. Tablet im Kinderzimmer)
 *   readonly: false   # true: nur anzeigen, keine Knöpfe (z. B. Küchen-Tablet)
 *
 * Daten kommen per Websocket (familienplan/subscribe), Änderungen laufen über
 * die Dienste. Home Assistant prüft dort, wer was darf.
 */

const VERSION = "0.13.0";

const T = {
  de: {
    hello: "Hallo {name}",
    points: "{n} Punkte",
    done: "Erledigt",
    allDone: "Alles erledigt 🎉",
    waiting: "Wartet auf Freigabe",
    undo: "Zurücknehmen",
    overdue: "überfällig",
    today: "heute {time}",
    tomorrow: "morgen {time}",
    noDue: "ohne Frist",
    tabToday: "Heute",
    tabApprove: "Freigaben",
    tabChores: "Aufgaben",
    tabAway: "Abwesend",
    approve: "Freigeben",
    reject: "Ablehnen",
    nothingToApprove: "Nichts freizugeben.",
    doneFor: "Erledigt für {name}",
    newChore: "Neue Aufgabe",
    name: "Name",
    assignees: "Wer",
    recurrence: "Wiederholung",
    due: "Frist",
    rotation: "Reihum",
    approval: "Freigabe nötig",
    create: "Anlegen",
    save: "Speichern",
    cancel: "Abbrechen",
    edit: "Bearbeiten",
    editChore: "Aufgabe bearbeiten",
    delete: "Löschen",
    confirmDelete: "„{name}“ wirklich löschen?",
    away: "abwesend bis {date}",
    awayPlanned: "abwesend {from} bis {date}",
    present: "da",
    until: "Bis",
    substitute: "Vertretung",
    none: "keine",
    setAway: "Abwesend eintragen",
    endAway: "Zurück",
    notSetUp: "Familienplan ist nicht eingerichtet.",
    noMember: "Dieses Konto gehört zu keinem Familienmitglied.",
    paused: "ruht",
    locked: "🔒 Internet gesperrt",
    pass: "Freikarte bis {time}",
    givePass: "Freikarte",
    takePass: "Freikarte weg",
    pointsLabel: "Punkte",
    photo: "Fotonachweis (Foto sehen nur Eltern)",
    photoDone: "📷 Foto & erledigt",
    photoOf: "Foto ansehen",
    lastPhoto: "Letztes Foto",
    minAge: "Ab Alter",
    fromAge: "ab {n} J.",
    years: "{n} J.",
    tabRewards: "Belohnungen",
    rewards: "Belohnungen",
    redeem: "Einlösen",
    missing: "noch {n} Punkte",
    confirmRedeem: "„{name}“ für {n} Punkte einlösen?",
    waitingParents: "Wartet auf die Eltern",
    wantsReward: "möchte einlösen",
    give: "Bekommt es",
    refuse: "Ablehnen",
    newReward: "Neue Belohnung",
    editReward: "Belohnung bearbeiten",
    forWhom: "Für wen",
    allChildren: "alle Kinder",
    forWhomHint: "nichts angehakt = alle Kinder",
    cost: "Punkte",
    noRewards: "Noch keine Belohnungen. Lege oben die erste an.",
    uploading: "Foto wird hochgeladen …",
    helpOthers: "Geschwistern helfen",
    helpHint: "Übernimm eine Aufgabe und hol dir die Punkte.",
    takeOver: "Übernehmen",
    takenFrom: "übernommen für {name}",
    double: "doppelte Punkte",
    trial: "Pro-Testphase: noch {n} Tage",
    free: "Kostenlose Version",
    proHint: "Pro freischalten: Einstellungen › Geräte & Dienste › Familienplan › Konfigurieren › Pro / Lizenz",
    proOnly: "Gehört zu Pro",
    awayPro: "Abwesenheit mit Vertretung gehört zu Pro.",
    whoAreYou: "Wer bist du?",
    leftToday: "Noch {n} für heute",
    leftOne: "Noch eine Aufgabe für heute",
    allDoneToday: "Alles geschafft für heute!",
    todayTitle: "Heute",
    doneShort: "Erledigt",
    great: ["Super!", "Stark!", "Klasse!", "Weiter so!", "Spitze!"],
    openCount: "{n} offen",
    finished: "Fertig",
    rec: { none: "einmalig", daily: "täglich", weekly: "wöchentlich", biweekly: "alle 2 Wochen" },
  },
  en: {
    hello: "Hi {name}",
    points: "{n} points",
    done: "Done",
    allDone: "All done 🎉",
    waiting: "Waiting for approval",
    undo: "Undo",
    overdue: "overdue",
    today: "today {time}",
    tomorrow: "tomorrow {time}",
    noDue: "no due date",
    tabToday: "Today",
    tabApprove: "Approvals",
    tabChores: "Chores",
    tabAway: "Away",
    approve: "Approve",
    reject: "Reject",
    nothingToApprove: "Nothing to approve.",
    doneFor: "Done for {name}",
    newChore: "New chore",
    name: "Name",
    assignees: "Who",
    recurrence: "Repeat",
    due: "Due",
    rotation: "Take turns",
    approval: "Needs approval",
    create: "Create",
    save: "Save",
    cancel: "Cancel",
    edit: "Edit",
    editChore: "Edit chore",
    delete: "Delete",
    confirmDelete: "Really delete “{name}”?",
    away: "away until {date}",
    awayPlanned: "away {from} to {date}",
    present: "home",
    until: "Until",
    substitute: "Substitute",
    none: "none",
    setAway: "Set away",
    endAway: "Back",
    notSetUp: "Familienplan is not set up.",
    noMember: "This account is not linked to a family member.",
    paused: "paused",
    locked: "🔒 Internet locked",
    pass: "Free pass until {time}",
    givePass: "Free pass",
    takePass: "Remove pass",
    pointsLabel: "Points",
    photo: "Photo proof (only parents see it)",
    photoDone: "📷 Photo & done",
    photoOf: "View photo",
    lastPhoto: "Last photo",
    minAge: "Minimum age",
    fromAge: "{n}+",
    years: "{n} y",
    tabRewards: "Rewards",
    rewards: "Rewards",
    redeem: "Redeem",
    missing: "{n} points to go",
    confirmRedeem: "Redeem “{name}” for {n} points?",
    waitingParents: "Waiting for a parent",
    wantsReward: "wants to redeem",
    give: "Give it",
    refuse: "Reject",
    newReward: "New reward",
    editReward: "Edit reward",
    forWhom: "For whom",
    allChildren: "all children",
    forWhomHint: "none ticked = all children",
    cost: "Points",
    noRewards: "No rewards yet. Create the first one above.",
    uploading: "Uploading photo …",
    helpOthers: "Help your siblings",
    helpHint: "Take over a chore and earn the points.",
    takeOver: "Take over",
    takenFrom: "taken over for {name}",
    double: "double points",
    trial: "Pro trial: {n} days left",
    free: "Free version",
    proHint: "Unlock Pro: Settings › Devices & services › Familienplan › Configure › Pro / license",
    proOnly: "Part of Pro",
    awayPro: "Absence with substitute is part of Pro.",
    whoAreYou: "Who are you?",
    leftToday: "{n} left for today",
    leftOne: "One chore left for today",
    allDoneToday: "All done for today!",
    todayTitle: "Today",
    doneShort: "Done",
    great: ["Great!", "Awesome!", "Nice!", "Keep going!", "Brilliant!"],
    openCount: "{n} open",
    finished: "Done",
    rec: { none: "once", daily: "daily", weekly: "weekly", biweekly: "every 2 weeks" },
  },
};

const esc = (value) =>
  String(value ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);

class FamilienplanCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._data = null;
    this._error = null;
    this._tab = "today";
    this._form = this._emptyForm();
    this._awayForm = {};
    this._rewardForm = this._emptyReward();
    this._busy = false;
    // Familientablet: welches Kind gerade dran ist
    this._actingAs = null;
    this._idleTimer = null;
    this.shadowRoot.addEventListener("click", (ev) => this._onClick(ev));
    this.shadowRoot.addEventListener("input", (ev) => this._onInput(ev));
    this.shadowRoot.addEventListener("change", (ev) => this._onInput(ev));
  }

  setConfig(config) {
    this._config = { mode: "auto", readonly: false, ...config };
    this._render();
  }

  set hass(hass) {
    const first = !this._hass;
    this._hass = hass;
    if (first) this._subscribe();
  }

  connectedCallback() {
    if (this._hass && !this._unsub) this._subscribe();
  }

  disconnectedCallback() {
    if (this._unsub) {
      this._unsub.then((unsub) => unsub()).catch(() => {});
      this._unsub = null;
    }
  }

  getCardSize() {
    return 4;
  }

  static getStubConfig() {
    return { mode: "auto" };
  }

  // -- Daten -----------------------------------------------------------------

  _subscribe() {
    this._unsub = this._hass.connection
      .subscribeMessage(
        (data) => {
          this._data = data;
          this._error = null;
          this._render();
        },
        { type: "familienplan/subscribe" },
      )
      .catch((err) => {
        this._error = err.code === "not_loaded" ? this._t("notSetUp") : err.message;
        this._unsub = null;
        this._render();
      });
  }

  _t(key, vars = {}) {
    const lang = (this._hass?.locale?.language || this._hass?.language || "de").startsWith("de") ? "de" : "en";
    let text = T[lang][key] ?? key;
    if (typeof text === "string") {
      for (const [k, v] of Object.entries(vars)) text = text.replace(`{${k}}`, v);
    }
    return text;
  }

  _locale() {
    return this._hass?.locale?.language || this._hass?.language || "de";
  }

  _member(id) {
    return this._data?.members.find((m) => m.id === id);
  }

  // Wer bedient gerade? Am Familientablet das ausgewählte Kind.
  _me() {
    return this._data?.tablet ? this._actingAs : this._data?.me;
  }

  // Am Familientablet nach einer Minute ohne Tippen zurück zur Namensauswahl,
  // damit das nächste Kind nicht im falschen Namen abhakt.
  _touchIdle() {
    clearTimeout(this._idleTimer);
    if (!this._actingAs) return;
    this._idleTimer = setTimeout(() => {
      this._actingAs = null;
      this._render();
    }, 60000);
  }

  _memberByConfig() {
    const wanted = String(this._config.member || "").toLowerCase();
    return this._data.members.find((m) => m.id === this._config.member || m.name.toLowerCase() === wanted);
  }

  async _call(service, data) {
    if (this._busy) return;
    this._busy = true;
    try {
      await this._hass.callService("familienplan", service, data);
    } catch (err) {
      this.dispatchEvent(
        new CustomEvent("hass-notification", { detail: { message: err.message }, bubbles: true, composed: true }),
      );
    } finally {
      this._busy = false;
    }
  }

  _notify(message) {
    this.dispatchEvent(new CustomEvent("hass-notification", { detail: { message }, bubbles: true, composed: true }));
  }

  // Kamera bzw. Fotoauswahl öffnen. Das Feld liegt außerhalb des Renderings,
  // damit ein neuer Stand vom Server die Auswahl nicht abbricht.
  _pickPhoto(mode, data) {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = "image/*";
    input.capture = "environment";
    input.addEventListener("change", () => {
      const file = input.files?.[0];
      if (file) this._upload(mode, data, file);
    });
    input.click();
  }

  async _upload(mode, data, file) {
    if (this._busy) return;
    this._busy = true;
    this._notify(this._t("uploading"));
    const body = new FormData();
    body.append("chore_id", data.chore_id);
    body.append("mode", mode);
    if (data.member) body.append("member", data.member);
    body.append("file", file, file.name || "foto.jpg");
    try {
      const url = "/api/familienplan/photo";
      const resp = this._hass.fetchWithAuth
        ? await this._hass.fetchWithAuth(url, { method: "POST", body })
        : await fetch(url, {
            method: "POST",
            body,
            headers: { Authorization: `Bearer ${this._hass.auth.data.access_token}` },
          });
      if (!resp.ok) {
        let message = resp.statusText;
        try {
          message = (await resp.json()).message || message;
        } catch (_) {
          /* keine JSON-Antwort */
        }
        this._notify(message);
      }
    } catch (err) {
      this._notify(err.message);
    } finally {
      this._busy = false;
    }
  }

  // -- Bedienung -------------------------------------------------------------

  _onClick(ev) {
    const el = ev.target.closest("[data-action]");
    if (!el) return;
    const { action, id, member } = el.dataset;
    this._touchIdle();
    switch (action) {
      case "pick":
        this._actingAs = id;
        this._touchIdle();
        this._render();
        break;
      case "unpick":
        this._actingAs = null;
        clearTimeout(this._idleTimer);
        this._render();
        break;
      case "tab":
        this._tab = id;
        this._render();
        break;
      case "claim": {
        const chore = this._data.chores.find((c) => c.id === id);
        const data = { chore_id: id };
        if (member && (member !== this._data.me || this._data.tablet)) data.member = member;
        if (this._photoNeeded(chore)) this._pickPhoto("claim", data);
        else {
          this._call("claim_chore", data);
          if (!this._data.is_manager || this._data.tablet) this._celebrate(el);
        }
        break;
      }
      case "take": {
        const chore = this._data.chores.find((c) => c.id === id);
        const data = { chore_id: id };
        if (this._data.tablet) data.member = this._actingAs;
        if (this._photoNeeded(chore)) this._pickPhoto("take_over", data);
        else this._call("take_over_chore", data);
        break;
      }
      case "undo":
        this._call("undo_claim", { chore_id: id });
        break;
      case "approve":
        this._call("approve_chore", { chore_id: id });
        break;
      case "reject":
        this._call("reject_chore", { chore_id: id });
        break;
      case "delete": {
        const chore = this._data.chores.find((c) => c.id === id);
        if (chore && confirm(this._t("confirmDelete", { name: chore.name }))) {
          this._call("delete_chore", { chore_id: id });
        }
        break;
      }
      case "create":
        this._createChore();
        break;
      case "edit":
        this._startEdit(id);
        break;
      case "cancel-edit":
        this._resetForm();
        this._render();
        break;
      case "set-away": {
        const form = this._awayForm[id] || {};
        if (!form.until) return;
        const data = { member: id, until: form.until };
        if (form.substitute) data.substitute = form.substitute;
        this._call("set_absence", data).then(() => {
          delete this._awayForm[id];
        });
        break;
      }
      case "redeem": {
        const reward = this._data.rewards.find((r) => r.id === id);
        if (reward && confirm(this._t("confirmRedeem", { name: reward.name, n: reward.cost }))) {
          const data = { reward_id: id };
          if (this._data.tablet) data.member = this._actingAs;
          this._call("redeem_reward", data);
        }
        break;
      }
      case "give":
        this._call("approve_redemption", { redemption_id: id });
        break;
      case "refuse":
        this._call("reject_redemption", { redemption_id: id });
        break;
      case "reward-save":
        this._saveReward();
        break;
      case "reward-edit": {
        const r = this._data.rewards.find((x) => x.id === id);
        if (r) {
          this._rewardForm = { name: r.name, cost: r.cost, members: [...r.members], editId: r.id };
          this._render();
        }
        break;
      }
      case "reward-cancel":
        this._rewardForm = this._emptyReward();
        this._render();
        break;
      case "reward-delete": {
        const r = this._data.rewards.find((x) => x.id === id);
        if (r && confirm(this._t("confirmDelete", { name: r.name }))) {
          this._call("delete_reward", { reward_id: id });
        }
        break;
      }
      case "pass":
        this._call("grant_pass", { member: id });
        break;
      case "revoke-pass":
        this._call("revoke_pass", { member: id });
        break;
      case "end-away":
        this._call("end_absence", { member: id });
        break;
    }
  }

  _onInput(ev) {
    const el = ev.target;
    const field = el.dataset?.field;
    if (!field) return;
    if (field.startsWith("away.")) {
      const [, memberId, key] = field.split(".");
      this._awayForm[memberId] = { ...(this._awayForm[memberId] || {}), [key]: el.value };
      return;
    }
    if (field.startsWith("reward.")) {
      const key = field.slice(7);
      if (key === "member") {
        const set = new Set(this._rewardForm.members);
        el.checked ? set.add(el.value) : set.delete(el.value);
        this._rewardForm.members = [...set];
      } else {
        this._rewardForm[key] = el.value;
      }
      return;
    }
    if (field === "assignee") {
      const set = new Set(this._form.assignees);
      el.checked ? set.add(el.value) : set.delete(el.value);
      this._form.assignees = [...set];
    } else if (el.type === "checkbox") {
      this._form[field] = el.checked;
    } else {
      this._form[field] = el.value;
    }
  }

  _emptyReward() {
    return { name: "", cost: 20, members: [], editId: null };
  }

  async _saveReward() {
    const f = this._rewardForm;
    const cost = Number(f.cost);
    if (!f.name.trim() || !(cost >= 1)) return;
    const data = { name: f.name.trim(), cost, members: f.members };
    if (f.editId) await this._call("update_reward", { reward_id: f.editId, ...data });
    else await this._call("create_reward", data);
    this._rewardForm = this._emptyReward();
    this._render();
  }

  _emptyForm() {
    return { name: "", assignees: [], recurrence: "daily", due: "", points: 1, rotation: false, approval: false, photo: false, minAge: 0, editId: null };
  }

  _resetForm() {
    this._form = this._emptyForm();
  }

  _toLocalInput(iso) {
    if (!iso) return "";
    const d = new Date(iso);
    const pad = (n) => String(n).padStart(2, "0");
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
  }

  _startEdit(id) {
    const c = this._data.chores.find((x) => x.id === id);
    if (!c) return;
    this._form = {
      name: c.name,
      assignees: [...c.assignees],
      recurrence: c.recurrence,
      due: this._toLocalInput(c.due),
      points: c.points,
      rotation: c.rotation,
      approval: c.requires_approval,
      photo: c.requires_photo,
      minAge: c.min_age || 0,
      editId: c.id,
    };
    this._render();
    this.shadowRoot.querySelector("details.form")?.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  async _createChore() {
    const f = this._form;
    if (!f.name.trim() || !f.assignees.length) return;
    if (f.editId) {
      await this._call("update_chore", {
        chore_id: f.editId,
        name: f.name.trim(),
        assignees: f.assignees,
        points: Number(f.points) || 0,
        recurrence: f.recurrence,
        due: f.due || "",
        rotation: f.rotation,
        requires_approval: f.approval,
        requires_photo: f.photo,
        min_age: Number(f.minAge) || 0,
      });
      this._resetForm();
      this._render();
      return;
    }
    const data = {
      name: f.name.trim(),
      assignees: f.assignees,
      points: Number(f.points) || 0,
      recurrence: f.recurrence,
      rotation: f.rotation,
      requires_approval: f.approval,
      requires_photo: f.photo,
      min_age: Number(f.minAge) || 0,
    };
    if (f.due) data.due = f.due;
    await this._call("create_chore", data);
    this._form = { ...this._form, name: "" };
    this._render();
  }

  // -- Anzeige ---------------------------------------------------------------

  // Jedes Kind bekommt eine feste Farbe, damit man es überall wiedererkennt.
  _color(memberId) {
    const kids = this._children();
    const i = kids.findIndex((m) => m.id === memberId);
    return i < 0 ? "var(--secondary-text-color)" : PALETTE[i % PALETTE.length];
  }

  _avatar(member, size = 40) {
    const letter = esc((member?.name || "?").trim().charAt(0).toUpperCase());
    return `<span class="avatar" style="--kid:${this._color(member?.id)};width:${size}px;height:${size}px;font-size:${Math.round(size * 0.45)}px">${letter}</span>`;
  }

  _isToday(iso) {
    if (!iso) return false;
    const d = new Date(iso);
    const n = new Date();
    return d.getFullYear() === n.getFullYear() && d.getMonth() === n.getMonth() && d.getDate() === n.getDate();
  }

  // Heute erledigt / offen für den Fortschrittsring.
  _todayStats(memberId) {
    const open = this._openFor(memberId).length;
    const done = this._data.chores.filter(
      (c) => c.last_completed_by === memberId && this._isToday(c.last_completed_at) && !this._openFor(memberId).includes(c),
    ).length;
    return { done, open, total: done + open };
  }

  _ring(done, total, color, size = 64) {
    const r = size / 2 - 5;
    const len = 2 * Math.PI * r;
    const part = total ? done / total : 1;
    return `
      <svg class="ring" width="${size}" height="${size}" viewBox="0 0 ${size} ${size}" role="img" aria-label="${done}/${total}">
        <circle cx="${size / 2}" cy="${size / 2}" r="${r}" fill="none" stroke="var(--divider-color, #e0e0e0)" stroke-width="6"/>
        ${part > 0 ? `<circle cx="${size / 2}" cy="${size / 2}" r="${r}" fill="none" stroke="${color}" stroke-width="6" stroke-linecap="round"
          stroke-dasharray="${len * part} ${len}" transform="rotate(-90 ${size / 2} ${size / 2})"/>` : ""}
        <text x="50%" y="50%" text-anchor="middle" dominant-baseline="central" font-size="${Math.round(size * 0.26)}" font-weight="600" fill="var(--primary-text-color)">${
          total && done < total ? `${done}/${total}` : "✓"
        }</text>
      </svg>`;
  }

  _rewardEmoji(name) {
    const n = String(name).toLowerCase();
    for (const [words, emoji] of REWARD_EMOJI) if (words.some((w) => n.includes(w))) return emoji;
    return "🎁";
  }

  // Kleines Konfetti beim Abhaken. Liegt außerhalb des Kartentexts, damit
  // ein neuer Stand vom Server die Animation nicht abbricht.
  _celebrate(from) {
    const fx = this.shadowRoot.querySelector(".fx");
    if (!fx || window.matchMedia?.("(prefers-reduced-motion: reduce)").matches) return;
    const box = from.getBoundingClientRect();
    const host = this.getBoundingClientRect();
    const x = box.left - host.left + box.width / 2;
    const y = box.top - host.top + box.height / 2;
    for (let i = 0; i < 24; i++) {
      const bit = document.createElement("i");
      const angle = (Math.PI * 2 * i) / 24 + Math.random() * 0.3;
      const dist = 50 + Math.random() * 60;
      bit.style.cssText = `left:${x}px;top:${y}px;background:${PALETTE[i % PALETTE.length]};--dx:${Math.cos(angle) * dist}px;--dy:${Math.sin(angle) * dist - 30}px;--rot:${Math.random() * 360}deg`;
      fx.appendChild(bit);
    }
    const words = this._t("great");
    const toast = document.createElement("b");
    toast.textContent = words[Math.floor(Math.random() * words.length)];
    toast.style.cssText = `left:${x}px;top:${y - 30}px`;
    fx.appendChild(toast);
    setTimeout(() => fx.replaceChildren(), 1400);
  }

  _dueLabel(chore) {
    if (chore.state === "overdue") return `<span class="chip bad">${this._t("overdue")}</span>`;
    if (!chore.due) return `<span class="muted">${this._t("noDue")}</span>`;
    const due = new Date(chore.due);
    const now = new Date();
    const time = due.toLocaleTimeString(this._locale(), { hour: "2-digit", minute: "2-digit" });
    const day = (d) => new Date(d.getFullYear(), d.getMonth(), d.getDate()).getTime();
    const diff = Math.round((day(due) - day(now)) / 86400000);
    let label;
    if (diff === 0) label = this._t("today", { time });
    else if (diff === 1) label = this._t("tomorrow", { time });
    else label = due.toLocaleDateString(this._locale(), { weekday: "short", day: "numeric", month: "numeric" }) + " " + time;
    return `<span class="muted">${esc(label)}</span>`;
  }

  _choreRow(chore, memberId, { showClaim, forName } = {}) {
    const ro = this._config.readonly;
    let action = "";
    if (chore.state === "claimed") {
      const mine = chore.claimed_by === this._me();
      action = "";
      if (!ro && (mine || this._data.is_manager)) {
        action += `<button class="link" data-action="undo" data-id="${esc(chore.id)}">${this._t("undo")}</button>`;
      }
    } else if (showClaim && !ro) {
      const label = forName ? this._t("doneShort") : this._t("done");
      const photo = this._photoNeeded(chore);
      action = `<button class="primary" data-action="claim" data-id="${esc(chore.id)}" data-member="${esc(memberId)}">${
        photo ? this._t("photoDone") : "✓ " + label
      }</button>`;
    }
    return `
      <li class="row task ${chore.state}">
        ${chore.state === "claimed" ? this._thumb(chore) : ""}
        <div class="main">
          <div class="title">${esc(chore.name)}${this._photoIcon(chore)}</div>
          <div class="sub">${
            chore.state === "claimed" ? `<span class="chip wait">${this._t("waiting")}</span>` : this._dueLabel(chore)
          }${this._takenInfo(chore)}</div>
        </div>
        <span class="pts-pill">+${chore.points}</span>
        <div class="actions">${action}</div>
      </li>`;
  }

  // Ohne Pro (Testphase vorbei, kein Schlüssel) gibt es keinen Fotonachweis.
  _pro() {
    return this._data?.pro?.pro !== false;
  }

  _photoNeeded(chore) {
    return !!chore?.requires_photo && this._pro() && !this._data.is_manager;
  }

  _photoIcon(chore) {
    return chore.requires_photo && this._pro() ? ' <span class="muted">📷</span>' : "";
  }

  _proLine() {
    const p = this._data.pro;
    if (!p || p.licensed) return "";
    if (p.pro) return `<p class="muted small pro">${esc(this._t("trial", { n: p.trial_days_left }))}</p>`;
    return `<p class="muted small pro">${esc(this._t("free"))} · ${esc(this._t("proHint"))}</p>`;
  }

  _thumb(chore) {
    if (!chore.photo_url) return "";
    return `<a class="thumb" href="${esc(chore.photo_url)}" target="_blank" rel="noopener" title="${this._t("photoOf")}"><img src="${esc(chore.photo_url)}" alt="${this._t("photoOf")}" loading="lazy"></a>`;
  }

  _takenInfo(chore) {
    let text = "";
    if (chore.state === "claimed" && chore.claim_taken_from) {
      text += ` · ${esc(this._t("takenFrom", { name: this._member(chore.claim_taken_from)?.name || "?" }))}`;
    }
    if (chore.state === "claimed" && chore.claim_multiplier > 1) text += ` · <span class="chip">x${chore.claim_multiplier}</span>`;
    return text;
  }

  // Aufgaben der Geschwister, die heute noch offen sind und übernommen werden können.
  _takeable(memberId) {
    return this._data.chores.filter(
      (c) =>
        (c.state === "open" || c.state === "overdue") &&
        c.responsible.length &&
        !c.responsible.includes(memberId) &&
        c.due &&
        this._dueSoon(c),
    );
  }

  _renderTakeOver(member) {
    const t = this._data.takeover;
    if (!t?.allowed || !this._pro() || this._config.readonly || member.id !== this._me()) return "";
    const chores = this._takeable(member.id);
    if (!chores.length) return "";
    const rows = chores
      .map((c) => {
        const owner = c.responsible.map((id) => this._member(id)?.name).filter(Boolean).join(", ");
        const pts = c.points * (t.multiplier || 1);
        return `
        <li class="row task ${c.state}" style="border-left-color:${this._color(c.responsible[0])}">
          <div class="main">
            <div class="title">${esc(c.name)}${this._photoIcon(c)}</div>
            <div class="sub muted">${esc(owner)}</div>
          </div>
          <span class="pts-pill">+${pts}</span>
          <div class="actions"><button class="primary" data-action="take" data-id="${esc(c.id)}">${this._t("takeOver")}${
            t.multiplier > 1 ? " x" + t.multiplier : ""
          }</button></div>
        </li>`;
      })
      .join("");
    return `
      <section class="help">
        <div class="section-head"><strong>${this._t("helpOthers")}</strong>${
          t.multiplier > 1 ? `<span class="chip">${this._t("double")}</span>` : ""
        }</div>
        <p class="muted small">${this._t("helpHint")}</p>
        <ul class="tasks">${rows}</ul>
      </section>`;
  }

  _renderChildRewards(member) {
    const rewards = (this._data.rewards || []).filter((r) => !r.members.length || r.members.includes(member.id));
    const pending = (this._data.redemptions || []).filter((r) => r.member_id === member.id);
    if (!rewards.length && !pending.length) return "";
    const ro = this._config.readonly || member.id !== this._me();
    const waiting = pending
      .map(
        (r) => `
        <li class="row">
          <div class="main"><div class="title">🎁 ${esc(r.reward_name)}</div><div class="sub"><span class="chip wait">${this._t("waitingParents")}</span></div></div>
          <div class="actions">${ro ? "" : `<button class="link" data-action="refuse" data-id="${esc(r.id)}">${this._t("undo")}</button>`}</div>
        </li>`,
      )
      .join("");
    const rows = rewards
      .slice()
      .sort((a, b) => a.cost - b.cost)
      .map((r) => {
        const enough = member.points >= r.cost;
        const action = ro
          ? ""
          : enough
            ? `<button class="primary" data-action="redeem" data-id="${esc(r.id)}">${this._t("redeem")}</button>`
            : `<span class="muted small">${esc(this._t("missing", { n: r.cost - member.points }))}</span>`;
        const pct = Math.min(100, Math.round((member.points / r.cost) * 100));
        return `
        <div class="reward ${enough ? "ready" : ""}">
          <div class="reward-emoji">${this._rewardEmoji(r.name)}</div>
          <div class="reward-name">${esc(r.name)}</div>
          <div class="reward-cost">⭐ ${r.cost}</div>
          <div class="bar"><span style="width:${pct}%"></span></div>
          <div class="reward-action">${action}</div>
        </div>`;
      })
      .join("");
    return `
      <section class="help">
        <div class="section-title">🎁 ${this._t("rewards")}</div>
        ${waiting ? `<ul>${waiting}</ul>` : ""}
        <div class="rewards">${rows}</div>
      </section>`;
  }

  _renderRewardAdmin() {
    const f = this._rewardForm;
    const kids = this._children();
    const names = (ids) => (ids.length ? ids.map((id) => this._member(id)?.name).filter(Boolean).join(", ") : this._t("allChildren"));
    const rows = (this._data.rewards || [])
      .slice()
      .sort((a, b) => a.cost - b.cost)
      .map(
        (r) => `
        <li class="row">
          <div class="main"><div class="title">${esc(r.name)}</div><div class="sub muted">${r.cost} P · ${esc(names(r.members))}</div></div>
          <div class="actions">
            <button class="link" data-action="reward-edit" data-id="${esc(r.id)}">${this._t("edit")}</button>
            <button class="link bad" data-action="reward-delete" data-id="${esc(r.id)}">${this._t("delete")}</button>
          </div>
        </li>`,
      )
      .join("");
    return `
      <details class="form" ${(this._data.rewards || []).length && !f.editId ? "" : "open"}>
        <summary>${f.editId ? this._t("editReward") : "+ " + this._t("newReward")}</summary>
        <div class="grid">
          <label>${this._t("name")}<input data-field="reward.name" value="${esc(f.name)}" maxlength="60"></label>
          <label>${this._t("cost")}<input type="number" min="1" data-field="reward.cost" value="${esc(f.cost)}"></label>
        </div>
        <fieldset><legend>${this._t("forWhom")} <span class="muted">(${this._t("forWhomHint")})</span></legend>
          ${kids
            .map(
              (m) =>
                `<label class="check"><input type="checkbox" data-field="reward.member" value="${esc(m.id)}" ${f.members.includes(m.id) ? "checked" : ""}>${esc(m.name)}</label>`,
            )
            .join("")}
        </fieldset>
        <button class="primary" data-action="reward-save">${f.editId ? this._t("save") : this._t("create")}</button>
        ${f.editId ? `<button class="link" data-action="reward-cancel">${this._t("cancel")}</button>` : ""}
      </details>
      ${rows ? `<ul>${rows}</ul>` : `<p class="empty muted">${this._t("noRewards")}</p>`}`;
  }

  _openFor(memberId) {
    return this._data.chores.filter(
      (c) => c.responsible.includes(memberId) && c.state !== "done" && this._dueSoon(c),
    );
  }

  _dueSoon(chore) {
    if (!chore.due || chore.state === "overdue" || chore.state === "claimed") return true;
    const end = new Date();
    end.setHours(23, 59, 59, 999);
    return new Date(chore.due) <= end;
  }

  _renderTablet() {
    const kid = this._actingAs && this._member(this._actingAs);
    if (kid) {
      return `
        <button class="link back" data-action="unpick">← ${this._t("finished")}</button>
        ${this._renderChild(kid)}`;
    }
    const tiles = this._children()
      .map((m) => {
        const open = this._openFor(m.id).filter((c) => c.state !== "claimed").length;
        return `
          <button class="tile" style="--kid:${this._color(m.id)}" data-action="pick" data-id="${esc(m.id)}">
            <span class="tile-avatar">${esc(m.name.trim().charAt(0).toUpperCase())}</span>
            <span class="tile-name">${esc(m.name)}</span>
            <span class="tile-sub">${open ? esc(this._t("openCount", { n: open })) : "✓"} · ⭐ ${m.points}</span>
          </button>`;
      })
      .join("");
    return `<div class="hello center">${this._t("whoAreYou")}</div><div class="tiles">${tiles}</div>`;
  }

  _renderChild(member) {
    const chores = this._openFor(member.id);
    const color = this._color(member.id);
    const { done, open, total } = this._todayStats(member.id);
    const left = chores.filter((c) => c.state !== "claimed").length;
    const line = !left ? this._t("allDoneToday") : left === 1 ? this._t("leftOne") : this._t("leftToday", { n: left });
    const list = chores.length
      ? `<ul class="tasks">${chores.map((c) => this._choreRow(c, member.id, { showClaim: c.state !== "claimed" })).join("")}</ul>`
      : `<div class="done-big">🎉<div>${this._t("allDone")}</div></div>`;
    return `
      <div class="kid" style="--kid:${color}">
        <div class="hero">
          ${this._avatar(member, 56)}
          <div class="hero-text">
            <div class="hello">${esc(this._t("hello", { name: member.name }))} 👋</div>
            <div class="muted">${esc(line)}</div>
            <div class="star">⭐ ${esc(this._t("points", { n: member.points }))}</div>
          </div>
          ${this._ring(done, total || open, color, 72)}
        </div>
        ${member.locked ? `<p class="chip bad">${this._t("locked")}</p>` : ""}
        <div class="section-title">${this._t("todayTitle")}</div>
        ${list}
        ${this._renderTakeOver(member)}
        ${this._renderChildRewards(member)}
      </div>`;
  }

  _renderParent() {
    const d = this._data;
    const waiting = d.chores.filter((c) => c.state === "claimed");
    const open = waiting.length + (d.redemptions || []).length;
    const tabs = [
      ["today", this._t("tabToday")],
      ["approve", `${this._t("tabApprove")}${open ? ` <span class="count">${open}</span>` : ""}`],
      ["chores", this._t("tabChores")],
      ["rewards", this._t("tabRewards")],
      ["away", this._t("tabAway")],
    ];
    let body = "";
    if (this._tab === "approve") body = this._renderApprovals(waiting);
    else if (this._tab === "chores") body = this._renderChores();
    else if (this._tab === "rewards") body = this._renderRewardAdmin();
    else if (this._tab === "away") body = this._renderAway();
    else body = this._renderToday();
    return `
      <nav class="tabs">${tabs
        .map(([id, label]) => `<button class="tab ${this._tab === id ? "on" : ""}" data-action="tab" data-id="${id}">${label}</button>`)
        .join("")}</nav>
      ${body}
      ${this._proLine()}`;
  }

  _children() {
    return this._data.members.filter((m) => m.role === "child");
  }

  _renderToday() {
    return `<div class="kidgrid">${this._renderTodayCards()}</div>`;
  }

  _renderTodayCards() {
    return this._children()
      .map((m) => {
        const chores = this._openFor(m.id);
        let status = m.away ? `<span class="chip">${esc(this._awayText(m))}</span>` : "";
        if (m.locked) status += ` <span class="chip bad">${this._t("locked")}</span>`;
        if (m.pass_until) {
          const time = new Date(m.pass_until).toLocaleTimeString(this._locale(), { hour: "2-digit", minute: "2-digit" });
          status += ` <span class="chip">${esc(this._t("pass", { time }))}</span>`;
        }
        let passBtn = "";
        if (m.has_devices && this._pro() && !this._config.readonly) {
          passBtn = m.pass_until
            ? `<button class="link" data-action="revoke-pass" data-id="${esc(m.id)}">${this._t("takePass")}</button>`
            : `<button class="link" data-action="pass" data-id="${esc(m.id)}">${this._t("givePass")}</button>`;
        }
        const list = chores.length
          ? `<ul>${chores.map((c) => this._choreRow(c, m.id, { showClaim: c.state !== "claimed", forName: m.name })).join("")}</ul>`
          : `<p class="empty small">${this._t("allDone")}</p>`;
        const { done, open, total } = this._todayStats(m.id);
        return `
          <section class="kidcard" style="--kid:${this._color(m.id)}">
            <div class="kidcard-head">
              ${this._avatar(m, 40)}
              <div class="kidcard-name"><strong>${esc(m.name)}</strong><span class="muted small">⭐ ${m.points}</span></div>
              ${this._ring(done, total || open, this._color(m.id), 44)}
            </div>
            ${status || passBtn ? `<div class="kidcard-status">${status}${passBtn}</div>` : ""}
            ${list}
          </section>`;
      })
      .join("");
  }

  _renderApprovals(waiting) {
    const redemptions = this._data.redemptions || [];
    if (!waiting.length && !redemptions.length) return `<p class="empty">${this._t("nothingToApprove")}</p>`;
    const gifts = redemptions
      .map(
        (r) => `
        <li class="row">
          <span class="gift">${this._rewardEmoji(r.reward_name)}</span>
          <div class="main">
            <div class="title">${esc(r.reward_name)}</div>
            <div class="sub muted">${esc(this._member(r.member_id)?.name)} ${this._t("wantsReward")} · ${r.cost} P</div>
          </div>
          <div class="actions">
            <button class="primary" data-action="give" data-id="${esc(r.id)}">✓ ${this._t("give")}</button>
            <button class="link bad" data-action="refuse" data-id="${esc(r.id)}">${this._t("refuse")}</button>
          </div>
        </li>`,
      )
      .join("");
    return `<ul>${gifts}${waiting
      .map(
        (c) => `
        <li class="row">
          ${this._thumb(c) || this._avatar(this._member(c.claimed_by), 36)}
          <div class="main">
            <div class="title">${esc(c.name)}</div>
            <div class="sub muted">${esc(this._member(c.claimed_by)?.name)} · ${c.points * (c.claim_multiplier || 1)} P${this._takenInfo(c)}</div>
          </div>
          <div class="actions">
            <button class="primary" data-action="approve" data-id="${esc(c.id)}">✓ ${this._t("approve")}</button>
            <button class="link bad" data-action="reject" data-id="${esc(c.id)}">${this._t("reject")}</button>
          </div>
        </li>`,
      )
      .join("")}</ul>`;
  }

  _renderChores() {
    const f = this._form;
    const names = (ids) => ids.map((id) => this._member(id)?.name).filter(Boolean).join(", ");
    const rows = this._data.chores
      .slice()
      .sort((a, b) => a.name.localeCompare(b.name))
      .map(
        (c) => `
        <li class="row">
          <div class="main">
            <div class="title">${esc(c.name)}</div>
            <div class="sub muted">${esc(names(c.assignees))} · ${esc(this._t("rec")[c.recurrence])}${c.rotation ? " · " + this._t("rotation") : ""}${
              c.requires_approval ? " · " + this._t("approval") : ""
            }${c.requires_photo && this._pro() ? " · 📷" : ""}${c.min_age ? " · " + esc(this._t("fromAge", { n: c.min_age })) : ""}${c.assignees.length && !c.responsible.length ? ` · <span class="chip">${this._t("paused")}</span>` : ""}</div>
          </div>
          <div class="actions">
            ${c.photo_url ? `<a class="link" href="${esc(c.photo_url)}" target="_blank" rel="noopener">📷 ${this._t("lastPhoto")}</a>` : ""}
            <button class="link" data-action="edit" data-id="${esc(c.id)}">${this._t("edit")}</button>
            <button class="link bad" data-action="delete" data-id="${esc(c.id)}">${this._t("delete")}</button>
          </div>
        </li>`,
      )
      .join("");
    const rec = this._t("rec");
    return `
      <details class="form" ${this._data.chores.length && !f.editId ? "" : "open"}>
        <summary>${f.editId ? this._t("editChore") : "+ " + this._t("newChore")}</summary>
        <label>${this._t("name")}<input data-field="name" value="${esc(f.name)}" maxlength="60"></label>
        <fieldset><legend>${this._t("assignees")}</legend>
          ${this._data.members
            .map(
              (m) =>
                `<label class="check"><input type="checkbox" data-field="assignee" value="${esc(m.id)}" ${f.assignees.includes(m.id) ? "checked" : ""}>${esc(m.name)}${
                  m.age != null ? ` <span class="muted">(${esc(this._t("years", { n: m.age }))})</span>` : ""
                }</label>`,
            )
            .join("")}
        </fieldset>
        <div class="grid">
          <label>${this._t("recurrence")}<select data-field="recurrence">${Object.entries(rec)
            .map(([k, v]) => `<option value="${k}" ${f.recurrence === k ? "selected" : ""}>${esc(v)}</option>`)
            .join("")}</select></label>
          <label>${this._t("due")}<input type="datetime-local" data-field="due" value="${esc(f.due)}"></label>
          <label>${this._t("pointsLabel")}<input type="number" min="0" max="100" data-field="points" value="${esc(f.points)}"></label>
          <label>${this._t("minAge")}<input type="number" min="0" max="18" data-field="minAge" value="${esc(f.minAge)}"></label>
        </div>
        <label class="check"><input type="checkbox" data-field="rotation" ${f.rotation ? "checked" : ""}>${this._t("rotation")}</label>
        <label class="check"><input type="checkbox" data-field="approval" ${f.approval ? "checked" : ""}>${this._t("approval")}</label>
        <label class="check"><input type="checkbox" data-field="photo" ${f.photo ? "checked" : ""} ${this._pro() ? "" : "disabled"}>${this._t("photo")}${
          this._pro() ? "" : ` <span class="chip">${this._t("proOnly")}</span>`
        }</label>
        <button class="primary" data-action="create">${f.editId ? this._t("save") : this._t("create")}</button>
        ${f.editId ? `<button class="link" data-action="cancel-edit">${this._t("cancel")}</button>` : ""}
      </details>
      <ul>${rows}</ul>`;
  }

  _awayText(m) {
    const fmt = (iso) => new Date(iso).toLocaleDateString(this._locale(), { day: "numeric", month: "numeric" });
    if (m.away) return this._t("away", { date: fmt(m.away_until) });
    if (m.away_until) return this._t("awayPlanned", { from: fmt(m.away_from), date: fmt(m.away_until) });
    return this._t("present");
  }

  _renderAway() {
    if (!this._pro()) return `<p class="empty muted">${esc(this._t("awayPro"))}</p>${this._proLine()}`;
    return `<ul>${this._children()
      .map((m) => {
        const form = this._awayForm[m.id] || {};
        const others = this._data.members.filter((o) => o.id !== m.id);
        const controls = m.away_until
          ? `<button class="link" data-action="end-away" data-id="${esc(m.id)}">${this._t("endAway")}</button>`
          : `
            <span class="muted">${this._t("until")}</span>
            <input type="datetime-local" aria-label="${this._t("until")}" data-field="away.${esc(m.id)}.until" value="${esc(form.until || "")}">
            <select aria-label="${this._t("substitute")}" data-field="away.${esc(m.id)}.substitute">
              <option value="">${this._t("substitute")}: ${this._t("none")}</option>
              ${others.map((o) => `<option value="${esc(o.id)}" ${form.substitute === o.id ? "selected" : ""}>${esc(o.name)}</option>`).join("")}
            </select>
            <button class="primary" data-action="set-away" data-id="${esc(m.id)}">${this._t("setAway")}</button>`;
        return `
          <li class="row wrap">
            <div class="main"><div class="title">${esc(m.name)}</div><div class="sub muted">${esc(this._awayText(m))}</div></div>
            <div class="actions">${controls}</div>
          </li>`;
      })
      .join("")}</ul>`;
  }

  _render() {
    if (!this._config) return;
    let body;
    if (this._error) body = `<p class="empty">${esc(this._error)}</p>`;
    else if (!this._data) body = `<p class="empty muted">…</p>`;
    else {
      const forced = this._config.member ? this._memberByConfig() : null;
      const me = this._member(this._data.me);
      const mode = this._config.mode;
      if (forced) body = this._renderChild(forced);
      else if (this._data.tablet && !this._data.is_manager) body = this._renderTablet();
      else if (mode === "eltern" || (mode === "auto" && this._data.is_manager && (!me || me.role === "parent")))
        body = this._renderParent();
      else if (me) body = this._renderChild(me);
      else body = `<p class="empty">${this._t("noMember")}</p>`;
    }
    if (!this._cardEl) {
      this.shadowRoot.innerHTML = `<style>${STYLE}</style><ha-card></ha-card><div class="fx" aria-hidden="true"></div>`;
      this._cardEl = this.shadowRoot.querySelector("ha-card");
    }
    this._cardEl.innerHTML = `${this._config.title ? `<h1>${esc(this._config.title)}</h1>` : ""}<div class="content">${body}</div>`;
  }
}

// Kräftige Farben, die auf hell und dunkel funktionieren (weiße Schrift darauf).
const PALETTE = ["#4f7cff", "#ff7a45", "#22a565", "#a259ff", "#e5a100", "#f0508c", "#13a8b8"];

const REWARD_EMOJI = [
  [["film", "kino", "movie"], "🎬"],
  [["bildschirm", "zocken", "konsole", "screen", "game", "spiel"], "🎮"],
  [["essen", "pizza", "dinner", "eis", "süß"], "🍕"],
  [["ausflug", "trip", "zoo", "park"], "🎡"],
  [["taschengeld", "geld", "euro", "pocket", "money"], "💶"],
  [["aufbleiben", "bett", "bedtime", "länger"], "🌙"],
  [["freund", "übernacht", "friend", "sleepover"], "🧑‍🤝‍🧑"],
  [["buch", "book"], "📚"],
];

const STYLE = `
  :host { display: block; }
  ha-card { padding: 12px 16px 16px; }
  h1 { font-size: 1.2em; margin: 4px 0 8px; font-weight: 500; }
  ul { list-style: none; margin: 0; padding: 0; }
  .row { display: flex; align-items: center; gap: 12px; padding: 10px 0; border-bottom: 1px solid var(--divider-color, #e0e0e0); }
  .row:last-child { border-bottom: none; }
  .row.wrap { flex-wrap: wrap; }
  .row.overdue .title { color: var(--error-color, #db4437); }
  .main { flex: 1; min-width: 0; }
  .title { font-weight: 500; overflow-wrap: anywhere; }
  .sub { font-size: 0.85em; margin-top: 2px; }
  .muted { color: var(--secondary-text-color); }
  .pts { color: var(--secondary-text-color); }
  .actions { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; justify-content: flex-end; }
  button { font: inherit; cursor: pointer; border-radius: 18px; border: none; min-height: 36px; padding: 0 14px; }
  button.primary { background: var(--primary-color); color: var(--text-primary-color, #fff); }
  button.link { background: none; color: var(--primary-color); padding: 0 8px; }
  button.bad, .bad { color: var(--error-color, #db4437); }
  .chip { display: inline-block; font-size: 0.8em; padding: 2px 8px; border-radius: 10px; background: var(--secondary-background-color); }
  .chip.bad { background: none; border: 1px solid var(--error-color, #db4437); }
  .chip.wait { color: var(--warning-color, #f4b400); }
  .head, .section-head { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; margin: 8px 0 4px; }
  .hello { font-size: 1.3em; font-weight: 500; flex: 1; }
  .section-head strong { flex: 0 0 auto; }
  .badge { margin-left: auto; font-size: 0.85em; padding: 2px 10px; border-radius: 12px; background: var(--primary-color); color: var(--text-primary-color, #fff); white-space: nowrap; }
  section + section { margin-top: 12px; }
  .empty { text-align: center; padding: 16px 0; margin: 0; }
  .thumb { flex: 0 0 auto; }
  a.link { color: var(--primary-color); text-decoration: none; padding: 0 8px; white-space: nowrap; }
  .thumb img { width: 56px; height: 56px; object-fit: cover; border-radius: 8px; display: block; }
  p.small { font-size: 0.85em; margin: 0 0 4px; }
  p.pro { margin-top: 12px; text-align: center; }
  .tiles { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 12px; margin-top: 12px; }
  button.tile { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 6px; min-height: 110px; border-radius: 16px; background: var(--primary-color); color: var(--text-primary-color, #fff); }
  .tile-name { font-size: 1.5em; font-weight: 500; }
  .tile-sub { font-size: 0.9em; opacity: 0.9; }
  button.back { margin: 0 0 4px -8px; }
  section.help { margin-top: 16px; padding-top: 8px; border-top: 2px solid var(--divider-color, #e0e0e0); }
  .bar { height: 6px; border-radius: 3px; background: var(--divider-color, #e0e0e0); margin-top: 6px; overflow: hidden; max-width: 220px; }
  .bar span { display: block; height: 100%; background: var(--success-color, #43a047); }
  .muted.small, span.small { font-size: 0.85em; }
  .empty.small { padding: 4px 0; text-align: left; color: var(--secondary-text-color); }
  .tabs { display: flex; gap: 4px; overflow-x: auto; margin-bottom: 8px; }
  .tab { background: none; color: var(--primary-text-color); white-space: nowrap; }
  .tab.on { background: var(--secondary-background-color); font-weight: 500; }
  .count { display: inline-block; min-width: 18px; border-radius: 9px; background: var(--error-color, #db4437); color: #fff; font-size: 0.8em; }
  .form { margin: 4px 0 12px; padding: 8px 12px; border-radius: 12px; background: var(--secondary-background-color); }
  .form summary { cursor: pointer; font-weight: 500; padding: 4px 0; }
  .form label { display: flex; flex-direction: column; gap: 4px; margin: 8px 0; font-size: 0.9em; }
  .form label.check, label.check { flex-direction: row; align-items: center; gap: 8px; margin: 4px 12px 4px 0; display: inline-flex; }
  fieldset { border: none; padding: 0; margin: 8px 0; }
  legend { font-size: 0.9em; margin-bottom: 4px; }
  .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 0 12px; }
  input, select { font: inherit; padding: 8px; border-radius: 8px; border: 1px solid var(--divider-color, #ccc); background: var(--card-background-color); color: var(--primary-text-color); min-width: 0; }
  /* -- Gestaltung 0.13 -- */
  ha-card { overflow: hidden; color: var(--primary-text-color); }
  .kidcard-status button.link { padding: 0 4px; min-height: 28px; }
  .tabs { background: var(--secondary-background-color); border-radius: 22px; padding: 4px; margin-bottom: 12px; }
  .tab { border-radius: 18px; flex: 1 0 auto; }
  .tab.on { background: var(--card-background-color); box-shadow: 0 1px 3px rgba(0,0,0,.15); }
  .avatar { display: inline-flex; align-items: center; justify-content: center; flex: 0 0 auto; border-radius: 50%;
            background: var(--kid); color: #fff; font-weight: 700; box-shadow: 0 2px 6px rgba(0,0,0,.15); }
  .ring { flex: 0 0 auto; }
  .ring circle:last-of-type { transition: stroke-dasharray .6s ease; }
  .kid button.primary { background: var(--kid); }
  .hero { display: flex; align-items: center; gap: 14px; padding: 14px; margin: 0 0 8px; border-radius: 18px;
          background: linear-gradient(135deg, color-mix(in srgb, var(--kid) 22%, transparent), color-mix(in srgb, var(--kid) 6%, transparent)); }
  .hero-text { flex: 1; min-width: 0; }
  .hero .hello { font-size: 1.4em; font-weight: 600; }
  .star { display: inline-block; margin-top: 6px; padding: 3px 10px; border-radius: 12px; background: var(--card-background-color); font-weight: 600; font-size: 0.9em; }
  .section-title { font-weight: 600; font-size: 1.05em; margin: 14px 0 6px; }
  ul.tasks { display: flex; flex-direction: column; gap: 8px; }
  ul.tasks .row.task { border: none; border-radius: 14px; padding: 12px 12px 12px 14px; background: var(--secondary-background-color);
                       border-left: 5px solid var(--kid); }
  ul.tasks .row.task.overdue { border-left-color: var(--error-color, #db4437); }
  ul.tasks .row.task.claimed { opacity: .75; }
  ul.tasks button.primary { min-height: 44px; padding: 0 18px; font-weight: 600; }
  .pts-pill { flex: 0 0 auto; font-size: 0.8em; font-weight: 600; padding: 2px 8px; border-radius: 10px;
              background: color-mix(in srgb, var(--kid, var(--primary-color)) 18%, transparent); }
  .done-big { text-align: center; font-size: 2.6em; padding: 18px 0 8px; }
  .done-big div { font-size: 0.42em; font-weight: 600; margin-top: 4px; }
  section.help { border-top: none; padding-top: 0; }
  .rewards { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 10px; }
  .reward { display: flex; flex-direction: column; align-items: center; text-align: center; gap: 4px; padding: 12px 10px;
            border-radius: 16px; background: var(--secondary-background-color); }
  .reward.ready { box-shadow: inset 0 0 0 2px var(--kid, var(--primary-color)); }
  .reward-emoji { font-size: 2em; }
  .reward-name { font-weight: 600; font-size: 0.92em; overflow-wrap: anywhere; }
  .reward-cost { font-size: 0.85em; color: var(--secondary-text-color); }
  .reward .bar { width: 100%; max-width: none; }
  .reward .bar span, .kid .bar span { background: var(--kid, var(--success-color, #43a047)); }
  .reward-action { min-height: 36px; display: flex; align-items: center; }
  .kidgrid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 12px; }
  section.kidcard { margin: 0; padding: 12px 14px; border-radius: 16px; background: var(--secondary-background-color);
                    border-top: 4px solid var(--kid); }
  .kidcard-head { display: flex; align-items: center; gap: 10px; }
  .kidcard-name { flex: 1; display: flex; flex-direction: column; }
  .kidcard-status { display: flex; flex-wrap: wrap; align-items: center; gap: 6px; margin-top: 6px; }
  .kidcard .row { border-bottom-color: var(--divider-color, #e0e0e0); }
  .kidcard button.primary { background: var(--kid); }
  .gift { font-size: 1.8em; width: 36px; text-align: center; }
  .hello.center { text-align: center; font-size: 1.6em; font-weight: 600; margin: 8px 0; }
  button.tile { background: var(--kid); min-height: 150px; box-shadow: 0 4px 12px rgba(0,0,0,.15); transition: transform .1s; }
  button.tile:active { transform: scale(.97); }
  .tile-avatar { width: 56px; height: 56px; border-radius: 50%; background: rgba(255,255,255,.25); display: flex;
                 align-items: center; justify-content: center; font-size: 1.6em; font-weight: 700; }
  .fx { position: absolute; inset: 0; pointer-events: none; overflow: visible; }
  :host { position: relative; }
  .fx i { position: absolute; width: 8px; height: 12px; border-radius: 2px; animation: pop 1.1s ease-out forwards; }
  .fx b { position: absolute; transform: translate(-50%, 0); font-size: 1.3em; color: var(--primary-text-color);
          text-shadow: 0 1px 4px var(--card-background-color); animation: rise 1.2s ease-out forwards; white-space: nowrap; }
  @keyframes pop { from { transform: translate(0,0) rotate(0); opacity: 1; }
                   to { transform: translate(var(--dx), calc(var(--dy) + 60px)) rotate(var(--rot)); opacity: 0; } }
  @keyframes rise { from { opacity: 0; transform: translate(-50%, 0) scale(.6); } 30% { opacity: 1; transform: translate(-50%, -12px) scale(1.1); }
                    to { opacity: 0; transform: translate(-50%, -40px) scale(1); } }
  @media (max-width: 420px) { .row { flex-wrap: wrap; } .actions { width: 100%; justify-content: flex-start; }
    ul.tasks .actions { width: auto; } .hero { padding: 12px; } .hero .hello { font-size: 1.2em; } }
`;

// Eigene Seite in der Seitenleiste („Familienplan“). Zeigt die Karte groß,
// damit niemand erst ein Dashboard einrichten muss.
class FamilienplanPanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._narrow = false;
  }

  set hass(hass) {
    this._hass = hass;
    if (!this._card) this._build();
    this._card.hass = hass;
    const menu = this.shadowRoot.querySelector("ha-menu-button");
    if (menu) menu.hass = hass;
  }

  set narrow(narrow) {
    this._narrow = narrow;
    const menu = this.shadowRoot.querySelector("ha-menu-button");
    if (menu) menu.narrow = narrow;
  }

  _build() {
    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; min-height: 100vh; background: var(--primary-background-color); }
        .bar { display: flex; align-items: center; gap: 8px; height: var(--header-height, 56px); padding: 0 12px;
               background: var(--app-header-background-color, var(--primary-color)); color: var(--app-header-text-color, #fff); }
        .bar h1 { font-size: 20px; font-weight: 400; margin: 0; }
        .wrap { max-width: 720px; margin: 0 auto; padding: 16px; box-sizing: border-box; }
        @media (max-width: 600px) { .wrap { padding: 8px; } }
      </style>
      <div class="bar"><ha-menu-button></ha-menu-button><h1>Familienplan</h1></div>
      <div class="wrap"></div>`;
    const menu = this.shadowRoot.querySelector("ha-menu-button");
    menu.hass = this._hass;
    menu.narrow = this._narrow;
    this._card = document.createElement("familienplan-card");
    this._card.setConfig({ mode: "auto" });
    this.shadowRoot.querySelector(".wrap").appendChild(this._card);
  }
}

if (!customElements.get("familienplan-panel")) {
  customElements.define("familienplan-panel", FamilienplanPanel);
}

if (!customElements.get("familienplan-card")) {
  customElements.define("familienplan-card", FamilienplanCard);
  window.customCards = window.customCards || [];
  window.customCards.push({
    type: "familienplan-card",
    name: "Familienplan",
    description: "Aufgaben der Familie: Kinder melden, Eltern geben frei.",
  });
  console.info(`%c FAMILIENPLAN-CARD %c ${VERSION} `, "background:#3f51b5;color:#fff", "");
}
