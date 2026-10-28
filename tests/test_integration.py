"""Tests in einem echten (Test-)Home-Assistant."""

from __future__ import annotations

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.core import Context, HomeAssistant
from homeassistant.exceptions import ServiceValidationError

from custom_components.familienplan.const import DOMAIN
from custom_components.familienplan.core import SYSTEM, Role


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    yield


@pytest.fixture
async def setup(hass: HomeAssistant, hass_admin_user, hass_read_only_user):
    entry = MockConfigEntry(domain=DOMAIN, title="Familie Test")
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    family = entry.runtime_data.family
    family.add_member(SYSTEM, "Papa", Role.PARENT, user_id=hass_admin_user.id)
    family.add_member(SYSTEM, "Lucas", Role.CHILD, user_id=hass_read_only_user.id)
    await entry.runtime_data.async_save()
    await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()
    return entry


def _ctx(user) -> Context:
    return Context(user_id=user.id)


def _chore_state(hass: HomeAssistant, name: str):
    for state in hass.states.async_all("sensor"):
        if state.attributes.get("friendly_name", "").endswith(name):
            return state
    return None


async def test_ablauf_mit_rechten(
    hass: HomeAssistant, setup, hass_admin_user, hass_read_only_user
) -> None:
    # Kind darf keine Aufgabe anlegen
    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            DOMAIN, "create_chore",
            {"name": "Müll", "assignees": ["Lucas"]},
            blocking=True, context=_ctx(hass_read_only_user),
        )

    # Eltern legen an, mit Freigabe
    await hass.services.async_call(
        DOMAIN, "create_chore",
        {"name": "Müll", "assignees": ["lucas"], "points": 2, "requires_approval": True},
        blocking=True, context=_ctx(hass_admin_user),
    )
    await hass.async_block_till_done()
    state = _chore_state(hass, "Müll")
    assert state is not None
    assert state.state == "open"
    chore_id = state.attributes["chore_id"]

    # Kind meldet, ohne sich selbst anzugeben
    await hass.services.async_call(
        DOMAIN, "claim_chore", {"chore_id": chore_id},
        blocking=True, context=_ctx(hass_read_only_user),
    )
    await hass.async_block_till_done()
    assert _chore_state(hass, "Müll").state == "claimed"

    # Kind kann sich nicht selbst freigeben
    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            DOMAIN, "approve_chore", {"chore_id": chore_id},
            blocking=True, context=_ctx(hass_read_only_user),
        )

    await hass.services.async_call(
        DOMAIN, "approve_chore", {"chore_id": chore_id},
        blocking=True, context=_ctx(hass_admin_user),
    )
    await hass.async_block_till_done()
    assert _chore_state(hass, "Müll").state == "done"
    points = _chore_state(hass, "Lucas Punkte") or _chore_state(hass, "Lucas points")
    assert points is not None and points.state == "2"


async def test_daten_ueberleben_neustart(hass: HomeAssistant, setup, hass_admin_user) -> None:
    await hass.services.async_call(
        DOMAIN, "create_chore", {"name": "Tisch", "assignees": ["Lucas"]},
        blocking=True, context=_ctx(hass_admin_user),
    )
    await hass.config_entries.async_reload(setup.entry_id)
    await hass.async_block_till_done()
    names = [c.name for c in setup.runtime_data.family.chores.values()]
    assert names == ["Tisch"]


async def test_loeschen_entfernt_sensor(hass: HomeAssistant, setup, hass_admin_user) -> None:
    await hass.services.async_call(
        DOMAIN, "create_chore", {"name": "Fenster", "assignees": ["Lucas"]},
        blocking=True, context=_ctx(hass_admin_user),
    )
    await hass.async_block_till_done()
    chore_id = _chore_state(hass, "Fenster").attributes["chore_id"]
    await hass.services.async_call(
        DOMAIN, "delete_chore", {"chore_id": chore_id},
        blocking=True, context=_ctx(hass_admin_user),
    )
    await hass.async_block_till_done()
    assert _chore_state(hass, "Fenster") is None


async def test_config_flow(hass: HomeAssistant) -> None:
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})
    assert result["type"] == "form"
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"family_name": "Familie B"}
    )
    assert result["type"] == "create_entry"
    assert result["title"] == "Familie B"
