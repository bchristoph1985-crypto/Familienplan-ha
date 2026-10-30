"""Draußen-Aufgaben bei Regen und der Wochenbericht."""

from __future__ import annotations

from datetime import timedelta

import pytest
from pytest_homeassistant_custom_component.common import (
    async_fire_time_changed,
    async_mock_service,
)

from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from custom_components.sternchenplan.const import DOMAIN
from custom_components.sternchenplan.core import (
    SYSTEM,
    ChoreState,
    Family,
    FamilyError,
    PermissionDenied,
    Recurrence,
)

from .test_core import NOW, actor, by_name, family  # noqa: F401
from .test_reminders import auto_enable_custom_integrations, entry  # noqa: F401

# NOW: Montag, 2. November 2026, 17:00 UTC


def test_regen_verschiebt_draussen_aufgabe(family: Family) -> None:  # noqa: F811
    finn = by_name(family, "Finn")
    family.set_devices(SYSTEM, finn.id, ["switch.ps5"])
    rasen = family.create_chore(
        SYSTEM, "Rasen mähen", [finn.id], recurrence=Recurrence.WEEKLY,
        due=NOW + timedelta(hours=1), outdoor=True,
    )
    family.bad_weather = True
    later = NOW + timedelta(hours=2)
    assert family.refresh(later)
    assert rasen.state is ChoreState.OPEN  # nicht überfällig, keine Sperre
    assert rasen.due == NOW + timedelta(days=1, hours=1)
    assert rasen.weather_shift == 1
    assert not family.should_lock(finn.id, later)
    assert rasen.history[-1]["event"] == "postponed"

    # Erledigt am Dienstag: der Wochentakt bleibt am Montag
    family.bad_weather = False
    family.claim(actor(family, "Finn"), rasen.id, finn.id, NOW + timedelta(days=1))
    assert rasen.due == NOW + timedelta(days=7, hours=1)
    assert rasen.weather_shift == 0


def test_trocken_oder_drinnen_wird_ueberfaellig(family: Family) -> None:  # noqa: F811
    finn = by_name(family, "Finn")
    drinnen = family.create_chore(SYSTEM, "Spülen", [finn.id], due=NOW + timedelta(hours=1))
    family.bad_weather = True
    family.refresh(NOW + timedelta(hours=2))
    assert drinnen.state is ChoreState.OVERDUE
    assert drinnen.history[-1] == {
        "event": "missed", "member": finn.id, "at": (NOW + timedelta(hours=2)).isoformat()
    }
    family.update_chore(SYSTEM, drinnen.id, NOW, outdoor=True)
    assert Family.from_dict(family.to_dict()).chores[drinnen.id].outdoor


def test_wochenbericht(family: Family) -> None:  # noqa: F811
    finn = by_name(family, "Finn")
    paul = by_name(family, "Paul")
    a = family.create_chore(SYSTEM, "Müll", [finn.id], points=3)
    family.claim(actor(family, "Finn"), a.id, finn.id, NOW)
    b = family.create_chore(SYSTEM, "Tisch", [paul.id], due=NOW - timedelta(days=2))
    family.refresh(NOW - timedelta(days=1))
    alt = family.create_chore(SYSTEM, "Alt", [paul.id], points=9)
    family.claim(actor(family, "Paul"), alt.id, paul.id, NOW - timedelta(days=10))
    report = {r["name"]: r for r in family.week_report(NOW + timedelta(hours=1))}
    assert report["Finn"]["done"] == 1 and report["Finn"]["stars"] == 3
    assert report["Paul"]["done"] == 0 and report["Paul"]["missed"] == 1
    assert "Papa" not in report
    assert b.state is ChoreState.OVERDUE


def test_einstellungen_nur_eltern(family: Family) -> None:  # noqa: F811
    with pytest.raises(PermissionDenied):
        family.set_report(actor(family, "Finn"), 0, 18)
    with pytest.raises(FamilyError):
        family.set_report(SYSTEM, 7, 18)
    family.set_report(SYSTEM, -1, 8)
    family.set_weather(SYSTEM, "weather.home")
    restored = Family.from_dict(family.to_dict())
    assert (restored.report_day, restored.report_hour, restored.weather_entity) == (-1, 8, "weather.home")


async def test_wetter_und_bericht_in_ha(hass: HomeAssistant, entry, freezer) -> None:  # noqa: F811
    papa_calls = async_mock_service(hass, "notify", "papa_handy")
    fam = entry.runtime_data.family
    hass.states.async_set("weather.home", "rainy")
    await hass.services.async_call(DOMAIN, "set_weather", {"entity": "weather.home"}, blocking=True)
    assert fam.bad_weather
    hass.states.async_set("weather.home", "sunny")
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(minutes=1))
    await hass.async_block_till_done()
    assert not fam.bad_weather

    await hass.services.async_call(DOMAIN, "set_report", {"day": 6, "hour": 18}, blocking=True)
    # Sonntag, 8. November, 18:00
    freezer.move_to("2026-11-08 18:00:00+00:00")
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    reports = [c for c in papa_calls if c.data["title"] == "📊 Wochenbericht"]
    assert len(reports) == 1
    assert "Finn: 0 erledigt, " in reports[0].data["message"]
    await hass.services.async_call(DOMAIN, "send_report", {}, blocking=True)
    assert len([c for c in papa_calls if c.data["title"] == "📊 Wochenbericht"]) == 2

