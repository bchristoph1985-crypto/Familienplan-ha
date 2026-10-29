"""Aufgaben im Home-Assistant-Kalender."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.core import HomeAssistant

from custom_components.sternchenplan.core import SYSTEM, Family, Recurrence

from .test_core import NOW, by_name, family  # noqa: F401
from .test_reminders import auto_enable_custom_integrations, entry  # noqa: F401

# NOW: Montag, 2. November 2026, 17:00 UTC


def test_wiederholungen_und_rotation(family: Family) -> None:  # noqa: F811
    lucas, osmo = by_name(family, "Lucas"), by_name(family, "Osmo")
    spuelen = family.create_chore(
        SYSTEM, "Spülen", [lucas.id, osmo.id], rotation=True,
        recurrence=Recurrence.DAILY, due=NOW + timedelta(hours=2),
    )
    family.create_chore(
        SYSTEM, "Schultasche", [lucas.id], recurrence=Recurrence.DAILY,
        due=NOW + timedelta(hours=1), weekdays=[0, 1, 2, 3, 4],
    )
    week = family.occurrences(NOW, NOW + timedelta(days=7))
    rotation = [who[0] for _, c, who in week if c is spuelen]
    assert rotation == [lucas.id, osmo.id] * 3 + [lucas.id]
    schul = [d.weekday() for d, c, _ in week if c.name == "Schultasche"]
    assert schul == [0, 1, 2, 3, 4]  # kein Wochenende
    assert len(family.occurrences(NOW, NOW + timedelta(days=7), osmo.id)) == 3

    family.set_pause(SYSTEM, NOW + timedelta(days=2), NOW + timedelta(days=4))
    paused = family.occurrences(NOW, NOW + timedelta(days=7))
    assert len(paused) == len(week) - 4


def test_einmalige_aufgabe(family: Family) -> None:  # noqa: F811
    lucas = by_name(family, "Lucas")
    family.create_chore(SYSTEM, "Keller", [lucas.id], due=NOW + timedelta(days=1))
    family.create_chore(SYSTEM, "Ohne Frist", [lucas.id])
    found = family.occurrences(NOW, NOW + timedelta(days=30))
    assert [c.name for _, c, _ in found] == ["Keller"]


async def test_kalender_entitaeten(hass: HomeAssistant, entry) -> None:  # noqa: F811
    await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()
    states = {s.entity_id: s for s in hass.states.async_all("calendar")}
    assert any(e.endswith("_aufgaben") for e in states)
    lucas_cal = next(e for e in states if "lucas" in e)
    assert states[lucas_cal].attributes["message"].endswith("Müll")
    response = await hass.services.async_call(
        "calendar", "get_events",
        {"entity_id": lucas_cal, "duration": {"days": 3}},
        blocking=True, return_response=True,
    )
    events = response[lucas_cal]["events"]
    assert [e["summary"] for e in events].count("⭐ Müll") == 3
