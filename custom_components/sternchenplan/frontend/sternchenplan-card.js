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

const VERSION = "0.32.0";

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
    starsBtn: "⭐ Bonus oder Abzug",
    moreActions: "Mehr für {name}",
    greet: ["Guten Morgen", "Hallo", "Guten Abend"],
    ckOpen: "Aufgaben offen",
    ckWaiting: "warten auf dich",
    ckKidsDone: "Kinder fertig",
    ckStars: "Sterne heute",
    ckWaitingTitle: "📬 Wartet auf dich",
    wzHello: "Willkommen bei Sternchenplan!",
    wzHelloText: "In einer Minute ist euer Familienplan startklar. Ich stelle dir vier kurze Fragen, alles lässt sich später ändern.",
    wzStart: "Los geht’s",
    wzSkip: "Ich richte alles selbst ein",
    wzNext: "Weiter",
    wzBack: "Zurück",
    wzKids: "Wer macht mit?",
    wzKidsText: "Mit dem Alter schlage ich passende Aufgaben vor. Jedes Kind kann sich auch gleich sein Design aussuchen.",
    wzNoKids: "Noch keine Kinder angelegt. Das geht unter Einstellungen → Geräte & Dienste → Sternchenplan → Konfigurieren → Mitglied hinzufügen.",
    wzAge: "Alter",
    wzAgeNone: "–",
    wzChores: "Welche Aufgaben passen zu euch?",
    wzChoresText: "Gemeinsame Aufgaben wechseln reihum, eigene bekommt jedes Kind selbst. Tippe an, was weg soll.",
    wzShared: "Gemeinsam, reihum",
    wzOwn: "Für jedes Kind",
    wzRewards: "Worauf sparen die Kinder?",
    wzRewardsText: "Belohnungen tauschen die Kinder gegen Sterne ein. Du bestätigst jedes Einlösen.",
    wzPhotos: "Fotos vom Erledigen",
    wzPhotosText: "Bei manchen Aufgaben machen Kinder ein Foto als Nachweis. Nur Eltern sehen es. Was soll danach passieren?",
    wzPhotoDelete: "Nach meiner Entscheidung löschen",
    wzPhotoDeleteSub: "Empfohlen. Es bleibt nichts gespeichert.",
    wzPhotoKeep: "Behalten",
    wzPhotoKeepSub: "Fotos bleiben im Home Assistant, bis du sie löschst.",
    wzFinish: "✨ Alles anlegen",
    wzWorking: "Ich lege alles an …",
    wzDone: "Fertig! Euer Plan steht.",
    wzDoneText: "{n} Aufgaben und {r} Belohnungen sind angelegt.",
    wzTips: ["Kinder öffnen in der Home-Assistant-App den Menüpunkt „Sternchenplan“.", "Neue Aufgaben legst du unter „Aufgaben“ an, mit Vorlagen nach Alter.", "Der ❓-Knopf erklärt jeden Bereich."],
    wzGo: "Zum Plan",
    wzStep: "Schritt {n} von 4",
    themeTitle: "🎨 Mein Design",
    themeParent: "Design",
    themeNames: { "": "Klar", space: "Weltraum", jungle: "Dschungel", ocean: "Ozean", candy: "Bonbon", elegant: "Elegant" },
    allDoneKid: "Alles geschafft für heute!",
    allDoneKidSub: "Super gemacht. Morgen geht’s weiter.",
    nfc: "📱 NFC-Aufkleber",
    moreOptions: "Mehr Optionen (Freigabe, Foto, Tage, Routine, NFC, Haus …)",
    starterTitle: "✨ In einer Minute startklar",
    starterText: "Ich schlage passende Aufgaben nach Alter vor. Gemeinsame Aufgaben wechseln reihum, eigene bekommt jedes Kind selbst. Alles lässt sich später ändern.",
    starterChores: "Aufgaben",
    starterRewards: "Belohnungen",
    starterGo: "✨ Alles anlegen",
    starterLater: "Nein danke, ich mache es selbst",
    starterDone: "Fertig! {n} Aufgaben und {r} Belohnungen sind angelegt.",
    starterNoKids: "Lege zuerst die Kinder an (Einstellungen → Geräte & Dienste → Sternchenplan → Konfigurieren).",
    shared: "reihum: {names}",
    help: "❓ Hilfe",
    helpTabs: {
      today: "Hier siehst du, was jedes Kind heute noch tun muss. Mit „± Sterne“ gibst du Bonus oder ziehst ab, unten steht die Wochenbilanz.",
      approve: "Hier bestätigst du gemeldete Aufgaben und Belohnungen. Einfacher geht es direkt in der Push-Nachricht auf dem Handy.",
      chores: "Hier legst du Aufgaben an. Am schnellsten über „Vorlagen“. Die Grundeinstellungen reichen meistens, der Rest steht unter „Mehr Optionen“.",
      rewards: "Belohnungen, die Kinder mit Sternen einlösen. Kleine Belohnungen (10–20 Sterne) motivieren am meisten.",
      money: "Optional: Sterne in Taschengeld tauschen und wöchentliches Taschengeld verwalten.",
      away: "Ferien eintragen (dann ruht alles) oder ein Kind abwesend melden, z. B. bei Krankheit oder Übernachtung.",
    },
    house: "🏠 Das Haus prüft selbst",
    houseHint: "Ohne Automation: Ein Gerät oder Sensor hakt die Aufgabe ab oder sagt dem Kind, dass es dran ist.",
    houseDone: "Erledigt, wenn",
    houseStart: "Jetzt dran, wenn",
    houseEntity: "Gerät oder Sensor",
    houseState: "Zustand",
    houseNow: "jetzt: {state}",
    houseExamples: "Beispiele: Saugroboter „docked“ → Staubsaugen erledigt. Spülmaschine „off“ → „Jetzt bist du dran: ausräumen“.",
    nfcHint: "Kleb einen NFC-Aufkleber z. B. an die Mülltonne. Wer ihn mit dem Handy (Home-Assistant-App) antippt, hat die Aufgabe erledigt.",
    nfcLearn: "Aufkleber anlernen",
    nfcWaiting: "Jetzt den Aufkleber mit dem Handy antippen (2 Minuten) …",
    nfcLinked: "✓ Aufkleber verbunden",
    nfcRemove: "lösen",
    nfcSaveFirst: "Erst speichern, dann Aufkleber anlernen.",
    voiceTitle: "🎙️ Sprachbefehle (Home Assistant Assist, auch über Alexa-Skill oder Sprach-Satelliten)",
    voiceList: ["„Ich habe den Müll rausgebracht“", "„Lucas hat den Tisch gedeckt“", "„Was muss ich noch machen?“", "„Wie viele Sterne hat Osmo?“"],
    starsTitle: "Bonus oder Abzug für {name}",
    starsCustom: "Eigener Grund",
    starsAmount: "Sterne",
    starsGive: "Buchen",
    starsLog: "Bonus und Abzug",
    starsHint: "Abzug geht nie unter null und kostet kein Level.",
    presets: "Schnellknöpfe für Bonus und Abzug",
    presetAdd: "Hinzufügen",
    presetName: "Name",
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
    pauseTitle: "Ferien-Pause",
    pauseHint: "In den Ferien ist nichts fällig, nichts wird gesperrt und Serien reißen nicht. Danach geht es normal weiter.",
    pauseFrom: "Von",
    pauseUntil: "Bis einschließlich",
    pauseStart: "🏖️ Ferien starten",
    pauseEnd: "Ferien beenden",
    pauseActive: "🏖️ Ferien! Bis {date} ist nichts zu tun.",
    pausePlanned: "🏖️ Ferien geplant: {from} bis {date}",
    weekdays: "Nur an diesen Tagen (leer = jeden Tag)",
    dayShort: ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"],
    schoolDays: "Mo–Fr",
    icon: "Symbol (für den Bilder-Modus)",
    pictureOn: "🖼️ Bilder-Modus",
    pictureOff: "🔤 Text-Modus",
    outdoor: "🌦️ Draußen: bei Regen einen Tag später",
    outdoorShort: "🌦️ draußen",
    rainWait: "🌧️ wegen Regen verschoben",
    rainBanner: "🌧️ Es regnet. Draußen-Aufgaben warten auf trockenes Wetter.",
    weekTitle: "📊 Diese Woche",
    weekRow: "{done} erledigt · {missed} verpasst",
    weekBest: "Am fleißigsten",
    weekEmpty: "Diese Woche ist noch nichts passiert.",
    sendReport: "Bericht jetzt aufs Handy",
    settings: "⚙️ Einstellungen: Wetter, Wochenbericht, Schnellknöpfe",
    weatherEntity: "Wetter für Draußen-Aufgaben",
    weatherNone: "aus",
    weatherNow: "gerade: {state}",
    reportDay: "Wochenbericht an Eltern",
    reportOff: "aus",
    reportHour: "Uhrzeit",
    readAloud: "Vorlesen",
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
    starsBtn: "⭐ Bonus or deduction",
    moreActions: "More for {name}",
    greet: ["Good morning", "Hello", "Good evening"],
    ckOpen: "chores open",
    ckWaiting: "waiting for you",
    ckKidsDone: "kids done",
    ckStars: "stars today",
    ckWaitingTitle: "📬 Waiting for you",
    wzHello: "Welcome to Sternchenplan!",
    wzHelloText: "Your family plan is ready in a minute. Four quick questions, and you can change everything later.",
    wzStart: "Let’s go",
    wzSkip: "I’ll set it up myself",
    wzNext: "Next",
    wzBack: "Back",
    wzKids: "Who’s joining?",
    wzKidsText: "With their age I can suggest fitting chores. Each child can pick their look right away.",
    wzNoKids: "No children yet. Add them under Settings → Devices & services → Sternchenplan → Configure → Add member.",
    wzAge: "Age",
    wzAgeNone: "–",
    wzChores: "Which chores fit your family?",
    wzChoresText: "Shared chores rotate, personal ones go to each child. Tap to leave one out.",
    wzShared: "Shared, rotating",
    wzOwn: "For each child",
    wzRewards: "What do the kids save up for?",
    wzRewardsText: "Kids trade stars for rewards. You confirm every redemption.",
    wzPhotos: "Proof photos",
    wzPhotosText: "Some chores need a photo as proof. Only parents see it. What happens afterwards?",
    wzPhotoDelete: "Delete after my decision",
    wzPhotoDeleteSub: "Recommended. Nothing stays stored.",
    wzPhotoKeep: "Keep",
    wzPhotoKeepSub: "Photos stay in Home Assistant until you delete them.",
    wzFinish: "✨ Create everything",
    wzWorking: "Creating everything …",
    wzDone: "Done! Your plan is ready.",
    wzDoneText: "{n} chores and {r} rewards created.",
    wzTips: ["Kids open “Sternchenplan” in the Home Assistant app.", "Add more chores under “Chores”, with templates by age.", "The ❓ button explains every section."],
    wzGo: "Go to the plan",
    wzStep: "Step {n} of 4",
    themeTitle: "🎨 My look",
    themeParent: "Look",
    themeNames: { "": "Clear", space: "Space", jungle: "Jungle", ocean: "Ocean", candy: "Candy", elegant: "Elegant" },
    allDoneKid: "All done for today!",
    allDoneKidSub: "Great job. See you tomorrow.",
    nfc: "📱 NFC tag",
    moreOptions: "More options (approval, photo, days, routine, NFC, house …)",
    starterTitle: "✨ Ready in one minute",
    starterText: "I suggest chores that fit each child's age. Shared chores rotate, personal ones go to each child. You can change everything later.",
    starterChores: "Chores",
    starterRewards: "Rewards",
    starterGo: "✨ Create all",
    starterLater: "No thanks, I'll do it myself",
    starterDone: "Done! {n} chores and {r} rewards created.",
    starterNoKids: "Add the children first (Settings → Devices & services → Sternchenplan → Configure).",
    shared: "rotating: {names}",
    help: "❓ Help",
    helpTabs: {
      today: "What each child still has to do today. Use “± Stars” for bonus or deductions; the weekly summary is at the bottom.",
      approve: "Confirm reported chores and rewards here, or directly in the push notification on your phone.",
      chores: "Create chores here, fastest via “Templates”. The basics are usually enough; everything else is under “More options”.",
      rewards: "Rewards children redeem with stars. Small rewards (10–20 stars) motivate most.",
      money: "Optional: exchange stars for pocket money and manage weekly allowance.",
      away: "Enter holidays (everything pauses) or mark a child as away, e.g. sick or at a sleepover.",
    },
    house: "🏠 The house checks itself",
    houseHint: "No automation needed: a device or sensor checks the chore off or tells the child it's their turn.",
    houseDone: "Done when",
    houseStart: "Your turn when",
    houseEntity: "Device or sensor",
    houseState: "State",
    houseNow: "now: {state}",
    houseExamples: "Examples: robot vacuum “docked” → vacuuming done. Dishwasher “off” → “your turn: empty it”.",
    nfcHint: "Stick an NFC tag e.g. on the bin. Whoever taps it with their phone (Home Assistant app) has done the chore.",
    nfcLearn: "Learn tag",
    nfcWaiting: "Now tap the tag with your phone (2 minutes) …",
    nfcLinked: "✓ Tag linked",
    nfcRemove: "remove",
    nfcSaveFirst: "Save first, then learn the tag.",
    voiceTitle: "🎙️ Voice commands (Home Assistant Assist)",
    voiceList: ["“I did the dishes”", "“Lucas did the trash”", "“What do I still have to do?”", "“How many stars does Osmo have?”"],
    starsTitle: "Bonus or deduction for {name}",
    starsCustom: "Own reason",
    starsAmount: "Stars",
    starsGive: "Book",
    starsLog: "Bonus and deductions",
    starsHint: "A deduction never goes below zero and never costs a level.",
    presets: "Quick buttons for bonus and deduction",
    presetAdd: "Add",
    presetName: "Name",
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
    pauseTitle: "Holiday pause",
    pauseHint: "During holidays nothing is due, nothing gets locked and streaks don't break. Afterwards everything continues as usual.",
    pauseFrom: "From",
    pauseUntil: "Until (inclusive)",
    pauseStart: "🏖️ Start holidays",
    pauseEnd: "End holidays",
    pauseActive: "🏖️ Holidays! Nothing to do until {date}.",
    pausePlanned: "🏖️ Holidays planned: {from} to {date}",
    weekdays: "Only on these days (empty = every day)",
    dayShort: ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"],
    schoolDays: "Mon–Fri",
    icon: "Symbol (for picture mode)",
    pictureOn: "🖼️ Picture mode",
    pictureOff: "🔤 Text mode",
    outdoor: "🌦️ Outdoors: one day later if it rains",
    outdoorShort: "🌦️ outdoors",
    rainWait: "🌧️ moved because of rain",
    rainBanner: "🌧️ It's raining. Outdoor chores wait for dry weather.",
    weekTitle: "📊 This week",
    weekRow: "{done} done · {missed} missed",
    weekBest: "Hardest worker",
    weekEmpty: "Nothing has happened this week yet.",
    sendReport: "Send report to my phone",
    settings: "⚙️ Settings: weather, weekly report, quick buttons",
    weatherEntity: "Weather for outdoor chores",
    weatherNone: "off",
    weatherNow: "now: {state}",
    reportDay: "Weekly report to parents",
    reportOff: "off",
    reportHour: "Time",
    readAloud: "Read aloud",
    moneyHint: "The money isn't really kept here. Sternchenplan only keeps the account. You pay out yourselves, in cash or by transfer.",
  },
};

