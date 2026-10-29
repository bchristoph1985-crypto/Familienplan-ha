# Sternchenplan

Home-Assistant-Integration für Familienaufgaben. Läuft komplett lokal, ohne Cloud.

Stand: Version 0.18.0. Noch nicht für den Alltag gedacht.

## Umstieg vom Arbeitstitel „Familienplan“

Bis Version 0.13.0 hieß die Integration `familienplan`. Ab 0.14.0 heißt sie `sternchenplan`. Daten werden nicht übernommen, weil es noch keine echten Nutzer gibt:

1. Unter Einstellungen → Geräte & Dienste die Integration „Familienplan“ löschen.
2. Den Ordner `custom_components/familienplan` löschen und `custom_components/sternchenplan` hineinkopieren.
3. Home Assistant neu starten und „Sternchenplan“ neu einrichten.

## Was schon geht

- **Einrichtung in sieben kurzen Schritten** über *Einstellungen → Geräte & Dienste → Integration hinzufügen → Sternchenplan*:
  1. Name der Familie
  2. Wer gehört dazu: die Personen aus Home Assistant sind schon angehakt, Kinder ohne eigenes Konto einfach mit Namen eintragen
  3. Wer sind die Eltern: HA-Administratoren sind vorgeschlagen
  4. Wie alt sind die Kinder (freiwillig)
  5. Startaufgaben ankreuzen, passend zum Alter vorgeschlagen (z. B. Spülmaschine reihum ab 7, Zimmer aufräumen je Kind)
  6. Belohnungen aus Vorschlägen ankreuzen (z. B. Filmabend aussuchen, 40 Punkte)
  7. Datenschutz: Fotos sofort nach der Bestätigung löschen oder 7 Tage behalten

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
- **Datenschutz bei Fotos**: Die Familie wählt im Assistenten (später unter *Konfigurieren → Regeln*), ob Fotos sofort nach Bestätigen oder Ablehnen gelöscht werden (Standard) oder bis zu 7 Tage (einstellbar) bleiben. Nimmt ein Kind seine Meldung zurück, wird das Foto immer sofort gelöscht.
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

Im Eltern-Reiter **Geld** führt Sternchenplan für jedes Kind ein
Taschengeld-Konto. Das Geld selbst liegt nicht in Sternchenplan: Ihr zahlt bar
oder per Überweisung aus und tippt dann auf „Auszahlen“.

- **Sterne tauschen:** Mit einem Kurs, z. B. 10 Sterne = 1 €, tauschen Kinder
  Sterne selbst in Taschengeld. Kurs 0 schaltet das aus.
- **Wochengeld:** Ein fester Betrag pro Kind, gutgeschrieben am Zahltag
  (Standard Sonntag). Das Kind bekommt eine Push-Nachricht.
- **Buchen:** Bonus von Oma oder Abzug für Kaputtes, mit Notiz im Verlauf.

Dienste: `set_money`, `set_allowance`, `exchange_stars`, `payout`,
`adjust_money`.

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

- **Kinder** sehen ihre Aufgaben für heute, Punkte und einen Erledigt-Knopf (bei Fotopflicht „Foto & erledigt“). Ab 16:30 erscheint „Geschwistern helfen“ mit Aufgaben, die sie übernehmen können.
- **Eltern** sehen Reiter für Heute (alle Kinder, für ein Kind abhaken), Freigaben, Aufgaben (anlegen, bearbeiten, löschen) und Abwesend (eintragen, beenden). Bei Freigaben sehen Eltern das Foto als Vorschau.

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
- Weitere Funktionen: Routinen, Vorlagen nach Alter
