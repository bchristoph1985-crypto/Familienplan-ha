"""Update von älteren Versionen: gespeicherte Daten laden und eine Woche damit leben."""

from __future__ import annotations

import json
import logging
from datetime import timedelta
from pathlib import Path

import pytest
from freezegun.api import FrozenDateTimeFactory
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_fire_time_changed,
    async_mock_service,
)

from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from custom_components.sternchenplan.const import DOMAIN
from custom_components.sternchenplan.core import DEFAULT_FEATURES, Family

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    yield


@pytest.mark.parametrize("version", ["0_14", "0_26"])
async def test_update_und_eine_woche(
    hass: HomeAssistant, hass_storage, hass_ws_client, freezer: FrozenDateTimeFactory, caplog, version: str
) -> None:
    caplog.set_level(logging.WARNING)
    old = json.loads((FIXTURES / f"state_{version}.json").read_text())
    entry = MockConfigEntry(domain=DOMAIN, entry_id="alt")
    entry.add_to_hass(hass)
    hass_storage[f"{DOMAIN}.alt"] = {"version": 1, "minor_version": 1, "key": f"{DOMAIN}.alt", "data": old}
    for svc in ("notify", "light", "switch"):
        async_mock_service(hass, svc, "noop")
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    fam: Family = entry.runtime_data.family

    # Nichts geht verloren, neue Funktionen sind an
    members = old["members"].values() if isinstance(old["members"], dict) else old["members"]
    assert {m.name for m in fam.members.values()} == {m["name"] for m in members}
    assert len(fam.chores) == len(old["chores"])
    assert fam.features == set(DEFAULT_FEATURES)

    client = await hass_ws_client(hass)
    await client.send_json_auto_id({"type": f"{DOMAIN}/subscribe"})
    assert (await client.receive_json())["success"]
    snap = (await client.receive_json())["event"]
    assert len(snap["chores"]) == len(old["chores"])

    # Eine Woche: jede Stunde ein Takt, abends melden die Kinder, Eltern geben frei
    kids = [m for m in fam.members.values() if m.role.value == "child"]
    for hour in range(24 * 7):
        freezer.tick(timedelta(hours=1))
        async_fire_time_changed(hass, dt_util.utcnow())
        await hass.async_block_till_done()
        if dt_util.now().hour == 18:
            for kid in kids:
                for chore in list(fam.open_for(kid.id, dt_util.utcnow())):
                    data = {"chore_id": chore.id, "member": kid.id}
                    try:
                        await hass.services.async_call(DOMAIN, "claim_chore", data, blocking=True)
                    except Exception:  # noqa: BLE001 – Fotopflicht o. Ä. ist erlaubt
                        pass
            for chore in [c for c in fam.chores.values() if c.state.value == "claimed"]:
                await hass.services.async_call(DOMAIN, "approve_chore", {"chore_id": chore.id}, blocking=True)

    assert sum(m.progress.done for m in kids) > 0
    again = Family.from_dict(json.loads(json.dumps(fam.to_dict())))
    assert again.to_dict() == fam.to_dict()
    errors = [r for r in caplog.records if r.levelno >= logging.ERROR]
    assert not errors, [r.getMessage() for r in errors]
