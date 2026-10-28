# Familienplan (Arbeitstitel)

Home-Assistant-Integration für Familienaufgaben. Läuft komplett lokal, ohne Cloud.

Stand: Version 0.5.0. Noch nicht für den Alltag gedacht.

## Was schon geht

- Einrichtung über *Einstellungen → Geräte & Dienste → Integration hinzufügen → Familienplan*
- Familienmitglieder (Eltern/Kind) über *Konfigurieren* anlegen, optional mit HA-Konto verknüpft
- Aufgaben: einmalig, täglich, wöchentlich, alle 2 Wochen; Reihum-Rotation; Punkte; Elternfreigabe
- Überfällig-Erkennung (jede Minute)
- Abwesenheit (z. B. Klassenfahrt, krank) mit Beginn, Ende und Vertretung. Bei Rotation ist automatisch das nächste Kind dran; ohne Rotation übernimmt die Vertretung. Ist niemand da, ruht die Aufgabe und wird nicht überfällig.
- Erinnerungen per HA-Push an Kinder zu einstellbaren Uhrzeiten (Standard 15:00, 17:00, 18:30), nur wenn noch etwas offen ist; Sammelnachricht an Eltern (Standard 19:00)
- Sensoren: Punkte je Mitglied, Status je Aufgabe
- **Internetsperre** (ausgeschaltet bis man sie aktiviert): Eltern wählen je Kind Internet-Schalter von Freizeitgeräten (z. B. FRITZ!Box „Internetzugang“). Hat das Kind im Sperrzeitraum (Standard 20:00–05:00) überfällige Aufgaben, gehen diese Schalter aus. Sie gehen wieder an, sobald alles erledigt oder gemeldet ist, spätestens am Ende des Zeitraums. Schaltet jemand ein gesperrtes Gerät wieder an, wird es nach spätestens einer Minute erneut gesperrt. Eltern können eine Freikarte geben. Abwesende Kinder werden nie gesperrt. Familienplan gibt nur Geräte frei, die es selbst gesperrt hat, und fasst keine anderen Schalter an.
- **Fotonachweis** je Aufgabe: Kinder machen beim Abhaken ein Foto (Kamera öffnet sich in der Karte). Fotos bleiben lokal in `config/familienplan_photos`, sind nicht öffentlich, nur Eltern sehen sie über einen kurz gültigen Link. Nach 7 Tagen (einstellbar) werden sie gelöscht.
- **Aufgaben übernehmen („wegmopsen“)**: Ab 16:30 können Kinder offene Aufgaben der Geschwister übernehmen und bekommen die Punkte, ab 19:00 doppelt. Höchstens 2 pro Tag. Bei Reihum-Aufgaben geht die Reihenfolge danach normal weiter. Zeiten und Anzahl unter *Konfigurieren → Regeln*.
- Dienste: `familienplan.create_chore`, `update_chore`, `delete_chore`, `claim_chore`, `take_over_chore`, `undo_claim`, `approve_chore`, `reject_chore`, `set_absence`, `end_absence`, `set_devices`, `grant_pass`, `revoke_pass`

## Dashboard-Karte

Die Karte wird von der Integration mitgeliefert, eine Ressource muss man nicht anlegen.

```yaml
type: custom:familienplan-card
mode: auto        # auto | kind | eltern
member: Lucas     # optional: immer dieses Kind zeigen
readonly: false   # true: nur anzeigen, z. B. Küchen-Tablet
title: Familienplan
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
- Daten in `.storage/familienplan.<entry_id>`

## Tests

```bash
pip install -r requirements_test.txt
pytest
```

Getestet mit Home Assistant 2026.2 (Testpaket). Vor einer Veröffentlichung gegen die aktuelle HA-Version testen.

## Offen

- Name und Lizenz (siehe Phase-0-Dokument)
- Erinnerung nur, wenn das Kind zu Hause ist; Ansagen über Lautsprecher
- Karten-Editor in der Oberfläche
- Pro-Funktionen und Lizenzschlüssel (Phase 3)
