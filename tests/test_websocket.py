"""Websocket für die Dashboard-Karte."""

from __future__ import annotations

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.core import HomeAssistant

from custom_components.sternchenplan.const import DOMAIN
from custom_components.sternchenplan.core import SYSTEM, Role


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    yield


async def test_karte_bekommt_stand_und_updates(
    hass: HomeAssistant, hass_ws_client, hass_admin_user
) -> None:
    entry = MockConfigEntry(domain=DOMAIN)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    family = entry.runtime_data.family
    family.add_member(SYSTEM, "Papa", Role.PARENT, user_id=hass_admin_user.id)
    lucas = family.add_member(SYSTEM, "Lucas", Role.CHILD)
    await entry.runtime_data.async_save()

    client = await hass_ws_client(hass)  # angemeldet als hass_admin_user
    await client.send_json_auto_id({"type": f"{DOMAIN}/subscribe"})
    assert (await client.receive_json())["success"]
    first = (await client.receive_json())["event"]
    assert first["is_manager"] is True
    assert first["me"] is not None
    assert {m["name"] for m in first["members"]} == {"Papa", "Lucas"}
    assert first["chores"] == []

    await hass.services.async_call(
        DOMAIN, "create_chore", {"name": "Müll", "assignees": ["Lucas"]}, blocking=True
    )
    update = (await client.receive_json())["event"]
    assert update["chores"][0]["name"] == "Müll"
    assert update["chores"][0]["responsible"] == [lucas.id]


async def test_ohne_einrichtung_fehler(hass: HomeAssistant, hass_ws_client) -> None:
    from homeassistant.setup import async_setup_component

    assert await async_setup_component(hass, DOMAIN, {})
    client = await hass_ws_client(hass)
    await client.send_json_auto_id({"type": f"{DOMAIN}/subscribe"})
    msg = await client.receive_json()
    assert not msg["success"]
    assert msg["error"]["code"] == "not_loaded"
