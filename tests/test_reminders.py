"""Erinnerungen und Abwesenheits-Dienste in Home Assistant."""

from __future__ import annotations

from datetime import time, timedelta

import pytest
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_fire_time_changed,
    async_mock_service,
)

from homeassistant.core import Context, HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.util import dt as dt_util

from custom_components.sternchenplan.const import DOMAIN
from custom_components.sternchenplan.core import SYSTEM, Recurrence, Role
from custom_components.sternchenplan.reminders import parse_times


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    yield


def test_uhrzeiten_lesen() -> None:
    assert parse_times("17:00, 15:00;18:30, 15:00") == [time(15), time(17), time(18, 30)]
    with pytest.raises(ValueError):
        parse_times("abends")


@pytest.fixture
async def entry(hass: HomeAssistant, hass_admin_user, hass_read_only_user, freezer):
    freezer.move_to("2026-11-02 08:00:00+00:00")
    await hass.config.async_set_time_zone("UTC")
    hass.config.language = "de"
    entry = MockConfigEntry(
        domain=DOMAIN,
        options={"reminder_times": "17:00", "parent_summary_time": "19:00"},
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    family = entry.runtime_data.family
    family.add_member(SYSTEM, "Papa", Role.PARENT, user_id=hass_admin_user.id, notify_service="papa_handy")
    finn = family.add_member(SYSTEM, "Finn", Role.CHILD, user_id=hass_read_only_user.id, notify_service="notify.lucas_handy")
    family.add_member(SYSTEM, "Paul", Role.CHILD, notify_service="osmo_handy")
    now = dt_util.utcnow()
    family.create_chore(SYSTEM, "Müll", [finn.id], recurrence=Recurrence.DAILY, due=now.replace(hour=19))
    family.create_chore(SYSTEM, "Morgen", [finn.id], recurrence=Recurrence.DAILY, due=now + timedelta(days=1))
    await entry.runtime_data.async_save()
    return entry


async def test_erinnerung_nur_bei_offenen_aufgaben(hass: HomeAssistant, entry, freezer) -> None:
    lucas_calls = async_mock_service(hass, "notify", "lucas_handy")
    osmo_calls = async_mock_service(hass, "notify", "osmo_handy")
    papa_calls = async_mock_service(hass, "notify", "papa_handy")

    freezer.move_to("2026-11-02 17:00:00+00:00")
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert len(lucas_calls) == 1
    assert "Müll" in lucas_calls[0].data["message"]
    assert "Morgen" not in lucas_calls[0].data["message"]
    assert osmo_calls == []  # Paul hat nichts offen
    assert papa_calls == []

    freezer.move_to("2026-11-02 19:00:00+00:00")
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert len(papa_calls) == 1
    assert "Finn: 1 offen" in papa_calls[0].data["message"]


async def test_keine_erinnerung_bei_abwesenheit(
    hass: HomeAssistant, entry, freezer, hass_admin_user, hass_read_only_user
) -> None:
    lucas_calls = async_mock_service(hass, "notify", "lucas_handy")

    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            DOMAIN, "set_absence", {"member": "Finn", "until": "2026-11-03 12:00:00"},
            blocking=True, context=Context(user_id=hass_read_only_user.id),
        )
    await hass.services.async_call(
        DOMAIN, "set_absence",
        {"member": "Finn", "until": "2026-11-03 12:00:00", "substitute": "Paul"},
        blocking=True, context=Context(user_id=hass_admin_user.id),
    )
    osmo_calls = async_mock_service(hass, "notify", "osmo_handy")

    freezer.move_to("2026-11-02 17:00:00+00:00")
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert lucas_calls == []
    assert len(osmo_calls) == 1  # Paul vertritt beim Müll

    await hass.services.async_call(
        DOMAIN, "end_absence", {"member": "finn"},
        blocking=True, context=Context(user_id=hass_admin_user.id),
    )
    assert not entry.runtime_data.family.members[
        next(m.id for m in entry.runtime_data.family.members.values() if m.name == "Finn")
    ].is_away(dt_util.utcnow())


async def test_optionen_erinnerungen(hass: HomeAssistant, entry) -> None:
    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] == "menu"
    assert "reminders" in result["menu_options"]
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "reminders"}
    )
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"reminder_times": "abends", "parent_summary_time": ""}
    )
    assert result["errors"] == {"base": "invalid_time"}
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"reminder_times": "16:00, 18:00", "parent_summary_time": ""}
    )
    assert result["type"] == "create_entry"
    await hass.async_block_till_done()
    assert entry.options["reminder_times"] == "16:00, 18:00"
    assert entry.options["parent_summary_time"] == ""


async def test_level_und_abzeichen_feiern(hass: HomeAssistant, entry) -> None:
    lucas_calls = async_mock_service(hass, "notify", "lucas_handy")
    badges = []
    levels = []
    hass.bus.async_listen("sternchenplan_badge", badges.append)
    hass.bus.async_listen("sternchenplan_level_up", levels.append)
    family = entry.runtime_data.family
    chore = next(c for c in family.chores.values() if c.name == "Müll")
    chore.points = 5
    await hass.services.async_call(
        DOMAIN, "claim_chore", {"chore_id": chore.id, "member": "Finn"}, blocking=True
    )
    await hass.async_block_till_done()
    assert levels[0].data["level"] == 2
    assert levels[0].data["title"] == "Helfer"
    assert badges[0].data["name"] == "Erster Stern"
    messages = [c.data["message"] for c in lucas_calls]
    assert "🎉 Level 2 geschafft! Du bist jetzt Helfer." in messages
    assert "🌟 Neues Abzeichen: Erster Stern" in messages


async def test_familienziel_per_dienst(hass: HomeAssistant, entry) -> None:
    papa_calls = async_mock_service(hass, "notify", "papa_handy")
    reached = []
    hass.bus.async_listen("sternchenplan_family_goal", reached.append)
    await hass.services.async_call(
        DOMAIN, "set_family_goal", {"name": "Zoo", "target": 1}, blocking=True
    )
    family = entry.runtime_data.family
    chore = next(c for c in family.chores.values() if c.name == "Müll")
    await hass.services.async_call(
        DOMAIN, "claim_chore", {"chore_id": chore.id, "member": "Finn"}, blocking=True
    )
    await hass.async_block_till_done()
    assert reached[0].data["name"] == "Zoo"
    assert any("Familienziel geschafft: Zoo" in c.data["message"] for c in papa_calls)
    await hass.services.async_call(DOMAIN, "clear_family_goal", {}, blocking=True)
    assert family.goal is None


async def test_taschengeld_per_dienst(hass: HomeAssistant, entry, freezer) -> None:
    lucas_calls = async_mock_service(hass, "notify", "lucas_handy")
    await hass.services.async_call(DOMAIN, "set_money", {"rate": 10, "payday": 0}, blocking=True)
    await hass.services.async_call(
        DOMAIN, "set_allowance", {"member": "Finn", "amount": 2.5}, blocking=True
    )
    family = entry.runtime_data.family
    finn = next(m for m in family.members.values() if m.name == "Finn")
    finn.points = 30
    await hass.services.async_call(
        DOMAIN, "exchange_stars", {"member": "Finn", "euros": 3}, blocking=True
    )
    assert finn.money == 300 and finn.points == 0
    # nächster Montag: Wochengeld per Takt
    freezer.move_to("2026-11-09 00:01:00+00:00")
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert finn.money == 550
    assert any("2,50 € Taschengeld" in c.data["message"] for c in lucas_calls)
    await hass.services.async_call(DOMAIN, "payout", {"member": "Finn"}, blocking=True)
    assert finn.money == 0
