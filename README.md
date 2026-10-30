# Sternchenplan

Home-Assistant-Integration für Familienaufgaben. Läuft komplett lokal, ohne Cloud.

Stand: Version 0.19.0. Noch nicht für den Alltag gedacht.

## Umstieg vom Arbeitstitel „Familienplan“

Bis Version 0.13.0 hieß die Integration `familienplan`. Ab 0.14.0 heißt sie `sternchenplan`. Daten werden nicht übernommen, weil es noch keine echten Nutzer gibt:

1. Unter Einstellungen → Geräte & Dienste die Integration „Familienplan“ löschen.
2. Den Ordner `custom_components/familienplan` löschen und `custom_components/sternchenplan` hineinkopieren.
3. Home Assistant neu starten und „Sternchenplan“ neu einrichten.

## Was schon geht

- **Einrichtung in drei kurzen Schritten** über *Einstellungen → Geräte & Dienste → Integration hinzufügen → Sternchenplan*:
  1. Name der Familie
  2. Wer gehört dazu: die Personen aus Home Assistant sind schon angehakt, Kinder ohne eigenes Konto einfach mit Namen eintragen
  3. Wer sind die Eltern: HA-Administratoren sind vorgeschlagen

  Danach öffnet man links **Sternchenplan**. Dort begrüßt einen der **Willkommens-Assistent** mit vier großen, einfachen Schritten: Alter und Design jedes Kindes, passende Aufgaben antippen, Belohnungen antippen, Fotos löschen oder behalten. Ein Tipp auf „✨ Alles anlegen“, fertig.

  Eigene Aufgaben legt man danach unter *Sternchenplan → Aufgaben* an.

  Die Handys für Erinnerungen werden über die Companion-App automatisch zugeordnet. Danach erscheint links in der Seitenleiste **Sternchenplan**, ein Dashboard muss niemand einrichten.
