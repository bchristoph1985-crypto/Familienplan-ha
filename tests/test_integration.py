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


async def test_einrichtungsassistent(
    hass: HomeAssistant, hass_admin_user, hass_read_only_user
) -> None:
    from homeassistant.helpers import device_registry as dr, entity_registry as er
    from pytest_homeassistant_custom_component.common import async_mock_service

    hass.config.language = "de"
    # Bennis Handy aus der Companion-App
    app_entry = MockConfigEntry(domain="mobile_app")
    app_entry.add_to_hass(hass)
    device = dr.async_get(hass).async_get_or_create(
        config_entry_id=app_entry.entry_id, identifiers={("mobile_app", "fold")}, name="Fold 7 Benni"
    )
    er.async_get(hass).async_get_or_create(
        "device_tracker", "mobile_app", "fold", device_id=device.id,
        config_entry=app_entry, suggested_object_id="fold_7_benni",
    )
    async_mock_service(hass, "notify", "mobile_app_fold_7_benni")
    hass.states.async_set(
        "person.benni", "home",
        {"friendly_name": "Benni", "user_id": hass_admin_user.id, "device_trackers": ["device_tracker.fold_7_benni"]},
    )
    hass.states.async_set(
        "person.jan", "home", {"friendly_name": "Jan", "user_id": hass_read_only_user.id}
    )
    hass.states.async_set("person.oma", "not_home", {"friendly_name": "Oma"})

    flow = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})
    flow = await hass.config_entries.flow.async_configure(flow["flow_id"], {"family_name": "Familie B"})
    assert flow["step_id"] == "members"

    # Niemand ausgewählt -> Hinweis
    bad = await hass.config_entries.flow.async_configure(flow["flow_id"], {"people": [], "extra_children": ""})
    assert bad["errors"] == {"base": "no_members"}

    flow = await hass.config_entries.flow.async_configure(
        flow["flow_id"],
        {"people": ["person.benni", "person.jan"], "extra_children": "Lucas, Osmo"},
    )
    assert flow["step_id"] == "parents"
    # Vorschlag: Admin ist Elternteil
    default = next(k for k in flow["data_schema"].schema if str(k) == "parents").default()
    assert default == ["person.benni"]

    flow = await hass.config_entries.flow.async_configure(flow["flow_id"], {"parents": ["person.benni"]})
    assert flow["step_id"] == "chores"
    result = await hass.config_entries.flow.async_configure(
        flow["flow_id"], {"starters": ["dishwasher", "room"]}
    )
    assert result["type"] == "create_entry"
    assert result["title"] == "Familie B"
    await hass.async_block_till_done()

    entry = hass.config_entries.async_entries(DOMAIN)[0]
    family = entry.runtime_data.family
    members = {m.name: m for m in family.members.values()}
    assert set(members) == {"Benni", "Jan", "Lucas", "Osmo"}
    assert members["Benni"].role is Role.PARENT
    assert members["Benni"].notify_service == "mobile_app_fold_7_benni"
    assert members["Jan"].role is Role.CHILD and members["Jan"].user_id == hass_read_only_user.id
    chores = sorted(c.name for c in family.chores.values())
    assert chores == [
        "Spülmaschine ausräumen",
        "Zimmer aufräumen (Jan)",
        "Zimmer aufräumen (Lucas)",
        "Zimmer aufräumen (Osmo)",
    ]
    dish = next(c for c in family.chores.values() if c.name == "Spülmaschine ausräumen")
    assert dish.rotation and len(dish.assignees) == 3
    # Startdaten wurden übernommen und aus dem Eintrag entfernt
    assert entry.data == {}
    await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()
    assert len(entry.runtime_data.family.members) == 4


async def test_einrichtung_ohne_personen(hass: HomeAssistant) -> None:
    flow = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})
    flow = await hass.config_entries.flow.async_configure(flow["flow_id"], {"family_name": ""})
    flow = await hass.config_entries.flow.async_configure(flow["flow_id"], {"extra_children": "Mia"})
    assert flow["step_id"] == "chores"
    result = await hass.config_entries.flow.async_configure(flow["flow_id"], {"starters": []})
    assert result["title"] == "Familie"
    await hass.async_block_till_done()
    entry = hass.config_entries.async_entries(DOMAIN)[0]
    assert [m.name for m in entry.runtime_data.family.members.values()] == ["Mia"]
