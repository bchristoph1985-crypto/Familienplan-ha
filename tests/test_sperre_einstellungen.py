"""Internetsperre aus der Karte: an/aus, Zeiten, Geräte – nur Eltern."""

from __future__ import annotations

import pytest
import voluptuous as vol
from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.core import Context, HomeAssistant
from homeassistant.exceptions import ServiceValidationError

from custom_components.sternchenplan.const import (
    CONF_CONSEQUENCES,
    CONF_LOCK_TIME,
    CONF_RELEASE_TIME,
    DOMAIN,
)
from custom_components.sternchenplan.core import SYSTEM, Role


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    yield


async def test_sperre_schalten_und_zeiten(
    hass: HomeAssistant, hass_admin_user, hass_read_only_user, hass_ws_client
) -> None:
    entry = MockConfigEntry(domain=DOMAIN)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    fam = entry.runtime_data.family
    fam.add_member(SYSTEM, "Papa", Role.PARENT, user_id=hass_admin_user.id)
    finn = fam.add_member(SYSTEM, "Finn", Role.CHILD, user_id=hass_read_only_user.id)
    fam.set_devices(SYSTEM, finn.id, ["switch.konsole"])
    await entry.runtime_data.async_save()

    # Kinder dürfen die Sperre nicht abschalten
    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            DOMAIN, "set_lock", {"enabled": False}, blocking=True,
            context=Context(user_id=hass_read_only_user.id),
        )
    with pytest.raises(vol.Invalid):
        await hass.services.async_call(DOMAIN, "set_lock", {"lock_time": "abends"}, blocking=True)

    await hass.services.async_call(
        DOMAIN, "set_lock", {"enabled": True, "lock_time": "19:30:00"}, blocking=True,
        context=Context(user_id=hass_admin_user.id),
    )
    await hass.async_block_till_done()
    assert entry.state.name == "LOADED"
    assert entry.options[CONF_CONSEQUENCES] is True
    assert entry.options[CONF_LOCK_TIME] == "19:30"
    assert CONF_RELEASE_TIME not in entry.options

    # Eltern sehen Schalter, Zeiten und Geräte in der Karte
    client = await hass_ws_client(hass)
    await client.send_json_auto_id({"type": f"{DOMAIN}/subscribe"})
    msg = await client.receive_json()
    assert msg["success"]
    snap = (await client.receive_json())["event"]
    assert snap["lock"] == {"enabled": True, "lock_time": "19:30", "release_time": "05:00"}
    member = next(m for m in snap["members"] if m["name"] == "Finn")
    assert member["devices"] == ["switch.konsole"]
