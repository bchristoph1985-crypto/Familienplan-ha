# Familienplan (Arbeitstitel)

Home-Assistant-Integration für Familienaufgaben. Läuft komplett lokal, ohne Cloud.

Stand: Version 0.2.0. Noch nicht für den Alltag gedacht.

## Was schon geht

- Einrichtung über *Einstellungen → Geräte & Dienste → Integration hinzufügen → Familienplan*
- Familienmitglieder (Eltern/Kind) über *Konfigurieren* anlegen, optional mit HA-Konto verknüpft
- Aufgaben: einmalig, täglich, wöchentlich, alle 2 Wochen; Reihum-Rotation; Punkte; Elternfreigabe
- Überfällig-Erkennung (jede Minute)
- Abwesenheit (z. B. Klassenfahrt, krank) mit Beginn, Ende und Vertretung. Bei Rotation ist automatisch das nächste Kind dran; ohne Rotation übernimmt die Vertretung. Ist niemand da, ruht die Aufgabe und wird nicht überfällig.
- Erinnerungen per HA-Push an Kinder zu einstellbaren Uhrzeiten (Standard 15:00, 17:00, 18:30), nur wenn noch etwas offen ist; Sammelnachricht an Eltern (Standard 19:00)
- Sensoren: Punkte je Mitglied, Status je Aufgabe
- Dienste: `familienplan.create_chore`, `delete_chore`, `claim_chore`, `undo_claim`, `approve_chore`, `reject_chore`, `set_absence`, `end_absence`

## Dashboard-Karte

Die Karte wird von der Integration mitgeliefert, eine Ressource muss man nicht anlegen.

```yaml
type: custom:familienplan-card
mode: auto        # auto | kind | eltern
member: Lucas     # optional: immer dieses Kind zeigen
readonly: false   # true: nur anzeigen, z. B. Küchen-Tablet
title: Familienplan
```

- **Kinder** sehen ihre Aufgaben für heute, Punkte und einen Erledigt-Knopf.
- **Eltern** sehen Reiter für Heute (alle Kinder, für ein Kind abhaken), Freigaben, Aufgaben (anlegen, löschen) und Abwesend (eintragen, beenden).

## Rechte (serverseitig geprüft)

| Wer | Darf |
| --- | --- |
| Eltern-Mitglied oder HA-Admin | alles |
| Kind | nur eigene, aktuell zugeteilte Aufgaben melden, eigene Meldung zurücknehmen |
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
- Karten-Editor in der Oberfläche, Aufgaben bearbeiten statt nur löschen
- Pro-Funktionen und Lizenzschlüssel (Phase 3)