- Weitere Mitglieder, Erinnerungen, Ansagen, Internetsperre und Regeln später unter *Konfigurieren*
- Aufgaben: einmalig, täglich, wöchentlich, alle 2 Wochen; Reihum-Rotation; Punkte; Elternfreigabe
- Überfällig-Erkennung (jede Minute)
- **Belohnungen**: Eltern legen fest, was es gibt und wie viele Punkte es kostet, für alle Kinder oder nur für bestimmte. Kinder sehen ihren Fortschritt und lösen ein, die Punkte werden sofort abgezogen. Eltern bekommen eine Push-Nachricht und bestätigen oder lehnen ab (dann gibt es die Punkte zurück). Das Kind kann eine Einlösung auch selbst zurücknehmen.
- **Alter**: Je Kind ein Alter, je Aufgabe ein Mindestalter („ab 8“). Zu junge Kinder werden bei Reihum übersprungen und rücken automatisch nach, sobald sie alt genug sind. Unbekanntes Alter zählt als alt genug. Alter ändern unter *Konfigurieren → Alter der Kinder* oder per Dienst `sternchenplan.set_age`.
- Abwesenheit (z. B. Klassenfahrt, krank) mit Beginn, Ende und Vertretung. Bei Rotation ist automatisch das nächste Kind dran; ohne Rotation übernimmt die Vertretung. Ist niemand da, ruht die Aufgabe und wird nicht überfällig.
- Erinnerungen per HA-Push an Kinder zu einstellbaren Uhrzeiten (Standard 15:00, 17:00, 18:30), nur wenn noch etwas offen ist; Sammelnachricht an Eltern (Standard 19:00)
- **Ansagen über Lautsprecher**: Zu einstellbaren Uhrzeiten (Standard 17:00, 18:30) sagt Sternchenplan an, wer heute noch etwas offen hat, z. B. „Lucas, bei dir ist noch offen: Müll und Tisch decken.“ Ist alles erledigt, bleibt es still. Geht über jede Sprachausgabe von HA auf beliebige Lautsprecher (Sonos, Google, Piper usw.) und optional über Alexa Media Player. Dienst `sternchenplan.announce` für eigene Ansagen aus Automationen.
- Sensoren: Punkte je Mitglied, Status je Aufgabe
- **Internetsperre** (ausgeschaltet bis man sie aktiviert): Eltern wählen je Kind Internet-Schalter von Freizeitgeräten (z. B. FRITZ!Box „Internetzugang“). Hat das Kind im Sperrzeitraum (Standard 20:00–05:00) überfällige Aufgaben, gehen diese Schalter aus. Sie gehen wieder an, sobald alles erledigt oder gemeldet ist, spätestens am Ende des Zeitraums. Schaltet jemand ein gesperrtes Gerät wieder an, wird es nach spätestens einer Minute erneut gesperrt. Eltern können eine Freikarte geben. Abwesende Kinder werden nie gesperrt. Sternchenplan gibt nur Geräte frei, die es selbst gesperrt hat, und fasst keine anderen Schalter an.
- **Fotonachweis** je Aufgabe, standardmäßig aus: Eltern haken ihn pro Aufgabe an. Kinder machen beim Abhaken ein Foto (Kamera öffnet sich in der Karte), die Aufgabe geht dann immer zur Bestätigung an die Eltern. Fotos bleiben lokal in `config/sternchenplan_photos`, sind nicht öffentlich, nur Eltern sehen sie über einen kurz gültigen Link.
- **Datenschutz bei Fotos**: Die Familie wählt im Willkommens-Assistenten (später unter *Konfigurieren → Regeln*), ob Fotos sofort nach Bestätigen oder Ablehnen gelöscht werden (Standard) oder bis zu 7 Tage (einstellbar) bleiben. Nimmt ein Kind seine Meldung zurück, wird das Foto immer sofort gelöscht.
- **Aufgaben übernehmen („wegmopsen“)**: Ab 16:30 können Kinder offene Aufgaben der Geschwister übernehmen und bekommen die Punkte, ab 19:00 doppelt. Höchstens 2 pro Tag. Bei Reihum-Aufgaben geht die Reihenfolge danach normal weiter. Zeiten und Anzahl unter *Konfigurieren → Regeln*.
- Dienste: `sternchenplan.create_chore`, `update_chore`, `delete_chore`, `claim_chore`, `take_over_chore`, `announce`, `create_reward`, `update_reward`, `delete_reward`, `redeem_reward`, `approve_redemption`, `reject_redemption`, `undo_claim`, `approve_chore`, `reject_chore`, `set_absence`, `end_absence`, `set_devices`, `grant_pass`, `revoke_pass`

## Kinder ohne eigenes Handy

Ein gemeinsames Familientablet (z. B. in der Küche) bekommt ein eigenes
HA-Konto. Das wählt man bei der Einrichtung oder später unter
*Konfigurieren › Familientablet* aus. Am Tablet zeigt die Seitenleiste
„Wer bist du?“ mit großen Namenskacheln. Das Kind tippt seinen Namen an und
hakt ab. Nach einer Minute ohne Tippen geht es zurück zur Auswahl. Das
Tablet darf pro Kind genau so viel wie das Kind selbst: nur eigene Aufgaben,
Belohnungen einlösen, aber nichts freigeben. Auf Wunsch müssen Eltern alles
bestätigen, was am Tablet abgehakt wurde. Eltern können zudem jederzeit in
ihrer Ansicht für ein Kind abhaken.

## Kostenlos

Sternchenplan ist komplett kostenlos, ohne Testphase, Lizenz oder Abo. Alle
Funktionen sind an: Aufgaben, Punkte, Belohnungen, Erinnerungen,
Familientablet, Internetsperre (FRITZ!Box & Co.), Fotonachweis, Aufgaben
übernehmen, Lautsprecher-Ansagen und Abwesenheit mit Vertretung.

Wer von 0.14 kommt: Ein eingetragener Lizenzschlüssel wird einfach nicht mehr
gebraucht. Es muss nichts umgestellt werden.

## Level, Serien und Abzeichen

Jeder Stern bringt Kinder im Level weiter (Starter, Helfer, Macher, Profi …).
Das Level zählt alle jemals verdienten Sterne. Wer Sterne für eine Belohnung
ausgibt, fällt also nicht zurück.

