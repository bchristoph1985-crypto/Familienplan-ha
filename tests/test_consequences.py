"""Internetsperre in Home Assistant, mit Test-Schaltern statt FRITZ!Box."""

from __future__ import annotations

from datetime import time, timedelta

import pytest
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_fire_time_changed,
)

from homeassistant.core import Context, HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.setup import async_setup_component
from homeassistant.util import dt as dt_util

from custom_components.sternchenplan.consequences import in_window
from custom_components.sternchenplan.const import DOMAIN
from custom_components.sternchenplan.core import SYSTEM, Recurrence, Role


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    yield


def test_zeitfenster() -> None:
    start, end = time(20), time(5)
    assert in_window(time(21), start, end)
    assert in_window(time(4, 59), start, end)
    assert not in_window(time(5), start, end)
    assert not in_window(time(19, 59), start, end)
    assert in_window(time(13), time(12), time(14))


@pytest.fixture
async def setup(hass: HomeAssistant, freezer, hass_admin_user, hass_read_only_user):
    freezer.move_to("2026-11-02 18:00:00+00:00")
    await hass.config.async_set_time_zone("UTC")
    # Zwei Test-Schalter als Ersatz für die FRITZ!Box-Internetschalter
    assert await async_setup_component(
        hass, "input_boolean", {"input_boolean": {"ps5": {"initial": True}, "handy": {"initial": True}}}
    )
    assert await async_setup_component(
        hass,
        "switch",
        {
            "switch": {
                "platform": "template",
                "switches": {
                    name: {
                        "value_template": f"{{{{ is_state('input_boolean.{name}', 'on') }}}}",
                        "turn_on": {"action": "input_boolean.turn_on", "target": {"entity_id": f"input_boolean.{name}"}},
                        "turn_off": {"action": "input_boolean.turn_off", "target": {"entity_id": f"input_boolean.{name}"}},
                    }
                    for name in ("ps5", "handy")
                },
            }
        },
    )
    await hass.async_block_till_done()
    entry = MockConfigEntry(domain=DOMAIN, options={"consequences": True})
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    family = entry.runtime_data.family
    family.add_member(SYSTEM, "Papa", Role.PARENT, user_id=hass_admin_user.id)
    finn = family.add_member(SYSTEM, "Finn", Role.CHILD, user_id=hass_read_only_user.id)
    family.set_devices(SYSTEM, finn.id, ["switch.ps5"])
    family.create_chore(
        SYSTEM, "Müll", [finn.id], recurrence=Recurrence.DAILY,
        due=dt_util.utcnow() + timedelta(hours=1),  # 19:00
    )
    await entry.runtime_data.async_save()
    return entry


def _state(hass, entity_id):
    return hass.states.get(entity_id).state


async def _tick(hass, freezer, when):
    freezer.move_to(when)
    async_fire_time_changed(hass)
    await hass.async_block_till_done()


async def test_sperre_ab_20_uhr_und_freigabe_nach_erledigung(
    hass: HomeAssistant, setup, freezer, hass_read_only_user
) -> None:
    await _tick(hass, freezer, "2026-11-02 19:30:00+00:00")
    assert _state(hass, "switch.ps5") == "on"  # überfällig, aber vor 20 Uhr

    await _tick(hass, freezer, "2026-11-02 20:01:00+00:00")
    assert _state(hass, "switch.ps5") == "off"
    assert _state(hass, "switch.handy") == "on"  # nicht eingetragen, bleibt an

    # Kind schaltet die PS5 selbst wieder an: nächste Minute wieder aus
    await hass.services.async_call("switch", "turn_on", {"entity_id": "switch.ps5"}, blocking=True)
    await hass.async_block_till_done()
    assert _state(hass, "switch.ps5") == "on"
    await _tick(hass, freezer, "2026-11-02 20:02:30+00:00")
    assert _state(hass, "switch.ps5") == "off"

    chore_id = next(iter(setup.runtime_data.family.chores))
    await hass.services.async_call(
        DOMAIN, "claim_chore", {"chore_id": chore_id},
        blocking=True, context=Context(user_id=hass_read_only_user.id),
    )
    await hass.async_block_till_done()
    assert _state(hass, "switch.ps5") == "on"
    assert setup.runtime_data.family.locked == {}


async def test_freikarte_und_ende_des_zeitfensters(
    hass: HomeAssistant, setup, freezer, hass_admin_user, hass_read_only_user
) -> None:
    await _tick(hass, freezer, "2026-11-02 20:01:00+00:00")
    assert _state(hass, "switch.ps5") == "off"

    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            DOMAIN, "grant_pass", {"member": "Finn"},
            blocking=True, context=Context(user_id=hass_read_only_user.id),
        )
    assert _state(hass, "switch.ps5") == "off"

    await hass.services.async_call(
        DOMAIN, "grant_pass", {"member": "Finn"},
        blocking=True, context=Context(user_id=hass_admin_user.id),
    )
    await hass.async_block_till_done()
    assert _state(hass, "switch.ps5") == "on"
    finn = next(m for m in setup.runtime_data.family.members.values() if m.name == "Finn")
    assert finn.pass_until.hour == 5  # bis morgen 05:00

    await hass.services.async_call(
        DOMAIN, "revoke_pass", {"member": "Finn"},
        blocking=True, context=Context(user_id=hass_admin_user.id),
    )
    await hass.async_block_till_done()
    assert _state(hass, "switch.ps5") == "off"

    # Ende des Sperrfensters: freigeben, obwohl noch offen
    await _tick(hass, freezer, "2026-11-03 05:01:00+00:00")
    assert _state(hass, "switch.ps5") == "on"


async def test_ausgeschaltet_sperrt_nie(hass: HomeAssistant, setup, freezer) -> None:
    hass.config_entries.async_update_entry(setup, options={"consequences": False})
    await _tick(hass, freezer, "2026-11-02 20:30:00+00:00")
    assert _state(hass, "switch.ps5") == "on"


async def test_nur_eigene_sperren_werden_freigegeben(hass: HomeAssistant, setup, freezer) -> None:
    # Papa schaltet die PS5 selbst aus, ohne dass etwas offen ist
    family = setup.runtime_data.family
    chore = next(iter(family.chores.values()))
    family.claim(SYSTEM, chore.id, chore.assignees[0], dt_util.utcnow())
    await setup.runtime_data.async_save()
    await hass.services.async_call("switch", "turn_off", {"entity_id": "switch.ps5"}, blocking=True)
    await _tick(hass, freezer, "2026-11-02 20:30:00+00:00")
    assert _state(hass, "switch.ps5") == "off"  # Sternchenplan schaltet es nicht ein
