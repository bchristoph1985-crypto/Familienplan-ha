"""Familientablet: Kinder ohne eigenes Handy haken an einem gemeinsamen Gerät ab."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.core import Context, HomeAssistant
from homeassistant.exceptions import ServiceValidationError

from custom_components.sternchenplan.const import DOMAIN
from custom_components.sternchenplan.core import (
    SYSTEM,
    ChoreState,
    Family,
    FamilyError,
    PermissionDenied,
    Recurrence,
    Role,
)
from custom_components.sternchenplan.websocket_api import snapshot

NOW = datetime(2026, 11, 2, 15, tzinfo=timezone.utc)


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    yield


def _family() -> tuple[Family, str, str, str]:
    family = Family()
    papa = family.add_member(SYSTEM, "Papa", Role.PARENT, user_id="u-papa")
    lucas = family.add_member(SYSTEM, "Lucas", Role.CHILD)
    osmo = family.add_member(SYSTEM, "Osmo", Role.CHILD)
    family.set_tablet(SYSTEM, ["u-tablet"], approval=False)
    return family, papa.id, lucas.id, osmo.id


def test_tablet_hakt_fuer_kind_ab_aber_nicht_fuer_eltern() -> None:
    family, papa, lucas, osmo = _family()
    chore = family.create_chore(SYSTEM, "Müll", [lucas], recurrence=Recurrence.NONE)
    tablet = family.actor_for_user("u-tablet", is_admin=False)
    assert tablet.tablet and not tablet.is_manager

    # Nur wer dran ist, nicht ein anderes Kind und nicht die Eltern
    with pytest.raises(PermissionDenied):
        family.claim(tablet, chore.id, osmo, NOW)
    with pytest.raises(PermissionDenied):
        family.claim(tablet, chore.id, papa, NOW)
    family.claim(tablet, chore.id, lucas, NOW)
    assert chore.state is ChoreState.DONE


def test_tablet_mit_elternbestaetigung() -> None:
    family, _, lucas, _ = _family()
    family.tablet_approval = True
    chore = family.create_chore(SYSTEM, "Müll", [lucas], recurrence=Recurrence.NONE)
    tablet = family.actor_for_user("u-tablet", is_admin=False)
    family.claim(tablet, chore.id, lucas, NOW)
    assert chore.state is ChoreState.CLAIMED
    family.undo_claim(tablet, chore.id)
    assert chore.state is ChoreState.OPEN


def test_tablet_belohnung_einloesen_und_zuruecknehmen() -> None:
    family, _, lucas, _ = _family()
    family.members[lucas].points = 20
    reward = family.create_reward(SYSTEM, "Filmabend", 15)
    tablet = family.actor_for_user("u-tablet", is_admin=False)
    redemption = family.redeem(tablet, reward.id, lucas, NOW)
    assert family.members[lucas].points == 5
    family.reject_redemption(tablet, redemption.id, NOW)
    assert family.members[lucas].points == 20
    # Bestätigen bleibt Elternsache
    redemption = family.redeem(tablet, reward.id, lucas, NOW)
    with pytest.raises(PermissionDenied):
        family.approve_redemption(tablet, redemption.id, NOW)


def test_tablet_konto_und_mitglieder() -> None:
    family, *_ = _family()
    with pytest.raises(FamilyError):
        family.set_tablet(SYSTEM, ["u-papa"], approval=False)
    # Wird das Tablet-Konto doch Mitglied, ist es kein Tablet mehr
    family.add_member(SYSTEM, "Jan", Role.CHILD, user_id="u-tablet")
    assert family.tablet_users == []
    restored = Family.from_dict(family.to_dict())
    assert restored.tablet_users == [] and not restored.tablet_approval


async def test_tablet_ueber_dienst_und_karte(
    hass: HomeAssistant, hass_admin_user, hass_read_only_user
) -> None:
    entry = MockConfigEntry(domain=DOMAIN)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    family = entry.runtime_data.family
    family.add_member(SYSTEM, "Papa", Role.PARENT, user_id=hass_admin_user.id)
    lucas = family.add_member(SYSTEM, "Lucas", Role.CHILD)
    family.set_tablet(SYSTEM, [hass_read_only_user.id], approval=False)
    chore = family.create_chore(SYSTEM, "Tisch", [lucas.id], recurrence=Recurrence.NONE)
    await entry.runtime_data.async_save()

    ctx = Context(user_id=hass_read_only_user.id)
    with pytest.raises(ServiceValidationError):
        # Ohne Namen weiß das Tablet nicht, wer es war
        await hass.services.async_call(
            DOMAIN, "claim_chore", {"chore_id": chore.id}, blocking=True, context=ctx
        )
    await hass.services.async_call(
        DOMAIN, "claim_chore", {"chore_id": chore.id, "member": "Lucas"}, blocking=True, context=ctx
    )
    assert chore.state is ChoreState.DONE

    data = snapshot(hass, entry, NOW + timedelta(hours=1), hass_read_only_user.id, False)
    assert data["tablet"] is True and data["me"] is None and not data["is_manager"]


async def test_tablet_im_assistenten(hass: HomeAssistant, hass_admin_user, hass_read_only_user) -> None:
    hass.config.language = "de"
    hass.states.async_set("person.benni", "home", {"friendly_name": "Benni", "user_id": hass_admin_user.id})
    hass.states.async_set("person.kueche", "home", {"friendly_name": "Küche", "user_id": hass_read_only_user.id})
    flow = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})
    flow = await hass.config_entries.flow.async_configure(flow["flow_id"], {"family_name": "B"})
    # Küchen-Tablet ist versehentlich als Mitglied angehakt
    flow = await hass.config_entries.flow.async_configure(
        flow["flow_id"], {"people": ["person.benni", "person.kueche"], "extra_children": "Lucas"}
    )
    flow = await hass.config_entries.flow.async_configure(flow["flow_id"], {"parents": ["person.benni"]})
    assert flow["step_id"] == "tablet"
    flow = await hass.config_entries.flow.async_configure(
        flow["flow_id"], {"tablet": ["person.kueche"], "tablet_approval": True}
    )
    assert flow["step_id"] == "ages"
    assert [str(k) for k in flow["data_schema"].schema] == ["Lucas"]
    flow = await hass.config_entries.flow.async_configure(flow["flow_id"], {"Lucas": 12})
    flow = await hass.config_entries.flow.async_configure(flow["flow_id"], {"starters": []})
    flow = await hass.config_entries.flow.async_configure(flow["flow_id"], {"rewards": []})
    result = await hass.config_entries.flow.async_configure(flow["flow_id"], {"photo_privacy": "delete"})
    assert result["type"] == "create_entry"
    await hass.async_block_till_done()
    family = hass.config_entries.async_entries(DOMAIN)[0].runtime_data.family
    assert {m.name for m in family.members.values()} == {"Benni", "Lucas"}
    assert family.tablet_users == [hass_read_only_user.id] and family.tablet_approval