- **Serie 🔥:** Tage in Folge, an denen das Kind mindestens eine Aufgabe
  erledigt hat. Sie reißt erst, wenn ein ganzer Tag ohne Erledigtes vergeht.
- **15 Abzeichen:** z. B. „Fleißige Biene“ (10 Aufgaben), „Am Ball“ (3 Tage in
  Folge), „Retter in der Not“ (Geschwistern geholfen), „Frühaufsteher“.
- **Feiern:** Neues Level oder Abzeichen gibt eine große Anzeige in der Karte
  und eine Push-Nachricht ans Kind.

Für eigene Automationen gibt es die Ereignisse `sternchenplan_level_up`
(`member`, `level`, `title`) und `sternchenplan_badge` (`member`, `badge`,
`name`, `emoji`). Der Sterne-Sensor jedes Kindes hat die Attribute `level`,
`stars_total`, `streak`, `best_streak` und `badges`.

Beim Update von 0.15 schätzt Sternchenplan den bisherigen Stand aus Sternen,
Einlösungen und dem Verlauf. Abzeichen, die schon verdient sind, gibt es still
dazu, ohne Feier-Flut.

## Sparziel und Familienziel

- **Sparziel 🎯:** Jedes Kind kann eine Belohnung als Ziel markieren (Knopf
  „Als Ziel“ unter der Belohnung). Oben in der Kinderansicht steht dann, wie
  viele Sterne noch fehlen. Sobald es reicht, kommt eine Push-Nachricht.
- **Familienziel 🏰:** Eltern legen unter *Belohnungen* ein gemeinsames Ziel
  an, z. B. „Freizeitpark, 500 Sterne“. Alle Sterne, die die Kinder verdienen,
  zählen dafür. Niemandem wird etwas abgezogen. Ist das Ziel erreicht, gibt es
  eine Nachricht an alle.

Dienste: `sternchenplan.set_goal`, `sternchenplan.set_family_goal`,
`sternchenplan.clear_family_goal`. Ereignisse: `sternchenplan_goal_ready`,
`sternchenplan_family_goal`.

## Taschengeld

Im Eltern-Reiter **Familie** führt Sternchenplan für jedes Kind ein
Taschengeld-Konto. Das Geld selbst liegt nicht in Sternchenplan: Ihr zahlt bar
oder per Überweisung aus und tippt dann auf „Auszahlen“.

- **Sterne tauschen:** Mit einem Kurs, z. B. 10 Sterne = 1 €, tauschen Kinder
  Sterne selbst in Taschengeld. Kurs 0 schaltet das aus.
- **Wochengeld:** Ein fester Betrag pro Kind, gutgeschrieben am Zahltag
  (Standard Sonntag). Das Kind bekommt eine Push-Nachricht.
- **Buchen:** Bonus von Oma oder Abzug für Kaputtes, mit Notiz im Verlauf.

Dienste: `set_money`, `set_allowance`, `exchange_stars`, `payout`,
`adjust_money`.

## Routinen und Vorlagen

- **Routinen:** Jede Aufgabe kann Schritte haben, z. B. die Morgenroutine mit
  Aufstehen, Anziehen, Zähne putzen und Bett machen. Das Kind hakt jeden
  Schritt einzeln ab. Mit dem letzten Schritt gilt die Aufgabe als gemeldet.
  Bei einer Routine mit Fotonachweis tippt das Kind danach selbst auf
  „Foto & erledigt“. Dienst: `sternchenplan.check_step`.
- **Vorlagen nach Alter:** Unter *Aufgaben › 📚 Vorlagen* gibt es 24 fertige
  Aufgaben und Routinen, sortiert nach Alter (4–6, 7–9, 10–12, ab 13). Ein Tipp
  füllt das Formular mit Namen, Sternen, Wiederholung, Uhrzeit und
  Mindestalter. Ihr wählt nur noch, wer sie macht.

## Ferien-Pause, Schultage und Bilder-Modus

