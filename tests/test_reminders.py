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
    lucas = family.add_member(SYSTEM, "Lucas", Role.CHILD, user_id=hass_read_only_user.id, notify_service="notify.lucas_handy")
    family.add_member(SYSTEM, "Osmo", Role.CHILD, notify_service="osmo_handy")
    now = dt_util.utcnow()
    family.create_chore(SYSTEM, "Müll", [lucas.id], recurrence=Recurrence.DAILY, due=now.replace(hour=19))
    family.create_chore(SYSTEM, "Morgen", [lucas.id], recurrence=Recurrence.DAILY, due=now + timedelta(days=1))
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
    assert osmo_calls == []  # Osmo hat nichts offen
    assert papa_calls == []

    freezer.move_to("2026-11-02 19:00:00+00:00")
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert len(papa_calls) == 1
    assert "Lucas: 1 offen" in papa_calls[0].data["message"]


async def test_keine_erinnerung_bei_abwesenheit(
    hass: HomeAssistant, entry, freezer, hass_admin_user, hass_read_only_user
) -> None:
    lucas_calls = async_mock_service(hass, "notify", "lucas_handy")

    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            DOMAIN, "set_absence", {"member": "Lucas", "until": "2026-11-03 12:00:00"},
            blocking=True, context=Context(user_id=hass_read_only_user.id),
        )
    await hass.services.async_call(
        DOMAIN, "set_absence",
        {"member": "Lucas", "until": "2026-11-03 12:00:00", "substitute": "Osmo"},
        blocking=True, context=Context(user_id=hass_admin_user.id),
    )
    osmo_calls = async_mock_service(hass, "notify", "osmo_handy")

    freezer.move_to("2026-11-02 17:00:00+00:00")
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert lucas_calls == []
    assert len(osmo_calls) == 1  # Osmo vertritt beim Müll

    await hass.services.async_call(
        DOMAIN, "end_absence", {"member": "lucas"},
        blocking=True, context=Context(user_id=hass_admin_user.id),
    )
    assert not entry.runtime_data.family.members[
        next(m.id for m in entry.runtime_data.family.members.values() if m.name == "Lucas")
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
