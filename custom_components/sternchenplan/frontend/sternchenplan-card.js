/*
 * Sternchenplan-Karte für das Home-Assistant-Dashboard.
 *
 *   type: custom:sternchenplan-card
 *   mode: auto        # auto | kind | eltern  (auto: Eltern sehen die Eltern-Ansicht)
 *   member: Lucas     # optional: immer dieses Kind zeigen (z. B. Tablet im Kinderzimmer)
 *   readonly: false   # true: nur anzeigen, keine Knöpfe (z. B. Küchen-Tablet)
 *
 * Daten kommen per Websocket (sternchenplan/subscribe), Änderungen laufen über
 * die Dienste. Home Assistant prüft dort, wer was darf.
 */

const VERSION = "0.19.0";

const T = {
  de: {
    hello: "Hallo {name}",
    points: "{n} Sterne",
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
    notSetUp: "Sternchenplan ist nicht eingerichtet.",
    noMember: "Dieses Konto gehört zu keinem Familienmitglied.",
    paused: "ruht",
    locked: "🔒 Internet gesperrt",
    pass: "Freikarte bis {time}",
    givePass: "Freikarte",
    takePass: "Freikarte weg",
    pointsLabel: "Sterne",
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
    missing: "noch {n} Sterne",
    confirmRedeem: "„{name}“ für {n} Sterne einlösen?",
    waitingParents: "Wartet auf die Eltern",
    wantsReward: "möchte einlösen",
    give: "Bekommt es",
    refuse: "Ablehnen",
    newReward: "Neue Belohnung",
    editReward: "Belohnung bearbeiten",
    forWhom: "Für wen",
    allChildren: "alle Kinder",
    forWhomHint: "nichts angehakt = alle Kinder",
    cost: "Sterne",
    noRewards: "Noch keine Belohnungen. Lege oben die erste an.",
    uploading: "Foto wird hochgeladen …",
    helpOthers: "Geschwistern helfen",
    helpHint: "Übernimm eine Aufgabe und hol dir die Sterne.",
    takeOver: "Übernehmen",
    takenFrom: "übernommen für {name}",
    double: "doppelte Sterne",
    donate: "Sternchenplan ist kostenlos. Gefällt er euch? ☕ Trinkgeld geben",
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
    level: "Level {n}",
    levelTitles: ["Starter", "Helfer", "Macher", "Profi", "Experte", "Meister", "Champion", "Held", "Superheld", "Legende"],
    toNext: "noch {n} ⭐ bis Level {next}",
    streakDays: "{n} Tage in Folge",
    streakOne: "1 Tag",
    streakKeep: "Heute etwas erledigen, dann wächst deine Serie!",
    streakStart: "Erledige heute etwas und starte eine Serie",
    streakDone: "Serie für heute gesichert",
    best: "Rekord {n}",
    badges: "Abzeichen",
    badgeNames: {
      first: "Erster Stern", done10: "Fleißige Biene", done50: "Arbeitstier", done100: "Haushaltsheld",
      done250: "Königlich", streak3: "Am Ball", streak7: "Eine ganze Woche", streak30: "Unaufhaltsam",
      helper1: "Retter in der Not", helper10: "Superhelfer", early5: "Frühaufsteher", photo10: "Fotoprofi",
      reward1: "Erste Belohnung", stars100: "100 Sterne", stars500: "500 Sterne",
    },
    badgeHow: {
      done: "{n} Aufgaben erledigen", best_streak: "{n} Tage in Folge etwas erledigen",
      taken_over: "{n}× Geschwistern helfen", early: "{n} Aufgaben vor 9 Uhr",
      photos: "{n} Aufgaben mit Foto", redeemed: "{n} Belohnung einlösen", earned: "{n} Sterne sammeln",
    },
    badgeEarned: "geschafft am {date}",
    newBadge: "Neues Abzeichen!",
    levelUp: "Level {n}!",
    youAre: "Du bist jetzt {title}",
    tapClose: "Tippen zum Weitermachen",
    goal: "Mein Sparziel",
    goalMissing: "noch {n} Sterne",
    goalReady: "Geschafft! Du kannst es einlösen.",
    setGoal: "🎯 Als Ziel",
    isGoal: "🎯 Mein Ziel",
    familyGoal: "Familienziel",
    together: "{n} von {t} ⭐, alle zusammen",
    familyReached: "Geschafft! 🎉",
    fgName: "Wofür spart ihr gemeinsam?",
    fgTarget: "Sterne zusammen",
    fgStart: "Familienziel starten",
    fgClear: "Familienziel beenden",
    fgHint: "Alle Kinder sammeln gemeinsam. Niemandem wird etwas abgezogen.",
    fgConfirm: "Familienziel „{name}“ beenden?",
    tabMoney: "Geld",
    money: "Taschengeld",
    weekly: "{amount} Wochengeld, jeden {day}",
    exchange: "{stars} ⭐ → 1 € tauschen",
    confirmExchange: "{stars} Sterne gegen 1 € tauschen?",
    rate: "Sterne pro Euro",
    rateHint: "0 = Sterne lassen sich nicht in Geld tauschen",
    payday: "Zahltag fürs Wochengeld",
    perWeek: "€ pro Woche",
    payout: "Auszahlen",
    confirmPayout: "{amount} an {name} auszahlen? Gib das Geld bar oder überweise es.",
    book: "Buchen",
    bookPrompt: "Betrag in Euro (minus zieht ab), z. B. 2,50",
    notePrompt: "Wofür? (optional)",
    history: "Verlauf",
    noHistory: "Noch keine Buchungen.",
    kinds: { allowance: "Wochengeld", exchange: "Sterne getauscht", payout: "ausgezahlt", adjust: "gebucht" },
    days: ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"],
    steps: "Schritte (einer pro Zeile, leer = normale Aufgabe)",
    stepsShort: "{n} Schritte",
    templates: "📚 Vorlagen",
    templatesHint: "Tippe auf eine Vorlage, dann wähle unten, wer sie machen soll.",
    ageAll: "Alle",
    ageGroup: "{from}–{to} J.",
    ageFrom: "ab {n} J.",
    moneyHint: "Das Geld liegt nicht wirklich hier. Sternchenplan führt nur das Konto. Auszahlen tut ihr selbst, bar oder per Überweisung.",
  },
  en: {
    hello: "Hi {name}",
    points: "{n} stars",
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
    notSetUp: "Sternchenplan is not set up.",
    noMember: "This account is not linked to a family member.",
    paused: "paused",
    locked: "🔒 Internet locked",
    pass: "Free pass until {time}",
    givePass: "Free pass",
    takePass: "Remove pass",
    pointsLabel: "Stars",
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
    missing: "{n} stars to go",
    confirmRedeem: "Redeem “{name}” for {n} stars?",
    waitingParents: "Waiting for a parent",
    wantsReward: "wants to redeem",
    give: "Give it",
    refuse: "Reject",
    newReward: "New reward",
    editReward: "Edit reward",
    forWhom: "For whom",
    allChildren: "all children",
    forWhomHint: "none ticked = all children",
    cost: "Stars",
    noRewards: "No rewards yet. Create the first one above.",
    uploading: "Uploading photo …",
    helpOthers: "Help your siblings",
    helpHint: "Take over a chore and earn the stars.",
    takeOver: "Take over",
    takenFrom: "taken over for {name}",
    double: "double stars",
    donate: "Sternchenplan is free. Like it? ☕ Leave a tip",
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
    level: "Level {n}",
    levelTitles: ["Starter", "Helper", "Doer", "Pro", "Expert", "Master", "Champion", "Hero", "Superhero", "Legend"],
    toNext: "{n} ⭐ to level {next}",
    streakDays: "{n} days in a row",
    streakOne: "1 day",
    streakKeep: "Do something today to keep your streak!",
    streakStart: "Do something today to start a streak",
    streakDone: "Streak saved for today",
    best: "Best {n}",
    badges: "Badges",
    badgeNames: {
      first: "First star", done10: "Busy bee", done50: "Workhorse", done100: "Household hero",
      done250: "Royal", streak3: "On a roll", streak7: "A whole week", streak30: "Unstoppable",
      helper1: "Lifesaver", helper10: "Super helper", early5: "Early bird", photo10: "Photographer",
      reward1: "First reward", stars100: "100 stars", stars500: "500 stars",
    },
    badgeHow: {
      done: "Finish {n} chores", best_streak: "Do something {n} days in a row",
      taken_over: "Help your siblings {n}×", early: "{n} chores before 9 am",
      photos: "{n} chores with a photo", redeemed: "Redeem {n} reward", earned: "Collect {n} stars",
    },
    badgeEarned: "earned on {date}",
    newBadge: "New badge!",
    levelUp: "Level {n}!",
    youAre: "You are now {title}",
    tapClose: "Tap to continue",
    goal: "My savings goal",
    goalMissing: "{n} stars to go",
    goalReady: "Done! You can redeem it.",
    setGoal: "🎯 Set as goal",
    isGoal: "🎯 My goal",
    familyGoal: "Family goal",
    together: "{n} of {t} ⭐, all together",
    familyReached: "Done! 🎉",
    fgName: "What are you saving for together?",
    fgTarget: "Stars together",
    fgStart: "Start family goal",
    fgClear: "End family goal",
    fgHint: "All children collect together. Nothing is deducted from anyone.",
    fgConfirm: "End family goal “{name}”?",
    tabMoney: "Money",
    money: "Pocket money",
    weekly: "{amount} allowance, every {day}",
    exchange: "Exchange {stars} ⭐ → 1 €",
    confirmExchange: "Exchange {stars} stars for 1 €?",
    rate: "Stars per euro",
    rateHint: "0 = stars can't be exchanged for money",
    payday: "Payday for the allowance",
    perWeek: "€ per week",
    payout: "Pay out",
    confirmPayout: "Pay {amount} to {name}? Hand over cash or transfer it.",
    book: "Book",
    bookPrompt: "Amount in euros (minus subtracts), e.g. 2.50",
    notePrompt: "What for? (optional)",
    history: "History",
    noHistory: "No entries yet.",
    kinds: { allowance: "Allowance", exchange: "Stars exchanged", payout: "paid out", adjust: "booked" },
    days: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    steps: "Steps (one per line, empty = normal chore)",
    stepsShort: "{n} steps",
    templates: "📚 Templates",
    templatesHint: "Tap a template, then choose below who should do it.",
    ageAll: "All",
    ageGroup: "{from}–{to} yrs",
    ageFrom: "{n}+ yrs",
    moneyHint: "The money isn't really kept here. Sternchenplan only keeps the account. You pay out yourselves, in cash or by transfer.",
  },
};