- **Ferien-Pause:** Im Reiter „Familie“ trägst du Ferien von–bis ein. In der Zeit ist nichts fällig, nichts wird gesperrt und keine Serie reißt. Danach rücken die Fristen automatisch nach. Geht auch per Dienst `sternchenplan.set_pause` / `sternchenplan.end_pause`.
- **Nur an bestimmten Tagen:** Tägliche Aufgaben kannst du auf Wochentage beschränken, z. B. „Schultasche packen“ nur Mo–Fr. Die Vorlagen für Schulsachen setzen das schon.
- **Bilder-Modus:** Für Kinder, die noch nicht lesen. Große Bildkacheln statt Text, ein 🔊-Knopf liest die Aufgabe vor (im Browser, ohne Internetdienst). Einschalten in der Elternansicht beim Kind („Bilder-Modus“) oder per `sternchenplan.set_picture_mode`. Jede Aufgabe kann ein eigenes Symbol bekommen.

## Wetter und Wochenbericht

- **Draußen-Aufgaben:** Hak bei einer Aufgabe „Draußen“ an (z. B. Rasen mähen, Laub rechen). Regnet es zur Frist, wird sie nicht überfällig und sperrt nichts, sondern rückt einen Tag weiter. Der Wochentakt bleibt dabei gleich. Welche Wetter-Entität zählt, stellst du im Reiter „Einstellungen“ ein (oder per `sternchenplan.set_weather`). Als nass gilt: Regen, Schauer, Schnee, Gewitter, Hagel.
- **Wochenbericht:** Eltern sehen unter „Heute“, wie die Woche lief: erledigt, verpasst, verdiente Sterne und wer am fleißigsten war. Einmal pro Woche (Standard: Sonntag 18 Uhr) kommt das als Push. Tag und Uhrzeit stellst du an derselben Stelle ein, `-1` schaltet ihn ab. Für eigene Automationen gibt es das Ereignis `sternchenplan_week_report` und den Dienst `sternchenplan.send_report`.

## Bonus und Abzug

In der Elternansicht hat jedes Kind unter „Heute“ den Knopf „± Sterne“. Damit gibst du Extra-Sterne („Oma beim Tragen geholfen“) oder ziehst welche ab („Streit“). Fertige Schnellknöpfe legst du im Reiter „Einstellungen“ an. Das Kind bekommt eine Push-Nachricht mit dem Grund und sieht den Verlauf in seiner Ansicht.

Ein Abzug geht nie unter null und kostet kein Level: Was ein Kind erreicht hat, bleibt. Bonus-Sterne zählen dagegen fürs Level und fürs Familienziel. Für Automationen gibt es den Dienst `sternchenplan.give_stars` und das Ereignis `sternchenplan_stars`.

## Freigeben direkt aus der Push-Nachricht

Meldet ein Kind eine Aufgabe, die eine Freigabe braucht, oder will es eine Belohnung einlösen, bekommen die Eltern eine Push-Nachricht mit zwei Knöpfen: „✓ Freigeben“ und „Ablehnen“. Ist ein Fotonachweis dabei, ist das Foto gleich in der Nachricht. Ein Tipp reicht, die App muss nicht geöffnet werden. Sobald ein Elternteil entschieden hat, verschwindet die Frage auch vom Handy des anderen.

Das klappt mit der Home-Assistant-App (Push-Dienst `notify.mobile_app_…`). Geprüft wird serverseitig wie überall: Nur ein Elternkonto kann freigeben. Andere Push-Dienste bekommen die Nachricht ohne Knöpfe.

## Kalender

Sternchenplan legt Kalender in Home Assistant an: „Aufgaben“ für die ganze Familie und „Aufgaben Lucas“ usw. für jedes Kind. Darin steht jede Frist der nächsten Wochen, auch Wiederholungen, Wochentage und wer bei Rotation dran ist. Ferien-Pausen bleiben leer. So siehst du alles im HA-Kalender, auf einem Wand-Tablet mit Kalenderkarte oder kannst Automationen auf „Termin beginnt“ bauen.

## Abhaken ohne Bildschirm: NFC-Aufkleber und Sprache

