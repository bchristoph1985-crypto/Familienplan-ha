# Familienplan (Arbeitstitel)

Home-Assistant-Integration für Familienaufgaben. Läuft komplett lokal, ohne Cloud.

Stand: Phase 1, Grundgerüst (Version 0.1.0). Noch nicht für den Alltag gedacht.

## Was schon geht

- Einrichtung über *Einstellungen → Geräte & Dienste → Integration hinzufügen → Familienplan*
- Familienmitglieder (Eltern/Kind) über *Konfigurieren* anlegen, optional mit HA-Konto verknüpft
- Aufgaben: einmalig, täglich, wöchentlich, alle 2 Wochen; Reihum-Rotation; Punkte; Elternfreigabe
- Überfällig-Erkennung (jede Minute)
- Sensoren: Punkte je Mitglied, Status je Aufgabe
- Dienste: `familienplan.create_chore`, `delete_chore`, `claim_chore`, `undo_claim`, `approve_chore`, `reject_chore`

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
- Erinnerungen, Abwesenheit/Vertretung, Karten fürs Dashboard (Phase 1/2)
- Pro-Funktionen und Lizenzschlüssel (Phase 3)