const esc = (value) =>
  String(value ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);

// Datumsformate einmal anlegen statt bei jeder Aufgabe neu (spürbar auf alten Tablets).
const FORMATS = new Map();
const fmt = (locale, opts, date) => {
  const key = locale + JSON.stringify(opts);
  if (!FORMATS.has(key)) FORMATS.set(key, new Intl.DateTimeFormat(locale, opts));
  return FORMATS.get(key).format(date);
};

// Neue Klappboxen merken sich, wie die Karte sie angelegt hat (auf oder zu).
const fresh = (node) => {
  if (node.nodeType !== 1) return node;
  for (const d of [node, ...node.querySelectorAll("details")]) {
    if (d.nodeName === "DETAILS") d._tplOpen = d.hasAttribute("open");
  }
  return node;
};

const morphChildren = (from, to) => {
  const a = [...from.childNodes];
  const b = [...to.childNodes];
  b.forEach((node, i) => (i < a.length ? morph(a[i], node) : from.appendChild(fresh(node))));
  for (let i = b.length; i < a.length; i++) a[i].remove();
};

// Neuen Stand in die bestehende Ansicht einarbeiten, statt alles neu zu bauen.
// So bleiben offene Menüs, das Feld mit dem Cursor und laufende Animationen
// erhalten, wenn jemand anderes gerade etwas abhakt, und der Browser muss nur
// das Geänderte neu zeichnen.
const morph = (from, to) => {
  if (from.nodeType !== to.nodeType || from.nodeName !== to.nodeName) {
    from.replaceWith(fresh(to));
    return;
  }
  if (from.nodeType !== 1) {
    if (from.nodeValue !== to.nodeValue) from.nodeValue = to.nodeValue;
    return;
  }
  for (const { name } of [...from.attributes]) {
    if (!to.hasAttribute(name) && name !== "open") from.removeAttribute(name);
  }
  for (const { name, value } of to.attributes) {
    if (name !== "open" && from.getAttribute(name) !== value) from.setAttribute(name, value);
  }
  if (from.nodeName === "DETAILS") {
    // Auf/zu nur übernehmen, wenn die Karte es selbst ändert, nicht bei jedem Stand
    const open = to.hasAttribute("open");
    if (from._tplOpen !== open) from.open = open;
    from._tplOpen = open;
  }
  const focused = from === from.getRootNode().activeElement;
  if (from.nodeName === "INPUT" || from.nodeName === "TEXTAREA") {
    if (!focused) {
      if (from.type === "checkbox" || from.type === "radio") from.checked = to.hasAttribute("checked");
      else if (from.type !== "file") from.value = from.nodeName === "TEXTAREA" ? to.value : to.getAttribute("value") ?? "";
    }
    if (from.nodeName === "TEXTAREA") return;
  }
  morphChildren(from, to);
  if (from.nodeName === "SELECT" && !focused) {
    const pick = [...to.options].find((o) => o.hasAttribute("selected")) || to.options[0];
    if (pick) from.value = pick.value;
  }
};

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
    this._pauseForm = { from: "", until: "" };
    this._starsOpen = null;
    this._starsForm = { stars: "", reason: "" };
    this._presetForm = { name: "", stars: "" };
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
    // Offene „⋯“-Menüs schließen, sobald woanders getippt wird.
    const keep = ev.target.closest("details.kid-menu");
    this.shadowRoot.querySelectorAll("details.kid-menu[open]").forEach((d) => d !== keep && d.removeAttribute("open"));
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
      case "say":
        this._say(el.dataset.text);
        break;
      case "picture":
        this._call("set_picture_mode", { member: id, enabled: !!el.dataset.on });
        break;
      case "pause-start": {
        const f = this._pauseForm;
        if (!f.until) break;
        const end = new Date(`${f.until}T00:00`);
        end.setDate(end.getDate() + 1); // „bis einschließlich“
        const data = { until: end.toISOString() };
        if (f.from) data.start = new Date(`${f.from}T00:00`).toISOString();
        this._call("set_pause", data);
        this._pauseForm = { from: "", until: "" };
    this._starsOpen = null;
    this._starsForm = { stars: "", reason: "" };
    this._presetForm = { name: "", stars: "" };
        break;
      }
      case "pause-end":
        this._call("end_pause", {});
        break;
      case "stars-open":
        this._starsOpen = this._starsOpen === id ? null : id;
        this._starsForm = { stars: "", reason: "" };
        this._render();
        break;
      case "stars-give": {
        const stars = el.dataset.stars ? Number(el.dataset.stars) : parseInt(this._starsForm.stars, 10);
        const reason = el.dataset.stars ? el.dataset.reason : this._starsForm.reason.trim();
        if (!stars) break;
        this._starsForm = { stars: "", reason: "" };
        this._call("give_stars", { member: id, stars, reason });
        if (stars > 0) this._celebrate(el);
        break;
      }
      case "preset-add": {
        const stars = parseInt(this._presetForm.stars, 10);
        const name = this._presetForm.name.trim();
        if (!stars || !name) break;
        this._presetForm = { name: "", stars: "" };
        this._call("add_preset", { name, stars });
        break;
      }
      case "help":
        this._help = !this._help;
        this._render();
        break;
      case "wz-step":
        this._wz.step = Math.max(0, Number(id));
        this._render();
        this.scrollIntoView?.({ block: "start", behavior: "smooth" });
        break;
      case "wz-chore":
      case "wz-reward": {
        const set = action === "wz-chore" ? this._wz.offChores : this._wz.offRewards;
        if (set.has(id)) set.delete(id);
        else set.add(id);
        this._render();
        break;
      }
      case "wz-photo":
        this._wz.photo = !!id;
        this._render();
        break;
      case "wz-finish":
        this._finishWelcome();
        break;
      case "wz-skip":
      case "wz-close":
        try {
          localStorage.setItem("sternchenplan-welcome-done", "1");
        } catch (e) {
          /* egal */
        }
        if (action === "wz-skip") {
          try {
            localStorage.removeItem("sternchenplan-starter-hidden");
          } catch (e) {
            /* egal */
          }
        }
        this._wz = null;
        this._tab = "today";
        this._render();
        break;
      case "theme-toggle":
        this._themeOpen = !this._themeOpen;
        this._render();
        break;
      case "theme": {
        // Sofort umschalten, der Server bestätigt gleich danach.
        const who = this._member(id);
        if (who) who.theme = el.dataset.theme;
        if (!this._wz) this._themeOpen = true;
        this._render();
        this._call("set_theme", { member: id, theme: el.dataset.theme });
        break;
      }
      case "starter-go":
        el.disabled = true;
        this._runStarter();
        break;
      case "starter-hide":
        try {
          localStorage.setItem("sternchenplan-starter-hidden", "1");
        } catch (e) {
          /* egal */
        }
        this._render();
        break;
      case "tag-learn":
        this._call("learn_tag", { chore_id: id });
        break;
      case "tag-clear":
        this._call("clear_tag", { chore_id: id });
        break;
      case "preset-del":
        this._call("delete_preset", { preset_id: id });
        break;
      case "send-report":
        this._call("send_report", {});
        this._notify(this._t("sendReport") + " ✓");
        break;
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
    if (el.dataset?.wzAge) {
      const who = this._member(el.dataset.wzAge);
      const age = el.value === "" ? null : Number(el.value);
      if (who) who.age = age;
      this._call("set_age", { member: el.dataset.wzAge, age });
      return;
    }
    const field = el.dataset?.field;
    if (!field) return;
    if (field.startsWith("away.")) {
      const [, memberId, key] = field.split(".");
      this._awayForm[memberId] = { ...(this._awayForm[memberId] || {}), [key]: el.value };
      return;
    }
    if (field.startsWith("stars.")) {
      this._starsForm[field.slice(6)] = el.value;
      return;
    }
    if (field.startsWith("preset.")) {
      this._presetForm[field.slice(7)] = el.value;
      return;
    }
    if (field.startsWith("set.")) {
      if (ev.type !== "change") return;
      const call = (service, data) =>
        this._hass.callService("sternchenplan", service, data).catch((err) => this._notify(err.message));
      if (field === "set.weather") call("set_weather", { entity: el.value });
      else {
        const r = { ...(this._data.report || { day: 6, hour: 18 }) };
        r[field.slice(4)] = parseInt(el.value, 10);
        call("set_report", r);
      }
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
    if (field === "weekday") {
      const set = new Set(this._form.weekdays);
      el.checked ? set.add(Number(el.value)) : set.delete(Number(el.value));
      this._form.weekdays = [...set].sort();
      return;
    }
    if (field.startsWith("pause.")) {
      this._pauseForm[field.slice(6)] = el.value;
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
      // Nach Gerätewahl Zustandsvorschläge und „jetzt: …“ zeigen
      if (field.endsWith("_entity") && ev.type === "change") this._render();
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
    return { name: "", assignees: [], recurrence: "daily", due: "", points: 1, rotation: false, approval: false, photo: false, minAge: 0, steps: "", weekdays: [], icon: "", outdoor: false, done_entity: "", done_state: "", start_entity: "", start_state: "", editId: null };
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
      weekdays: [...(c.weekdays || [])],
      icon: c.icon || "",
      outdoor: !!c.outdoor,
      done_entity: c.done_entity || "",
      done_state: c.done_state || "",
      start_entity: c.start_entity || "",
      start_state: c.start_state || "",
      editId: c.id,
    };
    this._render();
    this.shadowRoot.querySelector("details.form")?.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  _dayList(days) {
    if (days.join() === "0,1,2,3,4") return this._t("schoolDays");
    const short = this._t("dayShort");
    return days.map((d) => short[d]).join(", ");
  }

  _date(iso) {
    return new Date(iso).toLocaleDateString(this._locale(), { day: "numeric", month: "numeric" });
  }

  _pauseBanner() {
    const p = this._data.pause;
    if (!p?.active) return "";
    // Das Ende ist exklusiv gespeichert: als „bis einschließlich“ den Tag davor zeigen.
    const last = new Date(new Date(p.until).getTime() - 1);
    return `<div class="pause-banner">${esc(this._t("pauseActive", { date: this._date(last.toISOString()) }))}</div>`;
  }

  _weatherText(entity, state) {
    const obj = this._hass?.states?.[entity];
    try {
      if (obj && this._hass.formatEntityState) return this._hass.formatEntityState(obj);
    } catch (e) {
      /* ältere HA-Versionen: Rohwert zeigen */
    }
    return state;
  }

  // Bonus oder Abzug: Schnellknöpfe plus eigener Grund.
  _renderStarsPanel(m) {
    const f = this._starsForm;
    const chips = (this._data.presets || [])
      .map(
        (p) => `<button class="star-chip ${p.stars > 0 ? "plus" : "minus"}" data-action="stars-give" data-id="${esc(m.id)}" data-stars="${p.stars}" data-reason="${esc(p.name)}">
          ${p.stars > 0 ? "+" : "−"}${Math.abs(p.stars)} ⭐ ${esc(p.name)}</button>`,
      )
      .join("");
    return `
      <div class="stars-panel">
        <div class="small"><strong>${esc(this._t("starsTitle", { name: m.name }))}</strong></div>
        <div class="star-chips">${chips}</div>
        <div class="stars-custom">
          <input type="number" min="-100" max="100" step="1" placeholder="±" aria-label="${this._t("starsAmount")}" data-field="stars.stars" value="${esc(f.stars)}">
          <input placeholder="${this._t("starsCustom")}" maxlength="60" aria-label="${this._t("starsCustom")}" data-field="stars.reason" value="${esc(f.reason)}">
          <button class="primary" data-action="stars-give" data-id="${esc(m.id)}">${this._t("starsGive")}</button>
        </div>
        <p class="muted small">${this._t("starsHint")}</p>
        ${this._starLog(m, 3)}
      </div>`;
  }

  _starLog(member, limit = 5) {
    const log = (member.star_log || []).slice(0, limit);
    if (!log.length) return "";
    return `<ul class="ledger">${log
      .map(
        (e) => `<li><span>${esc(e.reason || (e.stars > 0 ? "Bonus" : "−"))}<span class="muted small"> · ${new Date(e.at).toLocaleDateString(this._locale())}</span></span>
          <b class="${e.stars < 0 ? "minus" : "plus"}">${e.stars > 0 ? "+" : ""}${e.stars} ⭐</b></li>`,
      )
      .join("")}</ul>`;
  }

  _renderChildStarLog(member) {
    const list = this._starLog(member, 5);
    if (!list) return "";
    return `<section class="star-log"><div class="section-title">⭐ ${this._t("starsLog")}</div>${list}</section>`;
  }

  _renderPresetAdmin() {
    const f = this._presetForm;
    const list = (this._data.presets || [])
      .map(
        (p) => `<span class="star-chip ${p.stars > 0 ? "plus" : "minus"}">${p.stars > 0 ? "+" : "−"}${Math.abs(p.stars)} ${esc(p.name)}
          <button class="x" data-action="preset-del" data-id="${esc(p.id)}" aria-label="${this._t("delete")}">×</button></span>`,
      )
      .join("");
    return `
      <div class="preset-admin">
        <div class="small"><strong>${this._t("presets")}</strong></div>
        <div class="star-chips">${list}</div>
        <div class="stars-custom">
          <input type="number" min="-100" max="100" placeholder="±" aria-label="${this._t("starsAmount")}" data-field="preset.stars" value="${esc(f.stars)}">
          <input placeholder="${this._t("presetName")}" maxlength="40" aria-label="${this._t("presetName")}" data-field="preset.name" value="${esc(f.name)}">
          <button class="link" data-action="preset-add">+ ${this._t("presetAdd")}</button>
        </div>
      </div>`;
  }

  _hasAdvanced(f) {
    return !!(f.approval || f.photo || f.outdoor || f.weekdays.length || f.icon || f.steps || Number(f.minAge) ||
      f.done_entity || f.start_entity || f.editId);
  }

  // Nächster Zeitpunkt mit dieser Uhrzeit (heute oder morgen).
  _nextAt(time) {
    const d = new Date();
    const [h, m] = time.split(":").map(Number);
    d.setHours(h, m, 0, 0);
    if (d < new Date()) d.setDate(d.getDate() + 1);
    return d;
  }

  // Startpaket: gemeinsame Aufgaben reihum für alle, die alt genug sind, eigene je Kind.
  _starterPlan() {
    const kids = this._children();
    const lang = this._lang();
    const SHARED = ["Tisch decken", "Spülmaschine ausräumen", "Müll rausbringen", "Staubsaugen"];
    const OWN = ["Spielzeug aufräumen", "Bett machen", "Zimmer aufräumen"];
    const byName = (n) => TEMPLATES.find((t) => t.name.de === n);
    const fits = (t, k) => k.age == null || k.age >= t.age;
    const chores = [];
    for (const n of SHARED) {
      const t = byName(n);
      const who = kids.filter((k) => fits(t, k));
      if (t && who.length) chores.push({ t, who, rotation: who.length > 1 });
    }
    for (const k of kids) {
      // Kleine räumen Spielzeug auf, Größere ihr Zimmer
      const own = OWN.map(byName).filter((t) => t && fits(t, k));
      const pick = own.filter((t) => !(t.name.de === "Spielzeug aufräumen" && k.age >= 8));
      for (const t of pick) chores.push({ t, who: [k], rotation: false });
    }
    const rewards = lang === "de"
      ? [["30 Minuten extra Bildschirmzeit", 15], ["Länger aufbleiben", 20], ["Filmabend aussuchen", 40], ["Ausflug aussuchen", 100]]
      : [["30 extra minutes screen time", 15], ["Stay up later", 20], ["Pick the movie night", 40], ["Pick a day trip", 100]];
    return { chores, rewards: this._data.rewards.length ? [] : rewards };
  }

  // -- Willkommens-Assistent -------------------------------------------------

  _welcomeActive() {
    const d = this._data;
    if (this._wz?.step === 5) return true; // „Fertig“ noch zeigen, auch wenn jetzt Aufgaben da sind
    if (this._config.readonly || !d.is_manager || d.chores.length || d.rewards.length) return false;
    try {
      if (localStorage.getItem("sternchenplan-welcome-done")) return false;
    } catch (e) {
      /* ohne Speicher einfach zeigen */
    }
    return true;
  }

  _wzKey(c) {
    return `${c.t.name.de}|${c.who.map((k) => k.id).join(",")}`;
  }

  _wzPlan() {
    const wz = this._wz;
    const plan = this._starterPlan();
    return {
      chores: plan.chores.filter((c) => !wz.offChores.has(this._wzKey(c))),
      rewards: plan.rewards.filter(([n]) => !wz.offRewards.has(n)),
      all: plan,
    };
  }

  _renderWelcome() {
    if (!this._wz) this._wz = { step: 0, offChores: new Set(), offRewards: new Set(), photo: null };
    const wz = this._wz;
    const lang = this._lang();
    const kids = this._children();
    const dots = wz.step >= 1 && wz.step <= 4
      ? `<div class="wz-top"><span class="muted small">${this._t("wzStep", { n: wz.step })}</span><div class="wz-dots">${[1, 2, 3, 4]
          .map((i) => `<i class="${i <= wz.step ? "on" : ""}"></i>`).join("")}</div></div>`
      : "";
    const nav = (next, label = this._t("wzNext")) => `
      <div class="wz-nav">
        <button class="link" data-action="wz-step" data-id="${wz.step - 1}">← ${this._t("wzBack")}</button>
        <button class="primary big" data-action="${next === "finish" ? "wz-finish" : "wz-step"}" data-id="${next}">${label}</button>
      </div>`;
    let body = "";
    if (wz.step === 0) {
      body = `
        <div class="wz-hero">
          <div class="wz-star" aria-hidden="true">⭐</div>
          <h2>${this._t("wzHello")}</h2>
          <p>${this._t("wzHelloText")}</p>
          <div class="wz-kids-row">${kids.map((k) => this._avatar(k, 52)).join("")}</div>
          <button class="primary big" data-action="wz-step" data-id="1">${this._t("wzStart")} →</button>
          <button class="link" data-action="wz-skip">${this._t("wzSkip")}</button>
        </div>`;
    } else if (wz.step === 1) {
      const names = this._t("themeNames");
      const cards = kids.length
        ? kids.map((k) => `
            <div class="wz-kid" style="--kid:${this._color(k.id)}">
              <div class="wz-kid-head">${this._avatar(k, 48)}<strong>${esc(k.name)}</strong>
                <label class="wz-age">${this._t("wzAge")}
                  <select data-wz-age="${esc(k.id)}"><option value="">${this._t("wzAgeNone")}</option>${Array.from({ length: 16 }, (_, i) => i + 3)
                    .map((a) => `<option value="${a}" ${k.age === a ? "selected" : ""}>${a}</option>`).join("")}</select></label>
              </div>
              <div class="muted small wz-caption">${this._t("themeParent")}</div>
              <div class="wz-themes">${THEMES.filter((t) => t.id !== "elegant")
                .map((t) => `<button class="wz-theme ${(k.theme || "") === t.id ? "on" : ""}" data-action="theme" data-id="${esc(k.id)}" data-theme="${t.id}" title="${esc(names[t.id])}" aria-label="${esc(names[t.id])}"><span class="sw sw-${t.id || "clear"}">${t.emoji}</span></button>`)
                .join("")}</div>
            </div>`).join("")
        : `<p class="help-tip">${this._t("wzNoKids")}</p>`;
      body = `<h2>${this._t("wzKids")}</h2><p class="muted">${this._t("wzKidsText")}</p><div class="wz-kid-list">${cards}</div>${nav(2)}`;
    } else if (wz.step === 2) {
      const plan = this._starterPlan();
      const item = (c) => {
        const off = wz.offChores.has(this._wzKey(c));
        return `<button class="wz-pick ${off ? "off" : ""}" data-action="wz-chore" data-id="${esc(this._wzKey(c))}" aria-pressed="${!off}">
          <span class="wz-pick-icon">${esc(c.t.emoji)}</span><span class="wz-pick-main"><strong>${esc(c.t.name[lang])}</strong>
          <span class="muted small">${esc(c.who.map((k) => k.name).join(", "))} · +${c.t.points} ⭐</span></span><span class="wz-check">${off ? "" : "✓"}</span></button>`;
      };
      const shared = plan.chores.filter((c) => c.rotation || c.who.length > 1 || ["Tisch decken", "Spülmaschine ausräumen", "Müll rausbringen", "Staubsaugen"].includes(c.t.name.de));
      const own = plan.chores.filter((c) => !shared.includes(c));
      body = `<h2>${this._t("wzChores")}</h2><p class="muted">${this._t("wzChoresText")}</p>
        ${shared.length ? `<div class="wz-group">${this._t("wzShared")}</div><div class="wz-picks">${shared.map(item).join("")}</div>` : ""}
        ${own.length ? `<div class="wz-group">${this._t("wzOwn")}</div><div class="wz-picks">${own.map(item).join("")}</div>` : ""}
        ${nav(3)}`;
    } else if (wz.step === 3) {
      const plan = this._starterPlan();
      body = `<h2>${this._t("wzRewards")}</h2><p class="muted">${this._t("wzRewardsText")}</p>
        <div class="wz-rewards">${plan.rewards.map(([n, c]) => {
          const off = wz.offRewards.has(n);
          return `<button class="wz-reward ${off ? "off" : ""}" data-action="wz-reward" data-id="${esc(n)}" aria-pressed="${!off}">
            <span class="wz-reward-emoji">${this._rewardEmoji(n)}</span><strong>${esc(n)}</strong><span class="muted small">⭐ ${c}</span><span class="wz-check">${off ? "" : "✓"}</span></button>`;
        }).join("")}</div>${nav(4)}`;
    } else if (wz.step === 4) {
      const del = wz.photo ?? this._data.photo_delete ?? true;
      const opt = (val, emoji, title, sub) => `<button class="wz-choice ${del === val ? "on" : ""}" data-action="wz-photo" data-id="${val ? "1" : ""}">
        <span class="wz-choice-emoji">${emoji}</span><span><strong>${title}</strong><span class="muted small">${sub}</span></span></button>`;
      body = `<h2>${this._t("wzPhotos")}</h2><p class="muted">${this._t("wzPhotosText")}</p>
        <div class="wz-choices">${opt(true, "🗑️", this._t("wzPhotoDelete"), this._t("wzPhotoDeleteSub"))}${opt(false, "🗂️", this._t("wzPhotoKeep"), this._t("wzPhotoKeepSub"))}</div>
        ${nav("finish", wz.busy ? this._t("wzWorking") : this._t("wzFinish"))}`;
    } else {
      body = `
        <div class="wz-hero">
          <div class="wz-star" aria-hidden="true">🎉</div>
          <h2>${this._t("wzDone")}</h2>
          <p>${esc(this._t("wzDoneText", { n: wz.made?.n ?? 0, r: wz.made?.r ?? 0 }))}</p>
          <ul class="wz-tips">${this._t("wzTips").map((t) => `<li>${esc(t)}</li>`).join("")}</ul>
          <button class="primary big" data-action="wz-close">${this._t("wzGo")} →</button>
        </div>`;
    }
    return `<section class="wizard">${dots}${body}</section>`;
  }

  async _finishWelcome() {
    const wz = this._wz;
    if (wz.busy) return;
    wz.busy = true;
    this._render();
    const { chores, rewards } = this._wzPlan();
    try {
      if (wz.photo !== null && wz.photo !== this._data.photo_delete) {
        await this._hass.callService("sternchenplan", "set_photo_privacy", { delete: wz.photo });
      }
      await this._runStarter({ chores, rewards }, true);
      wz.made = { n: chores.length, r: rewards.length };
      wz.step = 5;
    } finally {
      wz.busy = false;
      this._render();
    }
  }

  _renderStarter() {
    if (this._config.readonly || this._data.chores.length) return "";
    try {
      if (localStorage.getItem("sternchenplan-starter-hidden")) return "";
    } catch (e) {
      /* ohne Speicher einfach zeigen */
    }
    const kids = this._children();
    if (!kids.length) return `<section class="starter"><strong>${this._t("starterTitle")}</strong><p>${this._t("starterNoKids")}</p></section>`;
    const lang = this._lang();
    const plan = this._starterPlan();
    const names = (who) => who.map((k) => k.name).join(", ");
    return `
      <section class="starter">
        <div class="starter-title">${this._t("starterTitle")}</div>
        <p class="muted">${this._t("starterText")}</p>
        <div class="starter-cols">
          <div><div class="small"><strong>${this._t("starterChores")}</strong></div><ul>${plan.chores
            .map((c) => `<li>${esc(c.t.emoji)} ${esc(c.t.name[lang])} <span class="muted small">· ${esc(c.rotation ? this._t("shared", { names: names(c.who) }) : names(c.who))}</span></li>`)
            .join("")}</ul></div>
          ${plan.rewards.length ? `<div><div class="small"><strong>${this._t("starterRewards")}</strong></div><ul>${plan.rewards
            .map(([n, c]) => `<li>🎁 ${esc(n)} <span class="muted small">· ⭐ ${c}</span></li>`)
            .join("")}</ul></div>` : ""}
        </div>
        <div class="starter-actions">
          <button class="primary big" data-action="starter-go">${this._t("starterGo")}</button>
          <button class="link" data-action="starter-hide">${this._t("starterLater")}</button>
        </div>
      </section>`;
  }

  async _runStarter(plan = this._starterPlan(), quiet = false) {
    const lang = this._lang();
    const call = (service, data) => this._hass.callService("sternchenplan", service, data);
    try {
      for (const c of plan.chores) {
        await call("create_chore", {
          name: c.t.name[lang], assignees: c.who.map((k) => k.id), points: c.t.points, recurrence: c.t.rec,
          due: this._nextAt(c.t.time).toISOString(), rotation: c.rotation, requires_photo: !!c.t.photo,
          min_age: c.t.age, icon: c.t.emoji, steps: c.t.steps?.[lang] || [], outdoor: !!c.t.outdoor,
        });
      }
      for (const [name, cost] of plan.rewards) await call("create_reward", { name, cost });
      if (!quiet) this._notify(this._t("starterDone", { n: plan.chores.length, r: plan.rewards.length }));
    } catch (err) {
      this._notify(err.message);
    }
  }

  _helpTip() {
    if (!this._help) return "";
    return `<p class="help-tip">💡 ${esc(this._t("helpTabs")[this._tab] || "")}</p>`;
  }

  _houseData(f) {
    return { done_entity: f.done_entity || "", done_state: f.done_state || "", start_entity: f.start_entity || "", start_state: f.start_state || "" };
  }

  // Gerät + Zustand wählen. Die Liste schlägt passende Geräte und Zustände vor.
  _houseBlock(f) {
    const states = this._hass?.states || {};
    const useful = /^(binary_sensor|switch|vacuum|input_boolean|cover|lock|sensor|lawn_mower|media_player|light|fan|valve)\./;
    const ids = Object.keys(states).filter((id) => useful.test(id)).sort();
    const options = ids
      .map((id) => `<option value="${esc(id)}">${esc(states[id].attributes?.friendly_name || id)}</option>`)
      .join("");
    const row = (kind, label) => {
      const entity = f[`${kind}_entity`];
      const now = entity && states[entity] ? states[entity].state : "";
      const guesses = [...new Set([now, ...(states[entity]?.attributes?.options || []), "on", "off", "docked", "closed", "open", "idle"].filter(Boolean))];
      return `
        <div class="house-row">
          <span class="house-label">${label}</span>
          <input list="house-entities" placeholder="${this._t("houseEntity")}" aria-label="${this._t("houseEntity")}" data-field="${kind}_entity" value="${esc(entity)}">
          <input list="house-${kind}-states" placeholder="${this._t("houseState")}" aria-label="${this._t("houseState")}" data-field="${kind}_state" value="${esc(f[`${kind}_state`])}" class="house-state">
          <datalist id="house-${kind}-states">${guesses.map((g) => `<option value="${esc(g)}"></option>`).join("")}</datalist>
          ${now ? `<span class="muted small">${esc(this._t("houseNow", { state: now }))}</span>` : ""}
        </div>`;
    };
    const open = f.done_entity || f.start_entity;
    return `
      <details class="house-box" ${open ? "open" : ""}>
        <summary><strong>${this._t("house")}</strong></summary>
        <div class="muted small">${this._t("houseHint")}</div>
        <datalist id="house-entities">${options}</datalist>
        ${row("done", this._t("houseDone"))}
        ${row("start", this._t("houseStart"))}
        <div class="muted small">${this._t("houseExamples")}</div>
      </details>`;
  }

  _nfcBlock(f) {
    const chore = f.editId && this._data.chores.find((c) => c.id === f.editId);
    let body;
    if (!chore) body = `<span class="muted small">${this._t("nfcSaveFirst")}</span>`;
    else if (this._data.learning_tag === chore.id) body = `<span class="chip wait">${this._t("nfcWaiting")}</span>`;
    else if (chore.has_tag)
      body = `<span class="chip">${this._t("nfcLinked")}</span> <button class="link bad" data-action="tag-clear" data-id="${esc(chore.id)}">${this._t("nfcRemove")}</button>`;
    else body = `<button class="link" data-action="tag-learn" data-id="${esc(chore.id)}">${this._t("nfcLearn")}</button>`;
    return `<div class="nfc-box"><div class="small"><strong>${this._t("nfc")}</strong></div>
      <div class="muted small">${this._t("nfcHint")}</div><div>${body}</div></div>`;
  }

  _rainBanner() {
    const w = this._data.weather;
    if (!w?.bad || !this._data.chores.some((c) => c.outdoor)) return "";
    return `<div class="pause-banner rain-banner">${this._t("rainBanner")}</div>`;
  }

  // Wochenbilanz für Eltern: erledigt gegen verpasst, wer am meisten geschafft hat.
  _renderWeek() {
    const rows = this._data.week || [];
    if (!rows.length) return "";
    const best = rows.reduce((a, b) => (b.stars > a.stars || (b.stars === a.stars && b.done > a.done) ? b : a));
    const active = rows.some((r) => r.done || r.missed);
    const list = rows
      .map((r) => {
        const m = this._member(r.member);
        if (!m) return "";
        const total = r.done + r.missed;
        const pct = total ? Math.round((r.done / total) * 100) : 0;
        const crown = active && best.done && r.member === best.member;
        return `
          <li class="week-row" style="--kid:${this._color(m.id)}">
            ${this._avatar(m, 32)}
            <div class="week-main">
              <div class="week-head"><strong>${esc(m.name)}</strong>${crown ? ` <span class="chip best">🏆 ${this._t("weekBest")}</span>` : ""}
                <span class="week-stars">⭐ ${r.stars}</span></div>
              <div class="week-bar ${total ? "" : "nil"}" role="img" aria-label="${esc(this._t("weekRow", r))}"><span style="width:${pct}%"></span></div>
              <div class="muted small">${esc(this._t("weekRow", r))}${r.streak ? ` · 🔥 ${r.streak}` : ""}</div>
            </div>
          </li>`;
      })
      .join("");
    return `
      <section class="week">
        <div class="week-title"><strong>${this._t("weekTitle")}</strong>
          ${this._config.readonly ? "" : `<button class="link" data-action="send-report">${this._t("sendReport")}</button>`}</div>
        ${active ? `<ul class="week-list">${list}</ul>` : `<p class="muted small">${this._t("weekEmpty")}</p>`}
      </section>`;
  }

  // Einstellungen für Wetter und Wochenbericht, oben im Aufgaben-Reiter.
  _renderSettings() {
    const d = this._data;
    const weathers = Object.keys(this._hass?.states || {}).filter((id) => id.startsWith("weather."));
    const current = d.weather?.entity || "";
    if (current && !weathers.includes(current)) weathers.push(current);
    const r = d.report || { day: 6, hour: 18 };
    const days = this._t("days");
    const name = (id) => this._hass?.states?.[id]?.attributes?.friendly_name || id;
    return `
      <details class="form settings-box">
        <summary>${this._t("settings")}</summary>
        <div class="grid">
          <label>${this._t("weatherEntity")}<select data-field="set.weather">
            <option value="">${this._t("weatherNone")}</option>
            ${weathers.map((id) => `<option value="${esc(id)}" ${id === current ? "selected" : ""}>${esc(name(id))}</option>`).join("")}
          </select>${d.weather?.state ? `<span class="muted small">${esc(this._t("weatherNow", { state: this._weatherText(current, d.weather.state) }))}</span>` : ""}</label>
          <label>${this._t("reportDay")}<select data-field="set.day">
            <option value="-1" ${r.day === -1 ? "selected" : ""}>${this._t("reportOff")}</option>
            ${days.map((dn, i) => `<option value="${i}" ${i === r.day ? "selected" : ""}>${esc(dn)}</option>`).join("")}
          </select></label>
          <label>${this._t("reportHour")}<select data-field="set.hour" ${r.day === -1 ? "disabled" : ""}>
            ${Array.from({ length: 24 }, (_, h) => `<option value="${h}" ${h === r.hour ? "selected" : ""}>${String(h).padStart(2, "0")}:00</option>`).join("")}
          </select></label>
        </div>
        ${this._renderPresetAdmin()}
        <div class="voice-help"><div class="small"><strong>${this._t("voiceTitle")}</strong></div>
          <ul class="muted small">${this._t("voiceList").map((v) => `<li>${esc(v)}</li>`).join("")}</ul></div>
      </details>`;
  }

  _renderPause() {
    const p = this._data.pause;
    if (p) {
      const last = new Date(new Date(p.until).getTime() - 1).toISOString();
      const text = p.active ? this._t("pauseActive", { date: this._date(last) }) : this._t("pausePlanned", { from: this._date(p.from), date: this._date(last) });
      return `<div class="pause-box"><div class="pause-banner">${esc(text)}</div>
        <button class="link bad" data-action="pause-end">${this._t("pauseEnd")}</button></div>`;
    }
    const f = this._pauseForm;
    return `
      <details class="form pause-form">
        <summary>${this._t("pauseStart")}</summary>
        <p class="muted small">${this._t("pauseHint")}</p>
        <div class="grid">
          <label>${this._t("pauseFrom")}<input type="date" data-field="pause.from" value="${esc(f.from)}"></label>
          <label>${this._t("pauseUntil")}<input type="date" data-field="pause.until" value="${esc(f.until)}"></label>
        </div>
        <button class="primary" data-action="pause-start">${this._t("pauseStart")}</button>
      </details>`;
  }

  _choreIcon(chore) {
    if (chore.icon) return chore.icon;
    const n = chore.name.toLowerCase();
    for (const [words, emoji] of CHORE_EMOJI) if (words.some((w) => n.includes(w))) return emoji;
    return "⭐";
  }

  _say(text) {
    try {
      const u = new SpeechSynthesisUtterance(text);
      u.lang = this._lang() === "de" ? "de-DE" : "en-US";
      window.speechSynthesis.cancel();
      window.speechSynthesis.speak(u);
    } catch (e) {
      /* Kein Vorlesen verfügbar: einfach nichts tun. */
    }
  }

  // Bilder-Modus: große Kacheln mit Symbol, wenig Text, Vorlesen per Tipp.
  _renderPictureChild(member) {
    const chores = this._openFor(member.id);
    const color = this._color(member.id);
    const ro = this._config.readonly || member.id !== this._me();
    const tiles = chores
      .map((c) => {
        const waiting = c.state === "claimed";
        const left = (c.steps?.length || 0) - (c.steps_done?.length || 0);
        const photo = this._photoNeeded(c);
        const canTap = !ro && !waiting && !left;
        return `
          <div class="pic ${waiting ? "wait" : ""} ${c.state}">
            <button class="pic-main" ${canTap ? "" : "disabled"} data-action="claim" data-id="${esc(c.id)}" data-member="${esc(member.id)}">
              <span class="pic-icon">${esc(this._choreIcon(c))}</span>
              <span class="pic-stars">${"⭐".repeat(Math.min(c.points, 5))}</span>
              ${waiting ? `<span class="pic-state">⏳</span>` : photo ? `<span class="pic-state">📷</span>` : ""}
            </button>
            <button class="pic-say" data-action="say" data-text="${esc(c.name)}" aria-label="${this._t("readAloud")}">🔊 ${esc(c.name)}</button>
            ${c.steps?.length && !waiting ? this._steps(c, member.id, ro) : ""}
          </div>`;
      })
      .join("");
    return `
      <div class="kid picture" style="--kid:${color}">
        <div class="hero">
          ${this._avatar(member, 64)}
          <div class="hero-text"><div class="hello">${esc(member.name)}</div><div class="star big-star">⭐ ${member.points}</div></div>
          ${member.progress ? `<span class="level-badge">${member.progress.level}</span>` : ""}
        </div>
        ${this._pauseBanner()}${this._rainBanner()}
        ${chores.length ? `<div class="pic-grid">${tiles}</div>` : `<div class="done-big">🎉</div>`}
        ${this._renderChildRewards(member)}
        ${this._renderBadges(member)}
        ${this._renderChildStarLog(member)}
        ${this._renderThemePicker(member)}
      </div>`;
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
      icon: t.emoji,
      weekdays: t.school ? [0, 1, 2, 3, 4] : [],
      outdoor: !!t.outdoor,
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
    if (!f.due && f.recurrence !== "none") f.due = this._toLocalInput(this._nextAt("18:00").toISOString());
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
        weekdays: f.weekdays,
        icon: f.icon || "",
        outdoor: !!f.outdoor,
        ...this._houseData(f),
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
      weekdays: f.weekdays,
      icon: f.icon || "",
      outdoor: !!f.outdoor,
      ...this._houseData(f),
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
    if (chore.weather_shift > 0) return `<span class="chip rain">${this._t("rainWait")}</span>`;
    if (!chore.due) return `<span class="muted">${this._t("noDue")}</span>`;
    const due = new Date(chore.due);
    const now = new Date();
    const time = fmt(this._locale(), { hour: "2-digit", minute: "2-digit" }, due);
    const day = (d) => new Date(d.getFullYear(), d.getMonth(), d.getDate()).getTime();
    const diff = Math.round((day(due) - day(now)) / 86400000);
    let label;
    if (diff === 0) label = this._t("today", { time });
    else if (diff === 1) label = this._t("tomorrow", { time });
    else label = fmt(this._locale(), { weekday: "short", day: "numeric", month: "numeric" }, due) + " " + time;
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
        ${chore.state === "claimed" && chore.photo_url ? this._thumb(chore) : `<span class="task-icon" aria-hidden="true">${esc(this._choreIcon(chore))}</span>`}
        <div class="main">
          <div class="title">${esc(chore.name)}${this._photoIcon(chore)}</div>
          <div class="sub">${
            chore.state === "claimed" ? `<span class="chip wait">${this._t("waiting")}</span>` : this._dueLabel(chore)
          }${this._takenInfo(chore)}</div>
        </div>
        <span class="pts-pill">+${chore.points} ⭐</span>
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
        <li class="row task ${c.state}">
          <span class="task-icon" aria-hidden="true" style="--kid:${this._color(c.responsible[0])}">${esc(this._choreIcon(c))}</span>
          <div class="main">
            <div class="title">${esc(c.name)}${this._photoIcon(c)}</div>
            <div class="sub muted">${esc(owner)}</div>
          </div>
          <span class="pts-pill">+${pts} ⭐</span>
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

  _themeId() {
    if (!this._data) return "";
    const kid = this._shownChild();
    if (kid) return this._member(kid)?.theme || "";
    if (this._data.tablet && !this._data.is_manager) return "";
    return this._member(this._data.me)?.theme || "";
  }

  _renderThemePicker(member) {
    if (this._config.readonly) return "";
    const names = this._t("themeNames");
    const current = member.theme || "";
    const list = THEMES.filter((t) => member.role === "parent" || t.id !== "elegant");
    return `
      <details class="theme-box" ${this._themeOpen ? "open" : ""}>
        <summary><strong>${this._t("themeTitle")}</strong><span class="muted small">${esc(names[current])}</span></summary>
        <div class="theme-grid">${list
          .map(
            (t) => `<button class="theme-swatch ${t.id === current ? "on" : ""}" data-action="theme" data-id="${esc(member.id)}" data-theme="${t.id}" aria-pressed="${t.id === current}">
              <span class="sw sw-${t.id || "clear"}">${t.emoji}</span><span class="sw-name">${esc(names[t.id])}</span></button>`,
          )
          .join("")}</div>
      </details>`;
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
    if (member.picture_mode) return this._renderPictureChild(member);
    const chores = this._openFor(member.id);
    const color = this._color(member.id);
    const { done, open, total } = this._todayStats(member.id);
    const left = chores.filter((c) => c.state !== "claimed").length;
    const line = !left ? this._t("allDoneToday") : left === 1 ? this._t("leftOne") : this._t("leftToday", { n: left });
    const list = chores.length
      ? `<ul class="tasks">${chores.map((c) => this._choreRow(c, member.id, { showClaim: c.state !== "claimed" })).join("")}</ul>`
      : `<div class="done-card"><div class="done-emoji">🎉</div><div class="done-title">${this._t("allDoneKid")}</div><div class="muted">${this._t("allDoneKidSub")}</div></div>`;
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
        ${this._pauseBanner()}${this._rainBanner()}
        ${this._renderGoal(member)}
        ${this._renderFamilyGoal()}
        ${member.locked ? `<p class="chip bad">${this._t("locked")}</p>` : ""}
        <div class="section-title">${this._t("todayTitle")}</div>
        ${list}
        ${this._renderTakeOver(member)}
        ${this._renderChildRewards(member)}
        ${this._renderMoney(member)}
        ${this._renderBadges(member)}
        ${this._renderChildStarLog(member)}
        ${this._renderThemePicker(member)}
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
    if (this._welcomeActive()) return this._renderWelcome();
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
        .join("")}<button class="tab theme-btn ${this._themeOpen ? "on" : ""}" data-action="theme-toggle" title="${this._t("themeParent")}" aria-label="${this._t("themeParent")}">🎨</button><button class="tab help-btn ${this._help ? "on" : ""}" data-action="help" title="${this._t("help")}" aria-label="${this._t("help")}">❓</button></nav>
      ${this._helpTip()}
      ${this._themeOpen && this._member(d.me) ? this._renderThemePicker(this._member(d.me)) : ""}
      ${body}
      ${this._donateLine()}`;
  }

  _children() {
    return this._data.members.filter((m) => m.role === "child");
  }

  _renderCockpit() {
    const d = this._data;
    const kids = this._children().filter((k) => !k.away);
    const waiting = d.chores.filter((c) => c.state === "claimed");
    const toApprove = waiting.length + (d.redemptions || []).length;
    const open = kids.reduce((n, k) => n + this._openFor(k.id).filter((c) => c.state !== "claimed").length, 0);
    const done = kids.filter((k) => !this._openFor(k.id).some((c) => c.state !== "claimed")).length;
    const stars = d.chores
      .filter((c) => c.last_completed_by && this._isToday(c.last_completed_at))
      .reduce((n, c) => n + (c.points || 0), 0);
    const now = new Date();
    const h = now.getHours();
    const greet = this._t("greet")[h < 11 ? 0 : h < 17 ? 1 : 2];
    const me = this._member(d.me);
    const date = now.toLocaleDateString(this._locale(), { weekday: "long", day: "numeric", month: "long" });
    const tile = (emoji, value, label, cls = "", action = "") => `
      <${action ? `button data-action="tab" data-id="${action}"` : "div"} class="ck-tile ${cls}">
        <span class="ck-emoji">${emoji}</span><span class="ck-value">${value}</span><span class="ck-label">${label}</span>
      </${action ? "button" : "div"}>`;
    return `
      <section class="cockpit">
        <div class="ck-hello">
          <div class="ck-greet">${esc(greet)}${me ? `, ${esc(me.name)}` : ""} 👋</div>
          <div class="muted">${esc(date)}</div>
        </div>
        <div class="ck-stats">
          ${tile("📝", open, this._t("ckOpen"))}
          ${tile("📬", toApprove, this._t("ckWaiting"), toApprove ? "hot" : "", toApprove ? "approve" : "")}
          ${tile("🎉", `${done}/${kids.length}`, this._t("ckKidsDone"), kids.length && done === kids.length ? "good" : "")}
          ${tile("⭐", stars, this._t("ckStars"))}
        </div>
        ${toApprove && !this._config.readonly ? `<div class="ck-approve"><div class="section-title">${this._t("ckWaitingTitle")}</div>${this._renderApprovals(waiting)}</div>` : ""}
      </section>`;
  }

  _renderToday() {
    return `${this._renderStarter()}${this._renderCockpit()}${this._pauseBanner()}${this._rainBanner()}${this._renderFamilyGoal()}<div class="kidgrid">${this._renderTodayCards()}</div>${this._renderWeek()}`;
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
        if (!this._config.readonly) {
          passBtn += `<button class="menu-item" data-action="picture" data-id="${esc(m.id)}" data-on="${m.picture_mode ? "" : "1"}">${
            m.picture_mode ? this._t("pictureOff") : this._t("pictureOn")
          }</button>`;
        }
        if (!this._config.readonly) {
          passBtn += `<button class="menu-item" data-action="stars-open" data-id="${esc(m.id)}">${this._t("starsBtn")}</button>`;
        }
        if (m.has_devices && !this._config.readonly) {
          passBtn += m.pass_until
            ? `<button class="menu-item" data-action="revoke-pass" data-id="${esc(m.id)}">🎟️ ${this._t("takePass")}</button>`
            : `<button class="menu-item" data-action="pass" data-id="${esc(m.id)}">🎟️ ${this._t("givePass")}</button>`;
        }
        const list = chores.length
          ? `<ul>${chores.map((c) => this._choreRow(c, m.id, { showClaim: c.state !== "claimed", forName: m.name })).join("")}</ul>`
          : `<p class="kid-done">🎉 ${this._t("allDone").replace(" 🎉", "")}</p>`;
        const { done, open, total } = this._todayStats(m.id);
        const menu = passBtn
          ? `<details class="kid-menu"><summary aria-label="${esc(this._t("moreActions", { name: m.name }))}" title="${esc(this._t("moreActions", { name: m.name }))}">⋯</summary><div class="menu">${passBtn}</div></details>`
          : "";
        return `
          <section class="kidcard" style="--kid:${this._color(m.id)}">
            <div class="kidcard-head">
              ${this._avatar(m, 40)}
              <div class="kidcard-name"><strong>${esc(m.name)}</strong><span class="muted small">⭐ ${m.points}${
                m.progress ? ` · ${esc(this._t("level", { n: m.progress.level }))}${m.progress.streak ? ` · 🔥 ${m.progress.streak}` : ""}` : ""
              }</span></div>
              ${this._ring(done, total || open, this._color(m.id), 44)}
              ${menu}
            </div>
            ${status ? `<div class="kidcard-status">${status}</div>` : ""}
            ${this._starsOpen === m.id ? this._renderStarsPanel(m) : ""}
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
            <div class="sub muted">${esc(this._member(c.claimed_by)?.name)} · ⭐ ${c.points * (c.claim_multiplier || 1)}${this._takenInfo(c)}</div>
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
            <div class="title">${c.icon ? esc(c.icon) + " " : ""}${esc(c.name)}</div>
            <div class="sub muted">${esc(names(c.assignees))} · ${esc(this._t("rec")[c.recurrence])}${c.rotation ? " · " + this._t("rotation") : ""}${
              c.requires_approval ? " · " + this._t("approval") : ""
            }${c.weekdays?.length ? " · " + esc(this._dayList(c.weekdays)) : ""}${c.requires_photo ? " · 📷" : ""}${c.outdoor ? " · " + this._t("outdoorShort") : ""}${c.has_tag ? " · 📱" : ""}${c.done_entity || c.start_entity ? " · 🏠" : ""}${c.steps?.length ? " · ☑️ " + esc(this._t("stepsShort", { n: c.steps.length })) : ""}${c.min_age ? " · " + esc(this._t("fromAge", { n: c.min_age })) : ""}${c.assignees.length && !c.responsible.length ? ` · <span class="chip">${this._t("paused")}</span>` : ""}</div>
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
      ${f.editId ? "" : this._renderSettings() + this._renderTemplates()}
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
        </div>
        <label class="check"><input type="checkbox" data-field="rotation" ${f.rotation ? "checked" : ""}>${this._t("rotation")}</label>
        <details class="more-options" ${this._hasAdvanced(f) ? "open" : ""}>
        <summary>${this._t("moreOptions")}</summary>
        <label>${this._t("minAge")}<input type="number" min="0" max="18" data-field="minAge" value="${esc(f.minAge)}" class="narrow"></label>
        <label class="check"><input type="checkbox" data-field="approval" ${f.approval ? "checked" : ""}>${this._t("approval")}</label>
        <label class="check"><input type="checkbox" data-field="photo" ${f.photo ? "checked" : ""}>${this._t("photo")}</label>
        <label class="check"><input type="checkbox" data-field="outdoor" ${f.outdoor ? "checked" : ""}>${this._t("outdoor")}</label>
        <fieldset><legend>${this._t("weekdays")}</legend>${this._t("dayShort")
          .map((d, i) => `<label class="check day"><input type="checkbox" data-field="weekday" value="${i}" ${f.weekdays.includes(i) ? "checked" : ""}>${d}</label>`)
          .join("")}</fieldset>
        <label>${this._t("icon")}<input data-field="icon" value="${esc(f.icon)}" maxlength="8" placeholder="🧹" class="icon-input"></label>
        ${this._nfcBlock(f)}
        ${this._houseBlock(f)}
        <label>${this._t("steps")}<textarea data-field="steps" rows="3" maxlength="800">${esc(f.steps)}</textarea></label>
        </details>
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
    return `${this._renderPause()}<ul>${this._children()
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
    const theme = THEMES.find((t) => t.id === this._themeId()) || THEMES[0];
    if (theme.id) this._cardEl.dataset.theme = theme.id;
    else delete this._cardEl.dataset.theme;
    const deco = theme.deco.length ? `<div class="deco" aria-hidden="true">${theme.deco.map((e) => `<span>${e}</span>`).join("")}</div>` : "";
    const html = `${deco}${this._config.title ? `<h1>${esc(this._config.title)}</h1>` : ""}<div class="content">${body}</div>`;
    if (html === this._html) return;
    this._html = html;
    const next = document.createElement("template");
    next.innerHTML = html;
    morphChildren(this._cardEl, next.content);
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
    school: true,
    name: { de: "Schultasche packen", en: "Pack school bag" },
    steps: { de: ["Hausaufgaben einpacken", "Stundenplan prüfen", "Brotdose", "Trinkflasche"], en: ["Pack homework", "Check timetable", "Lunch box", "Water bottle"] } },
  { emoji: "📚", age: 7, points: 3, rec: "daily", time: "16:00",
    school: true,
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
  { emoji: "🌱", age: 13, points: 5, rec: "weekly", time: "17:00", outdoor: true, name: { de: "Rasen mähen", en: "Mow the lawn" } },
  { emoji: "🍂", age: 8, points: 3, rec: "weekly", time: "16:00", outdoor: true, name: { de: "Laub rechen", en: "Rake leaves" } },
  { emoji: "🚲", age: 9, points: 3, rec: "biweekly", time: "16:00", outdoor: true, name: { de: "Fahrrad putzen", en: "Clean the bike" } },
  { emoji: "🌻", age: 6, points: 1, rec: "daily", time: "18:00", outdoor: true, name: { de: "Blumen gießen", en: "Water the plants" } },
  { emoji: "🚗", age: 14, points: 4, rec: "biweekly", time: "17:00", name: { de: "Auto aussaugen", en: "Vacuum the car" } },
];

// Symbol raten, wenn die Aufgabe keins hat (Bilder-Modus).
const CHORE_EMOJI = [
  [["rasen", "lawn"], "🌱"],
  [["laub", "leaves"], "🍂"],
  [["fahrrad", "bike"], "🚲"],
  [["gieß", "blumen", "water the", "plants"], "🌻"],
  [["müll", "trash", "abfall"], "🗑️"],
  [["spülmaschine", "geschirr", "dishwasher", "dishes"], "🍽️"],
  [["tisch", "table"], "🍴"],
  [["zimmer", "aufräumen", "room", "tidy"], "🧹"],
  [["zähne", "teeth"], "🪥"],
  [["bett", "bed"], "🛏️"],
  [["anzieh", "dress", "kleidung", "clothes"], "👕"],
  [["wäsche", "laundry"], "🧺"],
  [["staub", "sauge", "vacuum"], "🌀"],
  [["bad", "bath", "toilette"], "🛁"],
  [["hund", "katze", "hamster", "füttern", "feed", "pet"], "🐾"],
  [["blume", "pflanze", "gießen", "plant", "water"], "🪴"],
  [["hausaufgabe", "homework", "lesen", "read"], "📚"],
  [["schul", "school", "ranzen"], "🎒"],
  [["spielzeug", "toys"], "🧸"],
  [["duschen", "shower"], "🚿"],
  [["kochen", "cook"], "🍳"],
  [["einkauf", "shopping"], "🛒"],
];

// Kräftige Farben, die auf hell und dunkel funktionieren (weiße Schrift darauf).
// Designs zum Aussuchen. deco = kleine Bilder, die im Hintergrund schweben.
const THEMES = [
  { id: "", emoji: "✨", deco: [] },
  { id: "space", emoji: "🚀", deco: ["🪐", "⭐", "🌙", "🚀", "✨", "☄️"] },
  { id: "jungle", emoji: "🌴", deco: ["🌴", "🦜", "🍃", "🐒", "🌺", "🦋"] },
  { id: "ocean", emoji: "🐠", deco: ["🐠", "🫧", "🐳", "🐚", "🫧", "🐙"] },
  { id: "candy", emoji: "🍭", deco: ["🍭", "🍬", "🧁", "🌈", "💖", "🍩"] },
  { id: "elegant", emoji: "🤍", deco: [] },
];

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
  .row.wrap > .main { min-width: 140px; }
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
  .pause-banner { margin: 0 0 10px; padding: 12px 14px; border-radius: 16px; font-weight: 600;
                  background: linear-gradient(135deg, color-mix(in srgb, #13a8b8 22%, var(--card-background-color)), color-mix(in srgb, #e5a100 16%, var(--card-background-color))); }
  .rain-banner { background: linear-gradient(120deg, rgba(96, 125, 139, 0.18), rgba(33, 150, 243, 0.14)); }
  .chip.rain { background: rgba(33, 150, 243, 0.14); color: var(--primary-text-color); }
  .chip.best { background: rgba(255, 193, 7, 0.22); color: var(--primary-text-color); }
  section.week { margin-top: 16px; padding: 14px 16px; border-radius: 16px; background: var(--secondary-background-color); }
  .week-title { display: flex; align-items: center; justify-content: space-between; gap: 8px; flex-wrap: wrap; margin-bottom: 8px; }
  .week-list { list-style: none; margin: 0; padding: 0; display: grid; gap: 12px; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); }
  .week-row { display: flex; gap: 10px; align-items: center; min-width: 0; }
  .week-main { flex: 1; min-width: 0; }
  .week-head { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
  .week-stars { margin-left: auto; font-weight: 600; }
  .week-bar { height: 8px; margin: 6px 0 4px; border-radius: 99px; overflow: hidden;
    background: color-mix(in srgb, var(--error-color, #db4437) 30%, transparent); }
  .week-bar.nil { background: var(--divider-color, #e0e0e0); }
  .week-bar span { display: block; height: 100%; border-radius: 99px; background: var(--kid); }
  .settings-box { margin-bottom: 12px; }
  .stars-panel { margin: 8px 0 4px; padding: 12px; border-radius: 14px; background: var(--card-background-color, #fff);
    border: 1px solid var(--divider-color, #e0e0e0); display: grid; gap: 8px; }
  .star-chips { display: flex; flex-wrap: wrap; gap: 6px; }
  .star-chip { display: inline-flex; align-items: center; gap: 4px; border: none; border-radius: 99px; padding: 6px 12px;
    font: inherit; font-size: 0.9em; cursor: pointer; color: var(--primary-text-color); }
  span.star-chip { cursor: default; padding-right: 6px; }
  .star-chip.plus { background: color-mix(in srgb, var(--success-color, #22a565) 18%, transparent); }
  .star-chip.minus { background: color-mix(in srgb, var(--error-color, #db4437) 14%, transparent); }
  .star-chip .x { border: none; background: none; cursor: pointer; font-size: 1.1em; padding: 0 4px; color: var(--secondary-text-color); }
  .stars-custom { display: flex; gap: 6px; flex-wrap: wrap; align-items: center; }
  .stars-custom input[type="number"] { width: 72px; }
  .stars-custom input:not([type]) { flex: 1; min-width: 120px; }
  .more-options { margin: 8px 0; padding: 8px 12px; border-radius: 12px; background: color-mix(in srgb, var(--primary-text-color) 4%, transparent); }
  .more-options summary { cursor: pointer; font-weight: 500; }
  .more-options[open] summary { margin-bottom: 8px; }
  input.narrow { max-width: 120px; }
  .starter { margin-bottom: 16px; padding: 18px; border-radius: 18px;
    background: linear-gradient(135deg, color-mix(in srgb, var(--primary-color, #03a9f4) 16%, transparent), color-mix(in srgb, #ffc107 14%, transparent)); }
  .starter-title { font-size: 1.25em; font-weight: 700; margin-bottom: 4px; }
  .starter-cols { display: grid; gap: 12px; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); }
  .starter ul { margin: 6px 0 0; padding-left: 0; list-style: none; display: grid; gap: 4px; }
  .starter-actions { display: flex; flex-wrap: wrap; gap: 12px; align-items: center; margin-top: 14px; }
  button.big { font-size: 1.05em; padding: 12px 22px; }
  .help-btn { margin-left: auto; }
  .help-tip { margin: 0 0 12px; padding: 10px 14px; border-radius: 12px; background: color-mix(in srgb, #ffc107 16%, transparent); }
  .nfc-box { display: grid; gap: 4px; margin: 8px 0; padding: 10px 12px; border-radius: 12px;
    border: 1px dashed var(--divider-color, #e0e0e0); }
  .voice-help { margin-top: 12px; }
  .house-box { margin: 8px 0; padding: 10px 12px; border-radius: 12px; border: 1px dashed var(--divider-color, #e0e0e0); }
  .house-box summary { cursor: pointer; }
  .house-row { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; margin: 8px 0; }
  .house-label { min-width: 120px; font-size: 0.9em; }
  .house-row input { flex: 1; min-width: 150px; }
  .house-row input.house-state { flex: 0 1 120px; min-width: 100px; }
  .voice-help ul { margin: 4px 0 0; padding-left: 18px; }
  .preset-admin { display: grid; gap: 8px; margin-top: 12px; }
  section.star-log { margin-top: 12px; }
  .pause-box { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; margin-bottom: 12px; }
  .pause-box .pause-banner { flex: 1; margin: 0; }
  label.check.day { margin-right: 6px; }
  input.icon-input { width: 80px; font-size: 1.3em; text-align: center; }
  .kid.picture .hero .hello { font-size: 1.6em; }
  .big-star { font-size: 1.3em; }
  .kid.picture .hero .level-badge { width: 48px; height: 48px; font-size: 1.4em; }
  .pic-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 12px; margin: 8px 0; }
  .pic { display: flex; flex-direction: column; gap: 6px; padding: 8px; border-radius: 22px; background: var(--secondary-background-color); }
  .pic.overdue { box-shadow: inset 0 0 0 3px var(--error-color, #db4437); }
  button.pic-main { position: relative; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 4px;
                    min-height: 140px; border-radius: 18px; background: var(--card-background-color); color: var(--primary-text-color);
                    box-shadow: 0 3px 0 color-mix(in srgb, var(--kid) 45%, transparent); transition: transform .1s; }
  button.pic-main:active { transform: scale(.96); }
  button.pic-main[disabled] { cursor: default; }
  .pic.wait button.pic-main { opacity: .6; }
  .pic-icon { font-size: 4em; line-height: 1; }
  .pic-stars { font-size: 0.9em; letter-spacing: -2px; }
  .pic-state { position: absolute; top: 8px; right: 10px; font-size: 1.4em; }
  button.pic-say { background: none; color: var(--primary-text-color); font-weight: 600; min-height: 32px; padding: 0 6px; text-align: center; }
  .pic ol.steps { margin-top: 0; }
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
    ul.tasks .actions { width: auto; } .hero { padding: 12px; } .hero .hello { font-size: 1.2em; } }  /* -- Gestaltung 0.28: Symbole, ruhige Elternkarten, Fertig-Karte -- */
  .task-icon { flex: 0 0 auto; width: 44px; height: 44px; border-radius: 14px; display: flex; align-items: center; justify-content: center;
               font-size: 1.45em; background: color-mix(in srgb, var(--kid, var(--primary-color)) 16%, var(--card-background-color)); }
  .row.task.overdue .task-icon { background: color-mix(in srgb, var(--error-color, #db4437) 14%, var(--card-background-color)); }
  ul.tasks .row.task { border-left: none; background: var(--card-background-color);
                       box-shadow: 0 1px 2px rgba(0,0,0,.06), 0 0 0 1px color-mix(in srgb, var(--primary-text-color) 7%, transparent); }
  ul.tasks .row.task.overdue { box-shadow: 0 0 0 2px color-mix(in srgb, var(--error-color, #db4437) 55%, transparent); }
  .kid { --radius: 20px; }
  .kid .hero { border-radius: var(--radius); padding: 18px; }
  .kid .level, .kid .goal, .kid .fgoal { border-radius: var(--radius); }
  .kid .section-title { font-size: 1.15em; font-weight: 700; margin: 18px 0 8px; }
  .pts-pill { white-space: nowrap; }
  .done-card { text-align: center; padding: 22px 16px; border-radius: 20px;
               background: linear-gradient(135deg, color-mix(in srgb, var(--kid, #22a565) 20%, var(--card-background-color)), color-mix(in srgb, #e5a100 14%, var(--card-background-color))); }
  .done-emoji { font-size: 3em; line-height: 1.1; animation: wiggle 1s ease-in-out 2; }
  .done-title { font-size: 1.25em; font-weight: 700; margin: 6px 0 2px; }
  .kidgrid { align-items: start; gap: 14px; }
  section.kidcard { background: var(--card-background-color); border-top: none; border-radius: 18px; padding: 14px 16px;
                    box-shadow: 0 1px 3px rgba(0,0,0,.08), 0 0 0 1px color-mix(in srgb, var(--primary-text-color) 6%, transparent);
                    position: relative; overflow: visible; }
  section.kidcard::before { content: ""; position: absolute; left: 16px; right: 16px; top: 0; height: 4px; border-radius: 0 0 4px 4px; background: var(--kid); }
  .kidcard-name strong { font-size: 1.1em; }
  .kidcard .row.task { padding: 10px 0; }
  .kidcard .task-icon { width: 36px; height: 36px; border-radius: 11px; font-size: 1.15em; }
  .kidcard ul { margin-top: 4px; }
  .kid-done { margin: 10px 0 2px; padding: 10px 12px; border-radius: 12px; font-weight: 600; font-size: 0.95em;
              background: color-mix(in srgb, var(--kid) 12%, transparent); }
  details.kid-menu { position: relative; flex: 0 0 auto; }
  details.kid-menu summary { list-style: none; cursor: pointer; width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center;
                             justify-content: center; font-size: 1.3em; font-weight: 700; color: var(--secondary-text-color); }
  details.kid-menu summary::-webkit-details-marker { display: none; }
  details.kid-menu summary:hover, details.kid-menu[open] summary { background: var(--secondary-background-color); color: var(--primary-text-color); }
  .menu { position: absolute; right: 0; top: 40px; z-index: 3; min-width: 210px; padding: 6px; border-radius: 14px; display: flex; flex-direction: column;
          background: var(--card-background-color); box-shadow: 0 8px 28px rgba(0,0,0,.18), 0 0 0 1px color-mix(in srgb, var(--primary-text-color) 8%, transparent); }
  button.menu-item { background: none; color: var(--primary-text-color); text-align: left; border-radius: 10px; min-height: 40px; padding: 0 12px; white-space: nowrap; }
  button.menu-item:hover { background: var(--secondary-background-color); }
  section.week, .starter { border-radius: 18px; }
  @media (prefers-reduced-motion: reduce) { .done-emoji { animation: none; } }
  /* -- Designs zum Aussuchen (0.29) -- */
  ha-card { position: relative; display: block; }
  ha-card > .content, ha-card > h1 { position: relative; z-index: 1; }
  .deco { position: absolute; inset: 0; overflow: hidden; pointer-events: none; z-index: 0; border-radius: inherit; }
  .deco span { position: absolute; font-size: 46px; opacity: .16; animation: drift 11s ease-in-out infinite; }
  .deco span:nth-child(1) { top: 1%; right: 4%; font-size: 64px; }
  .deco span:nth-child(2) { top: 22%; left: -8px; animation-delay: -3s; }
  .deco span:nth-child(3) { top: 44%; right: -6px; font-size: 54px; animation-delay: -6s; }
  .deco span:nth-child(4) { top: 63%; left: 6%; animation-delay: -2s; }
  .deco span:nth-child(5) { top: 80%; right: 12%; font-size: 38px; animation-delay: -8s; }
  .deco span:nth-child(6) { bottom: 1%; left: 38%; font-size: 40px; animation-delay: -5s; }
  @keyframes drift { 50% { transform: translateY(-14px) rotate(8deg); } }
  ha-card[data-theme] { border-radius: 24px; }
  ha-card[data-theme] input, ha-card[data-theme] select, ha-card[data-theme] textarea { background: var(--card-background-color); color: var(--primary-text-color); }
  ha-card[data-theme] .tabs { background: var(--secondary-background-color); }
  ha-card[data-theme] .tab.on { background: var(--card-background-color); }

  ha-card[data-theme="space"] {
    --primary-text-color: #eef1ff; --secondary-text-color: #aab3da; --card-background-color: rgba(255,255,255,.08);
    --secondary-background-color: rgba(255,255,255,.06); --divider-color: rgba(255,255,255,.14); --primary-color: #8aa4ff;
    color: var(--primary-text-color);
    background:
      radial-gradient(1.6px 1.6px at 12% 18%, #fff 50%, transparent 52%),
      radial-gradient(1.2px 1.2px at 64% 9%, #fff 50%, transparent 52%),
      radial-gradient(1.4px 1.4px at 86% 42%, #fff 50%, transparent 52%),
      radial-gradient(1px 1px at 33% 61%, #fff 50%, transparent 52%),
      radial-gradient(1.8px 1.8px at 52% 83%, #ffe9a8 50%, transparent 52%),
      radial-gradient(1px 1px at 8% 92%, #fff 50%, transparent 52%),
      radial-gradient(ellipse 70% 45% at 90% 0%, rgba(124, 77, 255, .45), transparent 70%),
      radial-gradient(ellipse 60% 40% at 0% 100%, rgba(0, 150, 255, .3), transparent 70%),
      linear-gradient(180deg, #0b1026, #15123a 60%, #0d1530);
    background-size: 240px 240px, 300px 300px, 260px 260px, 180px 180px, 340px 340px, 220px 220px, 100% 100%, 100% 100%, 100% 100%;
  }
  ha-card[data-theme="space"] .deco span { opacity: .3; }
  ha-card[data-theme="space"] ul.tasks .row.task, ha-card[data-theme="space"] section.kidcard { backdrop-filter: blur(6px);
    box-shadow: 0 0 0 1px rgba(255,255,255,.1); }
  ha-card[data-theme="space"] .hero { background: linear-gradient(135deg, color-mix(in srgb, var(--kid) 45%, transparent), rgba(255,255,255,.04));
    box-shadow: 0 0 30px color-mix(in srgb, var(--kid) 35%, transparent); }

  ha-card[data-theme="jungle"] {
    --primary-text-color: #173a22; --secondary-text-color: #4e6d57; --card-background-color: rgba(255,255,255,.86);
    --secondary-background-color: rgba(255,255,255,.55); --divider-color: rgba(23,58,34,.12); --primary-color: #2e9b57;
    color: var(--primary-text-color);
    background:
      radial-gradient(circle at 100% 0%, rgba(255, 214, 102, .55), transparent 35%),
      radial-gradient(ellipse 60% 40% at 0% 100%, rgba(46, 155, 87, .35), transparent 70%),
      linear-gradient(165deg, #f1fbe9, #d3f0cf 55%, #b4e2bb);
  }
  ha-card[data-theme="jungle"] .deco span { opacity: .22; }

  ha-card[data-theme="ocean"] {
    --primary-text-color: #0c3450; --secondary-text-color: #3d6984; --card-background-color: rgba(255,255,255,.84);
    --secondary-background-color: rgba(255,255,255,.5); --divider-color: rgba(12,52,80,.12); --primary-color: #1c8fd6;
    color: var(--primary-text-color);
    background:
      radial-gradient(circle at 14% 76%, transparent 9px, rgba(255,255,255,.7) 10px, transparent 12px),
      radial-gradient(circle at 82% 58%, transparent 6px, rgba(255,255,255,.7) 7px, transparent 9px),
      radial-gradient(circle at 46% 90%, transparent 12px, rgba(255,255,255,.6) 13px, transparent 15px),
      radial-gradient(ellipse 80% 30% at 50% 0%, rgba(255,255,255,.7), transparent 70%),
      linear-gradient(180deg, #e6f7ff, #a6dcf4 55%, #63bde6);
    background-size: 320px 420px, 260px 360px, 380px 500px, 100% 100%, 100% 100%;
  }
  ha-card[data-theme="ocean"] .deco span { opacity: .24; }

  ha-card[data-theme="candy"] {
    --primary-text-color: #4a1f4f; --secondary-text-color: #8a678f; --card-background-color: rgba(255,255,255,.9);
    --secondary-background-color: rgba(255,255,255,.6); --divider-color: rgba(74,31,79,.1); --primary-color: #e0559a;
    color: var(--primary-text-color);
    background:
      radial-gradient(circle, rgba(255, 105, 180, .16) 2.5px, transparent 3.5px),
      radial-gradient(circle, rgba(140, 110, 255, .14) 2.5px, transparent 3.5px),
      linear-gradient(135deg, #fff0f6, #f6e9ff 50%, #e7f3ff);
    background-size: 28px 28px, 28px 28px, 100% 100%;
    background-position: 0 0, 14px 14px, 0 0;
  }
  ha-card[data-theme="candy"] ul.tasks .row.task, ha-card[data-theme="candy"] .reward, ha-card[data-theme="candy"] .level,
  ha-card[data-theme="candy"] .goal { border-radius: 22px; }
  ha-card[data-theme="candy"] button.primary { box-shadow: 0 3px 0 color-mix(in srgb, var(--kid, var(--primary-color)) 55%, #000); }
  ha-card[data-theme="candy"] .deco span { opacity: .26; }

  ha-card[data-theme="elegant"] {
    --primary-text-color: #2b2722; --secondary-text-color: #7a7067; --card-background-color: #fffdf9;
    --secondary-background-color: #f1ebe2; --divider-color: #e6ddd1; --primary-color: #8a6d4b;
    color: var(--primary-text-color); background: linear-gradient(180deg, #faf7f2, #f3eee6);
  }
  ha-card[data-theme="elegant"] .hello, ha-card[data-theme="elegant"] .section-title, ha-card[data-theme="elegant"] .kidcard-name strong,
  ha-card[data-theme="elegant"] .fgoal-top strong, ha-card[data-theme="elegant"] .starter-title { font-family: Georgia, "Times New Roman", serif; letter-spacing: .01em; }
  ha-card[data-theme="elegant"] section.kidcard { box-shadow: 0 10px 30px rgba(60, 40, 20, .07), 0 0 0 1px #ece4d8; }

  ha-card[data-theme="jungle"] .hero { background: linear-gradient(135deg, #23864a, #6cc35f 70%, #b8de6a); }
  ha-card[data-theme="ocean"] .hero { background: linear-gradient(135deg, #1374c2, #22a9d8 60%, #57d5d2); }
  ha-card[data-theme="candy"] .hero { background: linear-gradient(135deg, #ff6fae, #c286ff 70%, #8fb8ff); }
  ha-card[data-theme="jungle"] .hero, ha-card[data-theme="ocean"] .hero, ha-card[data-theme="candy"] .hero {
    --primary-text-color: #fff; --secondary-text-color: rgba(255,255,255,.88); --divider-color: rgba(255,255,255,.35);
    color: #fff; box-shadow: 0 10px 24px rgba(0,0,0,.12); }
  ha-card[data-theme] .hero .star { background: rgba(255,255,255,.25); color: #fff; }
  ha-card[data-theme] .hero .avatar { box-shadow: 0 0 0 3px rgba(255,255,255,.6), 0 4px 10px rgba(0,0,0,.2); }
  ha-card[data-theme="jungle"] .section-title, ha-card[data-theme="jungle"] .section-head strong { color: #1f6b3a; }
  ha-card[data-theme="ocean"] .section-title, ha-card[data-theme="ocean"] .section-head strong { color: #0f5d8f; }
  ha-card[data-theme="candy"] .section-title, ha-card[data-theme="candy"] .section-head strong { color: #c23d84; }
  ha-card[data-theme="space"] .section-title, ha-card[data-theme="space"] .section-head strong { color: #c9d4ff; text-shadow: 0 0 12px rgba(138,164,255,.6); }
  /* Schmale Kinderkarten: Knopf unter die Aufgabe, damit der Name lesbar bleibt */
  section.kidcard { container-type: inline-size; }
  .kidgrid { grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); }
  @container (max-width: 440px) {
    .kidcard .row.task { display: grid; grid-template-columns: auto 1fr auto; column-gap: 12px; row-gap: 6px; align-items: center; }
    .kidcard .row.task > .actions { grid-column: 2 / -1; width: auto; justify-content: flex-end; }
    .kidcard .row.task > .actions:empty { display: none; }
    .kidcard .row.task > ol.steps { grid-column: 1 / -1; }
  }
  /* -- Willkommens-Assistent (0.29) -- */
  .wizard { max-width: 720px; margin: 0 auto; padding: 22px 6px 10px; }
  .wizard h2 { font-size: 1.7em; line-height: 1.15; margin: 6px 0 6px; font-weight: 800; letter-spacing: -.02em; }
  .wizard > p.muted { margin: 0 0 18px; font-size: 1.02em; }
  .wz-hero { text-align: center; display: flex; flex-direction: column; align-items: center; gap: 12px; padding: 26px 12px 18px;
    border-radius: 28px; background: radial-gradient(circle at 50% 0%, rgba(255, 214, 102, .45), transparent 55%),
    linear-gradient(160deg, color-mix(in srgb, #4f7cff 16%, var(--card-background-color)), color-mix(in srgb, #a259ff 12%, var(--card-background-color))); }
  .wz-hero h2 { font-size: 2em; }
  .wz-hero p { max-width: 460px; margin: 0; color: var(--secondary-text-color); font-size: 1.05em; }
  .wz-star { font-size: 4.4em; line-height: 1; filter: drop-shadow(0 8px 18px rgba(229, 161, 0, .45)); animation: wzfloat 3s ease-in-out infinite; }
  @keyframes wzfloat { 50% { transform: translateY(-10px) rotate(6deg); } }
  .wz-kids-row { display: flex; gap: 0; margin: 6px 0 8px; }
  .wz-kids-row .avatar { margin-left: -8px; border: 3px solid var(--card-background-color); }
  .wz-top { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 8px; }
  .wz-dots { display: flex; gap: 6px; }
  .wz-dots i { width: 28px; height: 6px; border-radius: 3px; background: var(--divider-color, #e0e0e0); }
  .wz-dots i.on { background: linear-gradient(90deg, #4f7cff, #a259ff); }
  .wz-nav { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-top: 22px; }
  .wz-kid-list { display: grid; gap: 12px; }
  .wz-kid { padding: 14px; border-radius: 20px; background: var(--card-background-color);
    box-shadow: 0 1px 3px rgba(0,0,0,.08), 0 0 0 1px color-mix(in srgb, var(--primary-text-color) 6%, transparent); border-left: 6px solid var(--kid); }
  .wz-kid-head { display: flex; align-items: center; gap: 12px; }
  .wz-kid-head strong { flex: 1; font-size: 1.2em; }
  .wz-age { display: flex; align-items: center; gap: 8px; font-size: 0.9em; color: var(--secondary-text-color); }
  .wz-age select { font-size: 1.05em; min-width: 64px; }
  .wz-caption { margin-top: 12px; }
  .wz-themes { display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px; margin-top: 6px; }
  button.wz-theme { padding: 3px; min-height: auto; border-radius: 14px; background: none; }
  button.wz-theme .sw { height: 46px; font-size: 1.4em; }
  button.wz-theme.on { box-shadow: 0 0 0 3px var(--kid); }
  .wz-group { font-weight: 700; margin: 14px 0 8px; color: var(--secondary-text-color); font-size: 0.9em; text-transform: uppercase; letter-spacing: .06em; }
  .wz-picks { display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: 10px; }
  button.wz-pick { display: flex; align-items: center; gap: 12px; text-align: left; padding: 12px; min-height: 64px; border-radius: 16px;
    background: var(--card-background-color); color: var(--primary-text-color); box-shadow: 0 0 0 2px #22a565; transition: transform .1s, opacity .2s; }
  button.wz-pick:active, button.wz-reward:active, button.wz-choice:active { transform: scale(.98); }
  button.wz-pick.off, button.wz-reward.off { box-shadow: 0 0 0 1px var(--divider-color, #e0e0e0); opacity: .5; }
  .wz-pick-icon { font-size: 1.6em; width: 44px; height: 44px; border-radius: 14px; display: flex; align-items: center; justify-content: center;
    background: var(--secondary-background-color); flex: 0 0 auto; }
  .wz-pick-main { flex: 1; min-width: 0; display: flex; flex-direction: column; }
  .wz-check { flex: 0 0 auto; width: 26px; height: 26px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
    font-weight: 800; color: #fff; background: #22a565; font-size: 0.85em; }
  .off .wz-check { background: none; box-shadow: inset 0 0 0 2px var(--divider-color, #ccc); }
  .wz-rewards { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 12px; }
  button.wz-reward { position: relative; display: flex; flex-direction: column; align-items: center; gap: 6px; padding: 18px 10px 14px; min-height: 150px;
    border-radius: 20px; background: var(--card-background-color); color: var(--primary-text-color); box-shadow: 0 0 0 2px #e5a100; text-align: center; }
  .wz-reward-emoji { font-size: 2.6em; }
  button.wz-reward .wz-check { position: absolute; top: 10px; right: 10px; background: #e5a100; }
  .wz-choices { display: grid; gap: 12px; }
  button.wz-choice { display: flex; align-items: center; gap: 14px; text-align: left; padding: 16px; min-height: 76px; border-radius: 18px;
    background: var(--card-background-color); color: var(--primary-text-color); box-shadow: 0 0 0 1px var(--divider-color, #e0e0e0); }
  button.wz-choice > span:last-child { display: flex; flex-direction: column; gap: 2px; }
  button.wz-choice.on { box-shadow: 0 0 0 3px var(--primary-color); background: color-mix(in srgb, var(--primary-color) 8%, var(--card-background-color)); }
  .wz-choice-emoji { font-size: 2em; }
  ul.wz-tips { text-align: left; margin: 4px 0 8px; padding-left: 20px; color: var(--secondary-text-color); display: grid; gap: 6px; max-width: 460px; }
  @media (prefers-reduced-motion: reduce) { .wz-star { animation: none; } }
  @media (max-width: 480px) { .wizard h2 { font-size: 1.4em; } .wz-hero h2 { font-size: 1.6em; } .wz-themes { gap: 5px; } button.wz-theme .sw { height: 40px; } }
  /* -- Eltern-Cockpit (0.31) -- */
  .cockpit { margin: 0 0 14px; }
  .ck-hello { display: flex; flex-direction: column; gap: 2px; margin: 6px 2px 12px; }
  .ck-greet { font-size: 1.6em; font-weight: 800; letter-spacing: -.02em; }
  .ck-stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }
  .ck-tile { display: flex; flex-direction: column; align-items: flex-start; gap: 2px; padding: 14px 14px 12px; border-radius: 18px; text-align: left;
    background: var(--card-background-color); color: var(--primary-text-color); min-height: auto;
    box-shadow: 0 1px 3px rgba(0,0,0,.07), 0 0 0 1px color-mix(in srgb, var(--primary-text-color) 6%, transparent); }
  button.ck-tile { cursor: pointer; font: inherit; }
  .ck-emoji { font-size: 1.3em; }
  .ck-value { font-size: 1.9em; font-weight: 800; line-height: 1.1; letter-spacing: -.02em; }
  .ck-label { font-size: 0.82em; color: var(--secondary-text-color); }
  .ck-tile.hot { background: linear-gradient(135deg, #ff7a45, #ffb03a); color: #fff; box-shadow: 0 6px 18px rgba(255,122,69,.35); }
  .ck-tile.hot .ck-label { color: rgba(255,255,255,.9); }
  .ck-tile.good { background: linear-gradient(135deg, #22a565, #6cc35f); color: #fff; }
  .ck-tile.good .ck-label { color: rgba(255,255,255,.9); }
  .ck-approve { margin-top: 14px; padding: 6px 16px 8px; border-radius: 18px; background: var(--card-background-color);
    box-shadow: 0 0 0 2px color-mix(in srgb, #ff7a45 45%, transparent); }
  .ck-approve .section-title { margin: 10px 0 2px; }
  @media (max-width: 560px) { .ck-stats { grid-template-columns: repeat(2, 1fr); } .ck-greet { font-size: 1.35em; } }
  .theme-box { margin-top: 18px; padding: 12px 14px; border-radius: 18px; background: var(--secondary-background-color); }
  .theme-box summary { list-style: none; cursor: pointer; display: flex; align-items: center; gap: 10px; }
  .theme-box summary::-webkit-details-marker { display: none; }
  .theme-box summary::after { content: "▾"; margin-left: auto; color: var(--secondary-text-color); }
  .theme-box[open] summary::after { transform: rotate(180deg); }
  .theme-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(96px, 1fr)); gap: 10px; margin-top: 12px; }
  button.theme-swatch { display: flex; flex-direction: column; align-items: center; gap: 6px; padding: 8px 6px 10px; min-height: auto;
    border-radius: 16px; background: var(--card-background-color); color: var(--primary-text-color); box-shadow: 0 0 0 1px var(--divider-color); }
  button.theme-swatch.on { box-shadow: 0 0 0 3px var(--kid, var(--primary-color)); }
  .sw { width: 100%; height: 58px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.8em; }
  .sw-clear { background: linear-gradient(135deg, #eef3ff, #ffffff); }
  .sw-space { background: radial-gradient(1.5px 1.5px at 30% 30%, #fff 50%, transparent 52%), radial-gradient(1.5px 1.5px at 75% 65%, #fff 50%, transparent 52%), linear-gradient(135deg, #0b1026, #3b2a7a); }
  .sw-jungle { background: linear-gradient(135deg, #f1fbe9, #9fd9a8); }
  .sw-ocean { background: linear-gradient(180deg, #e6f7ff, #63bde6); }
  .sw-candy { background: radial-gradient(circle, rgba(255,105,180,.3) 2px, transparent 3px) 0 0 / 12px 12px, linear-gradient(135deg, #ffe0ef, #ead9ff); }
  .sw-elegant { background: linear-gradient(135deg, #faf7f2, #e9dfd1); }
  .sw-name { font-size: 0.85em; font-weight: 600; }
  .theme-btn { flex: 0 0 auto; margin-left: auto; }
  .theme-btn + .help-btn { margin-left: 0; }
  @media (prefers-reduced-motion: reduce) { .deco span { animation: none; } }
  @media (max-width: 480px) {
    ul.tasks .row.task { display: grid; grid-template-columns: auto 1fr auto; column-gap: 12px; row-gap: 8px; align-items: center; }
    ul.tasks .row.task > .actions { grid-column: 1 / -1; width: 100%; justify-content: stretch; }
    ul.tasks .row.task > .actions:empty { display: none; }
    ul.tasks .row.task > .actions button.primary { width: 100%; }
    ul.tasks .row.task > ol.steps { grid-column: 1 / -1; }
    .kidcard .row.task { display: grid; grid-template-columns: auto 1fr auto; column-gap: 12px; row-gap: 6px; align-items: center; }
    .kidcard .row.task > .actions { grid-column: 2 / -1; width: auto; justify-content: flex-end; }
    .kidcard .row.task > .actions:empty { display: none; }
    .kidcard .row.task > ol.steps { grid-column: 1 / -1; }
  }
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