**NFC-Aufkleber:** Kleb einen NFC-Aufkleber (ein paar Cent das Stück) an die Mülltonne, den Hamsterkäfig oder die Spülmaschine. In der Elternansicht öffnest du die Aufgabe, tippst auf „Aufkleber anlernen“ und hältst dein Handy mit der Home-Assistant-App an den Aufkleber. Danach reicht es, wenn das Kind sein Handy dranhält: Die Aufgabe ist gemeldet, und es kommt eine Bestätigung. Mehrere Aufgaben dürfen denselben Aufkleber haben. Freigabe gilt wie sonst auch. Aufgaben mit Fotonachweis gehen nur in der App.

**Sprache:** Mit Home Assistant Assist (Handy, Sprach-Satellit, Wear OS) versteht Sternchenplan von selbst:

- „Ich habe den Müll rausgebracht“ / „Lucas hat den Tisch gedeckt“
- „Was muss ich noch machen?“ / „Was muss Osmo noch machen?“
- „Wie viele Sterne habe ich?“

Spricht ein Kind über sein eigenes Konto, kann es nur für sich melden. Über einen Lautsprecher ohne Konto sagt es seinen Namen dazu.

## Das Haus prüft selbst

Jede Aufgabe kann mit einem Gerät oder Sensor aus Home Assistant verbunden werden, ganz ohne Automation. Das stellst du in der Aufgabe unter „🏠 Das Haus prüft selbst“ ein:

- **Erledigt, wenn …:** Der Saugroboter meldet „docked“, also ist „Saugroboter leeren“ erledigt. Gutgeschrieben wird dem Kind, das gerade dran ist. Eine Freigabe braucht es dafür nicht, das Haus hat ja selbst nachgesehen. Sind mehrere Kinder gleichzeitig dran, wird nichts gutgeschrieben, weil unklar ist, wer es war.
- **Jetzt dran, wenn …:** Die Spülmaschine geht auf „off“, dann bekommt das Kind „Jetzt bist du dran: Spülmaschine ausräumen“.

## So einfach wie möglich

- **In einer Minute startklar:** Ist noch nichts angelegt, schlägt Sternchenplan unter „Heute“ ein Startpaket nach Alter vor: gemeinsame Aufgaben reihum (Tisch decken, Spülmaschine, Müll, Staubsaugen), eigene je Kind (Bett machen, Zimmer) und vier Belohnungen. Ein Tipp auf „Alles anlegen“ genügt.
- **Kurzes Formular:** Für eine neue Aufgabe reichen Name, wer, wie oft und Sterne. Alles Weitere steht unter „Mehr Optionen“. Ohne Frist nimmt Sternchenplan 18 Uhr.
- **💡 Hilfe-Tipps:** Unter „Einstellungen“ eingeschaltet, erklärt ein Satz oben jeden Reiter.

## Designs zum Aussuchen

Jedes Kind wählt in seinem Reiter „🙂 Ich“ unter „🎨 Mein Design“ sein eigenes Aussehen: 🚀 Weltraum, 🌴 Dschungel, 🐠 Ozean, 🍭 Bonbon oder ✨ Klar. Eltern finden ihr Design unter „Einstellungen“ und können zusätzlich „Elegant“ wählen. Die Wahl wird in Home Assistant gespeichert und gilt auf jedem Gerät. Per Dienst geht es auch: `sternchenplan.set_theme`.

## Extras: Was ihr nutzen wollt

Im Willkommens-Assistenten (Schritt 2) und später im Reiter **Einstellungen** schaltet ihr an oder aus, was ihr braucht. Was aus ist, verschwindet aus der Ansicht. Nichts davon ist Pflicht, und jede Wahl lässt sich später wieder ändern, auch die Foto- und Push-Einstellungen aus dem Assistenten (Einstellungen → Datenschutz).

- **🏆 Level und Abzeichen:** Level, Serien (🔥) und Abzeichen. Aus: keine Level-Leiste, keine Abzeichen, keine Level-Pushes.
- **🤝 Geschwistern helfen:** Abends Aufgaben der Geschwister übernehmen und mehr Sterne holen. Aus: Übernehmen ist auch per Dienst gesperrt.