const esc = (value) =>
  String(value ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);

class SternchenplanCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._data = null;
    this._error = null;
    this._tab = "today";
    this._form = this._emptyForm();
    this._awayForm = {};
    this._rewardForm = this._emptyReward();
    this._fgForm = { name: "", target: 300 };
    this._tplAge = 0;
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
          this._spotNews(this._data, data);
          this._data = data;
          this._error = null;
          this._render();
        },
        { type: "sternchenplan/subscribe" },
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
      await this._hass.callService("sternchenplan", service, data);
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
      const url = "/api/sternchenplan/photo";
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
      case "step": {
        const chore = this._data.chores.find((c) => c.id === id);
        const i = Number(el.dataset.i);
        const done = !(chore?.steps_done || []).includes(i);
        if (chore) {
          // Sofort zeigen, der Server bestätigt gleich.
          chore.steps_done = done ? [...chore.steps_done, i] : chore.steps_done.filter((x) => x !== i);
          if (done && chore.steps_done.length === chore.steps.length) this._celebrate(el);
          this._render();
        }
        this._hass
          .callService("sternchenplan", "check_step", { chore_id: id, index: i, done, member })
          .catch((err) => this._notify(err.message));
        break;
      }
      case "tpl":
        this._useTemplate(Number(id));
        break;
      case "tpl-toggle":
        // Klick kommt vor dem Umschalten: merken, damit ein neuer Stand es nicht zuklappt.
        this._tplOpen = !el.parentElement.open;
        break;
      case "tpl-age":
        this._tplOpen = true;
        this._tplAge = Number(id);
        this._render();
        break;
      case "exchange": {
        const rate = this._data.money?.rate;
        if (rate && confirm(this._t("confirmExchange", { stars: rate }))) {
          const data = { euros: 1 };
          if (this._data.tablet) data.member = this._actingAs;
          this._call("exchange_stars", data);
        }
        break;
      }
      case "payout": {
        const k = this._member(id);
        if (k && confirm(this._t("confirmPayout", { amount: this._euro(k.money), name: k.name }))) {
          this._call("payout", { member: id });
        }
        break;
      }
      case "book": {
        const raw = prompt(this._t("bookPrompt"));
        const amount = parseFloat(String(raw || "").replace(",", "."));
        if (amount) this._call("adjust_money", { member: id, amount, note: prompt(this._t("notePrompt")) || "" });
        break;
      }
      case "goal": {
        const data = { reward_id: id || null };
        if (this._data.tablet) data.member = this._actingAs;
        this._call("set_goal", data);
        break;
      }
      case "fgoal-save": {
        const target = parseInt(this._fgForm.target, 10);
        if (this._fgForm.name.trim() && target > 0) {
          this._call("set_family_goal", { name: this._fgForm.name.trim(), target });
          this._fgForm = { name: "", target: 300 };
        }
        break;
      }
      case "fgoal-clear": {
        const g = this._data.family_goal;
        if (g && confirm(this._t("fgConfirm", { name: g.name }))) this._call("clear_family_goal", {});
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
    if (field.startsWith("money.") || field.startsWith("allow.")) {
      if (ev.type !== "change") return;
      // Einstellungen nicht über _call: der sperrt bei schnellen Folgeänderungen.
      const send = (service, data) =>
        this._hass.callService("sternchenplan", service, data).catch((err) => this._notify(err.message));
      if (el.value === "") return;
      if (field.startsWith("allow.")) {
        const amount = Math.max(0, parseFloat(String(el.value).replace(",", ".")) || 0);
        send("set_allowance", { member: field.slice(6), amount });
      } else {
        const m = { ...(this._data.money || { rate: 0, payday: 6 }) };
        m[field.slice(6)] = parseInt(el.value, 10) || 0;
        send("set_money", { rate: m.rate, payday: m.payday });
      }
      return;
    }
    if (field.startsWith("fg.")) {
      this._fgForm[field.slice(3)] = el.value;
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
    return { name: "", assignees: [], recurrence: "daily", due: "", points: 1, rotation: false, approval: false, photo: false, minAge: 0, steps: "", editId: null };
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
      steps: (c.steps || []).join("\n"),
      editId: c.id,
    };
    this._render();
    this.shadowRoot.querySelector("details.form")?.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  _stepList(text) {
    return String(text || "")
      .split("\n")
      .map((x) => x.trim())
      .filter(Boolean);
  }

  _lang() {
    return this._t("rec") === T.de.rec ? "de" : "en";
  }

  // Vorlage ins Formular übernehmen. Wer sie macht, wählen die Eltern selbst.
  _useTemplate(index) {
    const t = TEMPLATES[index];
    if (!t) return;
    const lang = this._lang();
    const due = new Date();
    const [h, m] = t.time.split(":").map(Number);
    due.setHours(h, m, 0, 0);
    if (due < new Date()) due.setDate(due.getDate() + 1);
    this._form = {
      ...this._emptyForm(),
      assignees: this._form.assignees,
      name: t.name[lang],
      points: t.points,
      recurrence: t.rec,
      minAge: t.age,
      photo: !!t.photo,
      steps: (t.steps?.[lang] || []).join("\n"),
      due: this._toLocalInput(due.toISOString()),
    };
    this._render();
    const form = this.shadowRoot.querySelector("details.chore-form");
    if (form) {
      form.open = true;
      form.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }

  _renderTemplates() {
    const lang = this._lang();
    const groups = [[0, 99], [4, 6], [7, 9], [10, 12], [13, 99]];
    const [lo, hi] = groups[this._tplAge] || groups[0];
    const chips = groups
      .map(([a, b], i) => {
        const label = i === 0 ? this._t("ageAll") : b === 99 ? this._t("ageFrom", { n: a }) : this._t("ageGroup", { from: a, to: b });
        return `<button class="tab ${this._tplAge === i ? "on" : ""}" data-action="tpl-age" data-id="${i}">${esc(label)}</button>`;
      })
      .join("");
    // Routinen passen für alle Altersgruppen ab ihrem Mindestalter.
    const items = TEMPLATES.map((t, i) => [t, i])
      .filter(([t]) => this._tplAge === 0 || (t.age >= lo && t.age <= hi) || (t.steps && t.age <= hi))
      .map(
        ([t, i]) => `<button class="tpl" data-action="tpl" data-id="${i}">
          <span class="tpl-emoji">${t.emoji}</span>
          <span class="tpl-name">${esc(t.name[lang])}</span>
          <span class="muted small">⭐ ${t.points} · ${esc(this._t("rec")[t.rec])}${t.steps ? " · " + esc(this._t("stepsShort", { n: t.steps[lang].length })) : ""}</span>
        </button>`,
      )
      .join("");
    return `
      <details class="form templates" ${this._tplOpen ?? !this._data.chores.length ? "open" : ""}>
        <summary data-action="tpl-toggle">${this._t("templates")}</summary>
        <p class="muted small">${this._t("templatesHint")}</p>
        <nav class="tabs small-tabs">${chips}</nav>
        <div class="tpl-grid">${items}</div>
      </details>`;
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
        steps: this._stepList(f.steps),
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
      steps: this._stepList(f.steps),
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
      const stepsLeft = (chore.steps?.length || 0) - (chore.steps_done?.length || 0);
      // Bei Routinen meldet der letzte Schritt. Eltern dürfen trotzdem direkt abhaken,
      // bei Foto-Routinen tippt das Kind nach dem letzten Schritt selbst.
      if (!stepsLeft || this._data.is_manager || photo) {
        action = `<button class="primary" data-action="claim" data-id="${esc(chore.id)}" data-member="${esc(memberId)}" ${
          stepsLeft && !this._data.is_manager ? "disabled" : ""
        }>${photo ? this._t("photoDone") : "✓ " + label}</button>`;
      }
    }
    const steps = chore.steps?.length && chore.state !== "claimed" ? this._steps(chore, memberId, ro || !showClaim) : "";
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
        ${steps}
      </li>`;
  }

  _steps(chore, memberId, ro) {
    const done = new Set(chore.steps_done || []);
    return `<ol class="steps">${chore.steps
      .map(
        (text, i) => `<li><button class="step ${done.has(i) ? "on" : ""}" ${ro ? "disabled" : ""} data-action="step" data-id="${esc(chore.id)}" data-member="${esc(memberId)}" data-i="${i}">
          <span class="tick">${done.has(i) ? "✓" : ""}</span><span>${esc(text)}</span></button></li>`,
      )
      .join("")}</ol>`;
  }

  _photoNeeded(chore) {
    return !!chore?.requires_photo && !this._data.is_manager;
  }

  _photoIcon(chore) {
    return chore.requires_photo ? ' <span class="muted">📷</span>' : "";
  }

  _donateLine() {
    const url = this._data.donate_url;
    if (!url) return "";
    return `<p class="muted small pro"><a href="${esc(url)}" target="_blank" rel="noopener">${esc(this._t("donate"))}</a></p>`;
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
    if (!t?.allowed || this._config.readonly || member.id !== this._me()) return "";
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
        const isGoal = member.goal === r.id;
        const goalBtn = ro
          ? isGoal ? `<span class="chip">${this._t("isGoal")}</span>` : ""
          : `<button class="link goal-btn ${isGoal ? "on" : ""}" data-action="goal" data-id="${isGoal ? "" : esc(r.id)}">${this._t(isGoal ? "isGoal" : "setGoal")}</button>`;
        return `
        <div class="reward ${enough ? "ready" : ""} ${isGoal ? "is-goal" : ""}">
          <div class="reward-emoji">${this._rewardEmoji(r.name)}</div>
          <div class="reward-name">${esc(r.name)}</div>
          <div class="reward-cost">⭐ ${r.cost}</div>
          <div class="bar"><span style="width:${pct}%"></span></div>
          <div class="reward-action">${action}</div>
          ${goalBtn}
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
          <div class="main"><div class="title">${esc(r.name)}</div><div class="sub muted">⭐ ${r.cost} · ${esc(names(r.members))}</div></div>
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
      ${rows ? `<ul>${rows}</ul>` : `<p class="empty muted">${this._t("noRewards")}</p>`}
      ${this._renderFamilyGoalAdmin()}`;
  }

  _renderFamilyGoalAdmin() {
    const g = this._data.family_goal;
    const f = this._fgForm;
    return `
      <div class="section-title">🏰 ${this._t("familyGoal")}</div>
      ${g ? `${this._renderFamilyGoal()}<button class="link bad" data-action="fgoal-clear">${this._t("fgClear")}</button>` : ""}
      <details class="form" ${g ? "" : "open"}>
        <summary>+ ${this._t("fgStart")}</summary>
        <p class="muted small">${this._t("fgHint")}</p>
        <div class="grid">
          <label>${this._t("fgName")}<input data-field="fg.name" value="${esc(f.name)}" maxlength="60" placeholder="Freizeitpark"></label>
          <label>${this._t("fgTarget")}<input type="number" min="1" data-field="fg.target" value="${esc(f.target)}"></label>
        </div>
        <button class="primary" data-action="fgoal-save">${this._t("fgStart")}</button>
      </details>`;
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
            <span class="tile-sub">${open ? esc(this._t("openCount", { n: open })) : "✓"} · ⭐ ${m.points}${m.progress?.streak ? ` · 🔥 ${m.progress.streak}` : ""}</span>
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
        ${this._renderLevel(member)}
        ${this._renderGoal(member)}
        ${this._renderFamilyGoal()}
        ${member.locked ? `<p class="chip bad">${this._t("locked")}</p>` : ""}
        <div class="section-title">${this._t("todayTitle")}</div>
        ${list}
        ${this._renderTakeOver(member)}
        ${this._renderChildRewards(member)}
        ${this._renderMoney(member)}
        ${this._renderBadges(member)}
      </div>`;
  }

  _renderGoal(member) {
    const reward = member.goal && (this._data.rewards || []).find((r) => r.id === member.goal);
    if (!reward) return "";
    const pct = Math.min(100, Math.round((member.points / reward.cost) * 100));
    const ready = member.points >= reward.cost;
    const ro = this._config.readonly || member.id !== this._me();
    return `
      <div class="goal ${ready ? "ready" : ""}">
        <div class="goal-emoji">${this._rewardEmoji(reward.name)}</div>
        <div class="goal-main">
          <div class="muted small">🎯 ${this._t("goal")}</div>
          <strong>${esc(reward.name)}</strong>
          <div class="xp"><i style="width:${pct}%"></i></div>
          <div class="muted small">⭐ ${member.points} / ${reward.cost} · ${esc(ready ? this._t("goalReady") : this._t("goalMissing", { n: reward.cost - member.points }))}</div>
        </div>
        ${ready && !ro ? `<button class="primary" data-action="redeem" data-id="${esc(reward.id)}">${this._t("redeem")}</button>` : ""}
      </div>`;
  }

  _euro(cents) {
    return new Intl.NumberFormat(this._locale(), { style: "currency", currency: "EUR" }).format(cents / 100);
  }

  _moneyLog(member) {
    const log = member.money_log || [];
    if (!log.length) return `<p class="muted small">${this._t("noHistory")}</p>`;
    const kinds = this._t("kinds");
    return `<ul class="ledger">${log
      .slice(0, 10)
      .map(
        (e) => `<li><span>${esc(e.note || kinds[e.kind] || e.kind)}${e.stars ? ` · ${e.stars} ⭐` : ""}<span class="muted small"> · ${new Date(e.at).toLocaleDateString(this._locale())}</span></span>
          <b class="${e.cents < 0 ? "minus" : "plus"}">${e.cents > 0 ? "+" : ""}${esc(this._euro(e.cents))}</b></li>`,
      )
      .join("")}</ul>`;
  }

  _renderMoney(member) {
    const m = this._data.money || {};
    if (!m.rate && !member.allowance && !member.money) return "";
    const ro = this._config.readonly || member.id !== this._me();
    const can = m.rate && member.points >= m.rate;
    return `
      <section class="money">
        <div class="section-title">💶 ${this._t("money")}</div>
        <div class="wallet">
          <div class="wallet-sum">${esc(this._euro(member.money || 0))}</div>
          ${member.allowance ? `<div class="muted small">${esc(this._t("weekly", { amount: this._euro(member.allowance), day: this._t("days")[m.payday ?? 6] }))}</div>` : ""}
          ${m.rate && !ro ? `<button class="primary" data-action="exchange" ${can ? "" : "disabled"}>${esc(this._t("exchange", { stars: m.rate }))}</button>` : ""}
        </div>
        <details class="ledger-box"><summary class="muted small">${this._t("history")}</summary>${this._moneyLog(member)}</details>
      </section>`;
  }

  _renderMoneyAdmin() {
    const m = this._data.money || { rate: 0, payday: 6 };
    const days = this._t("days");
    const rows = this._children()
      .map(
        (k) => `
        <section class="kidcard money-kid" style="--kid:${this._color(k.id)}">
          <div class="kidcard-head">
            ${this._avatar(k, 40)}
            <div class="kidcard-name"><strong>${esc(k.name)}</strong><span class="muted small">⭐ ${k.points}</span></div>
            <div class="wallet-sum small-sum">${esc(this._euro(k.money || 0))}</div>
          </div>
          <div class="money-row">
            <label>${this._t("perWeek")}<input type="number" min="0" step="0.5" data-field="allow.${esc(k.id)}" value="${(k.allowance || 0) / 100}"></label>
            <button class="link" data-action="book" data-id="${esc(k.id)}">± ${this._t("book")}</button>
            <button class="primary" data-action="payout" data-id="${esc(k.id)}" ${k.money > 0 ? "" : "disabled"}>${this._t("payout")}</button>
          </div>
          <details class="ledger-box"><summary class="muted small">${this._t("history")}</summary>${this._moneyLog(k)}</details>
        </section>`,
      )
      .join("");
    return `
      <div class="form money-settings">
        <div class="grid">
          <label>${this._t("rate")}<input type="number" min="0" data-field="money.rate" value="${m.rate}"><span class="muted small">${this._t("rateHint")}</span></label>
          <label>${this._t("payday")}<select data-field="money.payday">${days
            .map((d, i) => `<option value="${i}" ${i === m.payday ? "selected" : ""}>${esc(d)}</option>`)
            .join("")}</select></label>
        </div>
      </div>
      <div class="kidgrid">${rows}</div>
      <p class="muted small">${this._t("moneyHint")}</p>`;
  }

  _renderFamilyGoal() {
    const g = this._data.family_goal;
    if (!g) return "";
    const pct = Math.min(100, Math.round((g.progress / g.target) * 100));
    return `
      <div class="fgoal ${g.reached_at ? "ready" : ""}">
        <div class="fgoal-top"><span class="fgoal-icon">🏰</span>
          <div class="goal-main"><div class="muted small">${this._t("familyGoal")}</div><strong>${esc(g.name)}</strong></div>
          <div class="fgoal-kids">${this._children().map((m) => this._avatar(m, 26)).join("")}</div>
        </div>
        <div class="xp fgoal-bar"><i style="width:${pct}%"></i></div>
        <div class="muted small">${esc(g.reached_at ? this._t("familyReached") : this._t("together", { n: g.progress, t: g.target }))}</div>
      </div>`;
  }

  _levelTitle(level) {
    const titles = this._t("levelTitles");
    return titles[Math.min(level, titles.length) - 1];
  }

  _renderLevel(member) {
    const p = member.progress;
    if (!p) return "";
    const span = Math.max(1, p.level_to - p.level_from);
    const pct = Math.min(100, Math.round(((p.earned - p.level_from) / span) * 100));
    const streak = p.streak
      ? `<span class="streak ${p.streak_today ? "hot" : "cold"}" title="${esc(this._t("best", { n: p.best_streak }))}">🔥 ${esc(
          p.streak === 1 ? this._t("streakOne") : this._t("streakDays", { n: p.streak }),
        )}</span>`
      : "";
    const hint = p.streak_today ? "streakDone" : p.streak ? "streakKeep" : "streakStart";
    return `
      <div class="level">
        <div class="level-top">
          <span class="level-badge">${p.level}</span>
          <div class="level-name"><strong>${esc(this._levelTitle(p.level))}</strong>
            <span class="muted small">${esc(this._t("toNext", { n: p.level_to - p.earned, next: p.level + 1 }))}</span></div>
          ${streak}
        </div>
        <div class="xp" role="progressbar" aria-valuenow="${pct}" aria-valuemin="0" aria-valuemax="100"><i style="width:${pct}%"></i></div>
        <div class="muted small streak-hint">${esc(this._t(hint))}</div>
      </div>`;
  }

  _renderBadges(member) {
    const list = member.progress?.badges;
    if (!list) return "";
    const names = this._t("badgeNames");
    const how = this._t("badgeHow");
    const got = list.filter((b) => b.earned_at).length;
    const items = list
      .map((b) => {
        const name = names[b.id] || b.id;
        const sub = b.earned_at
          ? this._t("badgeEarned", { date: new Date(b.earned_at).toLocaleDateString(this._locale()) })
          : `${(how[b.counter] || "{n}").replace("{n}", b.target)} · ${b.value}/${b.target}`;
        const pct = Math.round((b.value / b.target) * 100);
        return `
          <li class="bdg ${b.earned_at ? "got" : ""}" title="${esc(name)}: ${esc(sub)}">
            <span class="badge-emoji">${b.earned_at ? b.emoji : "🔒"}</span>
            <span class="badge-name">${esc(name)}</span>
            ${b.earned_at ? "" : `<span class="badge-bar"><i style="width:${pct}%"></i></span>`}
            <span class="badge-sub">${esc(sub)}</span>
          </li>`;
      })
      .join("");
    return `
      <details class="badges">
        <summary class="section-title">🏆 ${this._t("badges")} <span class="muted small">${got}/${list.length}</span></summary>
        <ul class="badge-grid">${items}</ul>
      </details>`;
  }

  // Neues Level oder Abzeichen für das Kind, das gerade zu sehen ist: groß feiern.
  _spotNews(before, after) {
    if (!before || !after) return;
    const id = this._shownChild();
    if (!id) return;
    const old = before.members.find((m) => m.id === id)?.progress;
    const now = after.members.find((m) => m.id === id)?.progress;
    if (!old || !now) return;
    if (now.level > old.level) {
      this._party("⭐", this._t("levelUp", { n: now.level }), this._t("youAre", { title: this._levelTitle(now.level) }));
      return;
    }
    const had = new Set(old.badges.filter((b) => b.earned_at).map((b) => b.id));
    const fresh = now.badges.find((b) => b.earned_at && !had.has(b.id));
    if (fresh) this._party(fresh.emoji, this._t("newBadge"), this._t("badgeNames")[fresh.id] || fresh.id);
  }

  _party(emoji, title, text) {
    this.shadowRoot.querySelector(".party")?.remove();
    const box = document.createElement("div");
    box.className = "party";
    box.setAttribute("role", "dialog");
    box.innerHTML = `<div class="party-card"><div class="party-emoji">${esc(emoji)}</div><div class="party-title">${esc(title)}</div><div class="party-text">${esc(text)}</div><div class="muted small">${esc(this._t("tapClose"))}</div></div>`;
    box.addEventListener("click", () => box.remove());
    this.shadowRoot.appendChild(box);
    setTimeout(() => box.remove(), 6000);
    requestAnimationFrame(() => this._celebrate(box.querySelector(".party-emoji")));
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
      ["money", this._t("tabMoney")],
      ["away", this._t("tabAway")],
    ];
    let body = "";
    if (this._tab === "approve") body = this._renderApprovals(waiting);
    else if (this._tab === "chores") body = this._renderChores();
    else if (this._tab === "rewards") body = this._renderRewardAdmin();
    else if (this._tab === "money") body = this._renderMoneyAdmin();
    else if (this._tab === "away") body = this._renderAway();
    else body = this._renderToday();
    return `
      <nav class="tabs">${tabs
        .map(([id, label]) => `<button class="tab ${this._tab === id ? "on" : ""}" data-action="tab" data-id="${id}">${label}</button>`)
        .join("")}</nav>
      ${body}
      ${this._donateLine()}`;
  }

  _children() {
    return this._data.members.filter((m) => m.role === "child");
  }

  _renderToday() {
    return `${this._renderFamilyGoal()}<div class="kidgrid">${this._renderTodayCards()}</div>`;
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
        if (m.has_devices && !this._config.readonly) {
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
              <div class="kidcard-name"><strong>${esc(m.name)}</strong><span class="muted small">⭐ ${m.points}${
                m.progress ? ` · ${esc(this._t("level", { n: m.progress.level }))}${m.progress.streak ? ` · 🔥 ${m.progress.streak}` : ""}` : ""
              }</span></div>
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
            <div class="sub muted">${esc(this._member(r.member_id)?.name)} ${this._t("wantsReward")} · ⭐ ${r.cost}</div>
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
            }${c.requires_photo ? " · 📷" : ""}${c.steps?.length ? " · ☑️ " + esc(this._t("stepsShort", { n: c.steps.length })) : ""}${c.min_age ? " · " + esc(this._t("fromAge", { n: c.min_age })) : ""}${c.assignees.length && !c.responsible.length ? ` · <span class="chip">${this._t("paused")}</span>` : ""}</div>
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
      ${f.editId ? "" : this._renderTemplates()}
      <details class="form chore-form" ${this._data.chores.length && !f.editId && !f.name ? "" : "open"}>
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
        <label class="check"><input type="checkbox" data-field="photo" ${f.photo ? "checked" : ""}>${this._t("photo")}</label>
        <label>${this._t("steps")}<textarea data-field="steps" rows="3" maxlength="800">${esc(f.steps)}</textarea></label>
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

  // Welches Kind die Karte gerade zeigt (null in der Elternansicht). Wie in _render.
  _shownChild() {
    if (!this._data) return null;
    if (this._config.member) return this._memberByConfig()?.id ?? null;
    if (this._data.tablet && !this._data.is_manager) return this._actingAs;
    const me = this._member(this._data.me);
    const mode = this._config.mode;
    if (mode === "eltern" || (mode === "auto" && this._data.is_manager && (!me || me.role === "parent"))) return null;
    return me?.role === "child" ? me.id : null;
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

// Vorlagen nach Alter. age = Mindestalter, time = übliche Uhrzeit für die erste Frist.
const TEMPLATES = [
  { emoji: "🌅", age: 4, points: 3, rec: "daily", time: "07:30",
    name: { de: "Morgenroutine", en: "Morning routine" },
    steps: { de: ["Aufstehen", "Anziehen", "Zähne putzen", "Bett machen"], en: ["Get up", "Get dressed", "Brush teeth", "Make the bed"] } },
  { emoji: "🌙", age: 4, points: 3, rec: "daily", time: "19:30",
    name: { de: "Abendroutine", en: "Evening routine" },
    steps: { de: ["Schlafanzug anziehen", "Zähne putzen", "Kleidung weglegen", "Licht aus"], en: ["Put on pyjamas", "Brush teeth", "Put clothes away", "Lights out"] } },
  { emoji: "🎒", age: 6, points: 2, rec: "daily", time: "19:00",
    name: { de: "Schultasche packen", en: "Pack school bag" },
    steps: { de: ["Hausaufgaben einpacken", "Stundenplan prüfen", "Brotdose", "Trinkflasche"], en: ["Pack homework", "Check timetable", "Lunch box", "Water bottle"] } },
  { emoji: "📚", age: 7, points: 3, rec: "daily", time: "16:00",
    name: { de: "Hausaufgaben", en: "Homework" },
    steps: { de: ["Alles erledigt", "Mama oder Papa zeigen", "Wieder einpacken"], en: ["All done", "Show a parent", "Pack it away"] } },
  { emoji: "🧸", age: 4, points: 1, rec: "daily", time: "18:30", name: { de: "Spielzeug aufräumen", en: "Tidy up toys" } },
  { emoji: "🍽️", age: 4, points: 1, rec: "daily", time: "18:00", name: { de: "Tisch decken", en: "Set the table" } },
  { emoji: "🧦", age: 4, points: 1, rec: "weekly", time: "17:00", name: { de: "Socken sortieren", en: "Sort socks" } },
  { emoji: "🪴", age: 5, points: 1, rec: "weekly", time: "17:00", name: { de: "Blumen gießen", en: "Water the plants" } },
  { emoji: "🐹", age: 5, points: 1, rec: "daily", time: "18:00", name: { de: "Haustier füttern", en: "Feed the pet" } },
  { emoji: "🛏️", age: 6, points: 1, rec: "daily", time: "08:00", name: { de: "Bett machen", en: "Make the bed" } },
  { emoji: "🍽️", age: 7, points: 2, rec: "daily", time: "19:00", name: { de: "Spülmaschine ausräumen", en: "Empty the dishwasher" } },
  { emoji: "🗑️", age: 8, points: 1, rec: "daily", time: "19:00", name: { de: "Müll rausbringen", en: "Take out the trash" } },
  { emoji: "🧹", age: 7, points: 3, rec: "weekly", time: "18:00", photo: true, name: { de: "Zimmer aufräumen", en: "Tidy up room" } },
  { emoji: "👕", age: 8, points: 2, rec: "weekly", time: "18:00", name: { de: "Wäsche zusammenlegen", en: "Fold laundry" } },
  { emoji: "🧽", age: 10, points: 2, rec: "weekly", time: "18:00", name: { de: "Waschbecken putzen", en: "Clean the sink" } },
  { emoji: "🌀", age: 10, points: 3, rec: "weekly", time: "17:00", name: { de: "Staubsaugen", en: "Vacuum" } },
  { emoji: "📦", age: 10, points: 2, rec: "weekly", time: "18:00", name: { de: "Altpapier wegbringen", en: "Take out paper recycling" } },
  { emoji: "🧺", age: 10, points: 2, rec: "weekly", time: "18:00", name: { de: "Wäsche aufhängen", en: "Hang up laundry" } },
  { emoji: "🛒", age: 11, points: 2, rec: "weekly", time: "17:00", name: { de: "Beim Einkaufen helfen", en: "Help with shopping" } },
  { emoji: "🛁", age: 12, points: 5, rec: "weekly", time: "18:00", photo: true, name: { de: "Bad putzen", en: "Clean the bathroom" } },
  { emoji: "🍳", age: 12, points: 4, rec: "weekly", time: "18:00", name: { de: "Beim Kochen helfen", en: "Help with cooking" } },
  { emoji: "🛌", age: 12, points: 3, rec: "biweekly", time: "18:00", name: { de: "Bettwäsche wechseln", en: "Change bed sheets" } },
  { emoji: "🌱", age: 13, points: 5, rec: "weekly", time: "17:00", name: { de: "Rasen mähen", en: "Mow the lawn" } },
  { emoji: "🚗", age: 14, points: 4, rec: "biweekly", time: "17:00", name: { de: "Auto aussaugen", en: "Vacuum the car" } },
];

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
  p.pro a { color: var(--secondary-text-color); text-decoration: none; }
  p.pro a:hover { color: var(--primary-color); }
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
  /* -- Level, Serie, Abzeichen (0.16) -- */
  .level { margin: 0 0 10px; padding: 10px 14px 8px; border-radius: 16px; background: var(--secondary-background-color); }
  .level-top { display: flex; align-items: center; gap: 10px; }
  .level-badge { flex: 0 0 auto; width: 38px; height: 38px; border-radius: 12px; display: flex; align-items: center; justify-content: center;
                 font-weight: 800; font-size: 1.15em; color: #fff; transform: rotate(-6deg);
                 background: linear-gradient(135deg, var(--kid), color-mix(in srgb, var(--kid) 70%, #fff)); box-shadow: 0 3px 8px color-mix(in srgb, var(--kid) 40%, transparent); }
  .level-name { flex: 1; min-width: 0; display: flex; flex-direction: column; line-height: 1.25; }
  .streak { flex: 0 0 auto; font-weight: 700; font-size: 0.85em; padding: 4px 10px; border-radius: 14px; white-space: nowrap; }
  .streak.hot { background: linear-gradient(135deg, #ff7a45, #ffb03a); color: #fff; box-shadow: 0 2px 8px rgba(255,122,69,.45); animation: flame 1.6s ease-in-out infinite; }
  .streak.cold { background: var(--card-background-color); color: var(--secondary-text-color); border: 1px dashed #ff7a45; }
  .xp { height: 10px; border-radius: 5px; margin: 10px 0 4px; overflow: hidden; background: color-mix(in srgb, var(--kid) 14%, var(--card-background-color)); }
  .xp i { display: block; height: 100%; border-radius: 5px; transition: width .8s cubic-bezier(.2,.8,.2,1);
          background: linear-gradient(90deg, color-mix(in srgb, var(--kid) 75%, #fff), var(--kid)); }
  .streak-hint { font-size: 0.8em; }
  details.badges summary { list-style: none; cursor: pointer; display: flex; align-items: center; gap: 8px; }
  details.badges summary::-webkit-details-marker { display: none; }
  details.badges summary::after { content: "▾"; margin-left: auto; color: var(--secondary-text-color); transition: transform .2s; }
  details.badges[open] summary::after { transform: rotate(180deg); }
  .badge-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(104px, 1fr)); gap: 8px; }
  .bdg { display: flex; flex-direction: column; align-items: center; text-align: center; gap: 3px; padding: 10px 6px;
         border-radius: 14px; background: var(--secondary-background-color); }
  .bdg .badge-emoji { font-size: 1.9em; filter: grayscale(1); opacity: .45; }
  .bdg.got { background: linear-gradient(160deg, color-mix(in srgb, var(--kid) 20%, var(--card-background-color)), var(--secondary-background-color));
             box-shadow: inset 0 0 0 2px color-mix(in srgb, var(--kid) 45%, transparent); }
  .bdg.got .badge-emoji { filter: none; opacity: 1; }
  .badge-name { font-weight: 600; font-size: 0.82em; overflow-wrap: anywhere; }
  .badge-sub { font-size: 0.72em; color: var(--secondary-text-color); }
  .badge-bar { width: 80%; height: 4px; border-radius: 2px; background: var(--divider-color, #e0e0e0); overflow: hidden; }
  .badge-bar i { display: block; height: 100%; background: var(--kid); }
  .goal, .fgoal { margin: 0 0 10px; padding: 12px 14px; border-radius: 16px; background: var(--secondary-background-color); }
  .goal { display: flex; align-items: center; gap: 12px; }
  .goal.ready { box-shadow: inset 0 0 0 2px var(--kid); }
  .goal-emoji { font-size: 2.2em; }
  .goal-main { flex: 1; min-width: 0; display: flex; flex-direction: column; }
  .goal .xp { margin: 6px 0 4px; }
  .fgoal { background: linear-gradient(135deg, color-mix(in srgb, #a259ff 16%, var(--card-background-color)), color-mix(in srgb, #4f7cff 12%, var(--card-background-color))); }
  .fgoal-top { display: flex; align-items: center; gap: 10px; }
  .fgoal-icon { font-size: 1.9em; }
  .fgoal-kids { display: flex; }
  .fgoal-kids .avatar { margin-left: -6px; border: 2px solid var(--card-background-color); }
  .fgoal-bar i { background: linear-gradient(90deg, #a259ff, #4f7cff, #22a565); }
  .fgoal.ready .fgoal-bar i { background: linear-gradient(90deg, #22a565, #e5a100); }
  .fgoal .xp { background: color-mix(in srgb, #a259ff 14%, var(--card-background-color)); margin: 10px 0 4px; }
  .reward.is-goal { box-shadow: inset 0 0 0 2px #e5a100; }
  button.goal-btn { min-height: 28px; font-size: 0.8em; }
  button.goal-btn.on { color: #e5a100; font-weight: 600; }
  .wallet { display: flex; flex-direction: column; align-items: center; gap: 6px; padding: 14px; border-radius: 16px;
            background: linear-gradient(135deg, color-mix(in srgb, #22a565 18%, var(--card-background-color)), var(--secondary-background-color)); }
  .wallet-sum { font-size: 2em; font-weight: 800; letter-spacing: -.5px; }
  .wallet-sum.small-sum { font-size: 1.3em; }
  .wallet button.primary { background: #22a565; }
  .wallet button[disabled], .money-row button[disabled] { opacity: .45; cursor: default; }
  .ledger-box summary { cursor: pointer; padding: 6px 0 2px; }
  ul.ledger li { display: flex; justify-content: space-between; gap: 8px; padding: 6px 0; border-bottom: 1px solid var(--divider-color, #e0e0e0); font-size: 0.9em; }
  ul.ledger li:last-child { border-bottom: none; }
  .ledger .plus { color: var(--success-color, #22a565); }
  .ledger .minus { color: var(--secondary-text-color); }
  .money-row { display: flex; align-items: flex-end; gap: 8px; flex-wrap: wrap; margin-top: 8px; }
  .money-row label { display: flex; flex-direction: column; gap: 2px; font-size: 0.8em; width: 110px; }
  .money-row .primary { margin-left: auto; }
  .money-settings label span { font-size: 0.8em; }
  ol.steps { list-style: none; margin: 8px 0 0; padding: 0; width: 100%; display: flex; flex-direction: column; gap: 6px; }
  button.step { width: 100%; display: flex; align-items: center; gap: 10px; text-align: left; min-height: 40px; padding: 6px 12px;
                border-radius: 12px; background: var(--card-background-color); color: var(--primary-text-color); }
  button.step .tick { flex: 0 0 auto; width: 22px; height: 22px; border-radius: 50%; border: 2px solid var(--kid, var(--primary-color));
                      display: flex; align-items: center; justify-content: center; font-size: 0.8em; font-weight: 800; color: #fff; }
  button.step.on .tick { background: var(--kid, var(--primary-color)); animation: popin .25s ease-out; }
  button.step.on span:last-child { text-decoration: line-through; color: var(--secondary-text-color); }
  button.step[disabled] { cursor: default; }
  .row.task { flex-wrap: wrap; }
  .templates .small-tabs { margin: 6px 0; }
  .small-tabs .tab { font-size: 0.85em; min-height: 30px; }
  .tpl-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 8px; }
  button.tpl { display: flex; flex-direction: column; align-items: flex-start; gap: 2px; text-align: left; padding: 10px 12px;
               border-radius: 14px; background: var(--card-background-color); color: var(--primary-text-color); min-height: 76px;
               box-shadow: 0 1px 2px rgba(0,0,0,.08); }
  button.tpl:hover { box-shadow: 0 0 0 2px var(--primary-color); }
  .tpl-emoji { font-size: 1.5em; }
  .tpl-name { font-weight: 600; }
  .form textarea { font: inherit; padding: 8px; border-radius: 8px; border: 1px solid var(--divider-color, #ccc);
                   background: var(--card-background-color); color: var(--primary-text-color); resize: vertical; }
  button.primary[disabled] { opacity: .45; cursor: default; }
  @keyframes popin { from { transform: scale(.4); } }
  .party { position: fixed; inset: 0; z-index: 9; display: flex; align-items: center; justify-content: center;
           background: rgba(0,0,0,.45); animation: fade .25s ease-out; cursor: pointer; }
  .party-card { text-align: center; padding: 26px 34px; border-radius: 24px; background: var(--card-background-color);
                box-shadow: 0 12px 40px rgba(0,0,0,.35); animation: zoom .45s cubic-bezier(.2,1.4,.4,1); max-width: 80vw; }
  .party-emoji { font-size: 4.2em; line-height: 1.1; animation: wiggle 1s ease-in-out .4s 2; }
  .party-title { font-size: 1.6em; font-weight: 800; margin-top: 6px; }
  .party-text { font-size: 1.1em; margin: 4px 0 12px; }
  @keyframes flame { 50% { transform: scale(1.06); } }
  @keyframes fade { from { opacity: 0; } }
  @keyframes zoom { from { transform: scale(.4); opacity: 0; } }
  @keyframes wiggle { 25% { transform: rotate(-12deg); } 75% { transform: rotate(12deg); } }
  @media (prefers-reduced-motion: reduce) { .streak.hot, .party-card, .party-emoji, .xp i { animation: none; transition: none; } }
  @media (max-width: 420px) { .row { flex-wrap: wrap; } .actions { width: 100%; justify-content: flex-start; }
    ul.tasks .actions { width: auto; } .hero { padding: 12px; } .hero .hello { font-size: 1.2em; } }
`;

// Eigene Seite in der Seitenleiste („Sternchenplan“). Zeigt die Karte groß,
// damit niemand erst ein Dashboard einrichten muss.
class SternchenplanPanel extends HTMLElement {
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
      <div class="bar"><ha-menu-button></ha-menu-button><h1>Sternchenplan</h1></div>
      <div class="wrap"></div>`;
    const menu = this.shadowRoot.querySelector("ha-menu-button");
    menu.hass = this._hass;
    menu.narrow = this._narrow;
    this._card = document.createElement("sternchenplan-card");
    this._card.setConfig({ mode: "auto" });
    this.shadowRoot.querySelector(".wrap").appendChild(this._card);
  }
}

if (!customElements.get("sternchenplan-panel")) {
  customElements.define("sternchenplan-panel", SternchenplanPanel);
}

if (!customElements.get("sternchenplan-card")) {
  customElements.define("sternchenplan-card", SternchenplanCard);
  window.customCards = window.customCards || [];
  window.customCards.push({
    type: "sternchenplan-card",
    name: "Sternchenplan",
    description: "Aufgaben der Familie: Kinder melden, Eltern geben frei.",
  });
  console.info(`%c STERNCHENPLAN-CARD %c ${VERSION} `, "background:#3f51b5;color:#fff", "");
}