- **🐉 Sternchen-Haustier:** Jedes Kind sucht sich ein Tier aus (Drache, Katze, Hund, Einhorn, Dino, Panda, Fuchs, Eule) und gibt ihm einen Namen. Es schlüpft aus dem Ei und wächst mit jedem Level. Es freut sich, wenn alles geschafft ist, hat Hunger, wenn noch etwas offen ist, ist traurig bei Überfälligem und schläft nachts.
- **💡 Zimmerlampe als Ampel:** Pro Person eine Lampe. Sie leuchtet ein paar Sekunden orange bei Erinnerungen und überfälligen Aufgaben und grün, wenn heute alles geschafft ist. Danach ist sie wieder genau wie vorher. Zwischen 21 und 7 Uhr bleibt sie in Ruhe.
- **📺 Bildschirmzeit verdienen:** Eltern legen fest, wie viele Minuten ein Stern wert ist und wie viel höchstens pro Tag geht, und wählen pro Kind Geräte (Fernseher-Steckdose, Konsole, Internet-Schalter). Das Kind tauscht Sterne gegen 10, 20, 30 oder 60 Minuten. Die Geräte gehen an und danach wieder aus, 5 Minuten vorher kommt ein Hinweis. Bei überfälligen Aufgaben gibt es keine Bildschirmzeit.
- **🧺 Geräte melden Aufgaben:** Aufgaben mit Wiederholung „bei Bedarf“ ruhen, bis ein Gerät sie fällig macht (unter „Das Haus prüft selbst“ → „Jetzt dran, wenn …“, z. B. Waschmaschine fertig). Wer dran ist, bekommt sofort Bescheid und hat 2 Stunden Zeit. Reihum geht es danach weiter. Eltern können sie auch per Knopf oder Dienst `sternchenplan.trigger_chore` fällig machen.
- **🗳️ Familienrat:** Eltern stellen eine Frage mit 2 bis 6 Möglichkeiten. Alle stimmen ab, auch die Eltern. Sind alle fertig oder ist die Zeit um, bekommen alle das Ergebnis per Push.
- **🏅 Monatsurkunde:** Am Monatsersten gibt es pro Kind eine Urkunde mit erledigten Aufgaben, Sternen, bester Serie, Lieblingsaufgabe und neuen Abzeichen, zum Ansehen und Ausdrucken.
- **👨‍👩‍👧 Eltern machen mit:** Eltern mit eigenen Aufgaben erscheinen bei „Heute“, in der Wochenwertung und auf der Urkunde. Ihre Sterne zählen fürs Familienziel.
- **💶 Taschengeld** und **🎯 Familienziel** lassen sich ebenfalls abschalten.

Neue Ereignisse für eigene Automationen: `sternchenplan_all_done`, `sternchenplan_screen_start`, `sternchenplan_screen_ending`, `sternchenplan_screen_over`, `sternchenplan_vote_started`, `sternchenplan_vote_result`, `sternchenplan_month_report`.

## Fotogalerie

Behaltet ihr Fotos (Einstellungen → Datenschutz → „Fotos nach dem Freigeben löschen“ aus), sammelt Sternchenplan sie im Eltern-Reiter **Familie** unter „📷 Fotos“: neueste zuerst, mit Aufgabe, Kind und Uhrzeit, filterbar nach Kind. Ein Tipp öffnet das Foto groß, mit Blättern und Löschen. Die Galerie sehen nur Eltern, die Links gelten jeweils eine Stunde. Nach der Löschfrist (Integrations-Optionen) verschwinden Fotos automatisch, auch aus der Galerie. Wird eine Person gelöscht, gehen alle ihre Fotos mit. Dienst: `sternchenplan.delete_photo`.

## Datenschutz

- **Alles bleibt zu Hause.** Sternchenplan läuft komplett in eurem Home Assistant. Es gibt keine Cloud, kein Konto und keine Statistik, und die Integration schickt nichts ins Internet.
- **Fotos** sehen nur Eltern, über Links, die eine Stunde gelten. Standardmäßig werden sie nach der Entscheidung gelöscht, sonst nach der eingestellten Frist.
- **Sparsame Push-Nachrichten:** Pushes ans Handy laufen über Google (Android) bzw. Apple (iPhone). Eingeschaltet (im Assistenten oder unter Einstellungen → Datenschutz) stehen darin keine Namen, Aufgaben oder Fotos mehr, nur „Schau in Sternchenplan nach“. Die Knöpfe zum Freigeben bleiben. Hinweis: Ansagen über Alexa laufen über Amazon.
- **Daten einer Person:** Unter Einstellungen → Datenschutz lässt sich alles über eine Person als Datei exportieren oder komplett löschen (Verlauf, Sterne, Taschengeld, Einlösungen, Fotos). Dienst: `sternchenplan.forget_member`.
- **Alles löschen:** Wer die Integration entfernt, löscht damit alle Familiendaten.

## Trinkgeld

Gefällt euch Sternchenplan? Über ein kleines Trinkgeld freue ich mich sehr.
Der Link folgt in Kürze.

## Seitenleiste und Dashboard-Karte

Nach der Einrichtung gibt es den Menüpunkt **Sternchenplan** in der Seitenleiste. Eltern sehen dort die Eltern-Ansicht, Kinder ihre eigenen Aufgaben.

Wer die Karte zusätzlich auf ein eigenes Dashboard legen will (z. B. Küchen-Tablet), kann das ohne Ressource tun:

```yaml
type: custom:sternchenplan-card
mode: auto        # auto | kind | eltern
member: Lucas     # optional: immer dieses Kind zeigen
readonly: false   # true: nur anzeigen, z. B. Küchen-Tablet
title: Sternchenplan
```

- **Kinder** haben drei Reiter: **✅ Heute** zeigt nur, was noch offen ist, mit Erledigt-Knopf (bei Fotopflicht „Foto & erledigt“). Was geschafft ist, klappt unter „✓ 3 heute geschafft“ zusammen. Ab 16:30 erscheint „Geschwistern helfen“. **🎁 Belohnen** zeigt Sparziel, Familienziel, Bildschirmzeit, Belohnungen und Taschengeld (die Zahl am Reiter sagt, wie viele Belohnungen schon drin sind). **🙂 Ich** zeigt Haustier, Level, Abzeichen, Verlauf und Design.
- **Eltern** haben fünf Reiter: **Heute** (Überblick, Freigaben mit Foto-Vorschau, jedes Kind als kompakte Karte mit „2 offen · Als Nächstes …“, ein Tipp klappt die Aufgaben auf), **Aufgaben**, **Belohnungen**, **Familie** (Ferien, Abwesenheit, Taschengeld) und **Einstellungen** (Wetter, Wochenbericht, Schnellknöpfe, Design, Hilfe-Tipps, Zusatzfunktionen, Datenschutz). Abwesend melden geht auch direkt über das ⋯-Menü beim Kind. Auf dem Handy passen alle fünf Reiter ohne Wischen nebeneinander.

## Rechte (serverseitig geprüft)

| Wer | Darf |
| --- | --- |
| Eltern-Mitglied oder HA-Admin | alles |
| Kind | nur eigene, aktuell zugeteilte Aufgaben melden, eigene Meldung zurücknehmen, ab 16:30 Aufgaben der Geschwister für sich übernehmen; Fotos nur hochladen, nicht ansehen |
| Automationen (ohne Benutzer) | alles |
| unbekanntes Nicht-Admin-Konto | nichts |

## Aufbau

- `core/` – Regeln und Datenmodell, ohne Home-Assistant-Import, separat testbar
- `services.py` – Dienste, ermittelt den Aufrufer und prüft Rechte über den Kern
- `sensor.py`, `config_flow.py` – HA-Oberfläche
- Daten in `.storage/sternchenplan.<entry_id>`

## Tests

```bash
pip install -r requirements_test.txt
pytest
```

Getestet mit Home Assistant 2026.2 (Testpaket). Vor einer Veröffentlichung gegen die aktuelle HA-Version testen.

## Offen

- Erinnerung nur, wenn das Kind zu Hause ist
- Karten-Editor in der Oberfläche
- Weitere Funktionen: weitere Sprachen
