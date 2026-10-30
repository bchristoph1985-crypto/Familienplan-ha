"""Datenschutz: sparsame Pushes, Datenauskunft und Löschen einer Person."""

from __future__ import annotations

from datetime import timedelta

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_mock_service

from homeassistant.core import Context, HomeAssistant
from homeassistant.exceptions import ServiceValidationError

from custom_components.sternchenplan.const import DOMAIN
from custom_components.sternchenplan.core import SYSTEM, Family, PermissionDenied, Recurrence, Role
from custom_components.sternchenplan.photos import photo_dir
from custom_components.sternchenplan.privacy import scrub

from .test_core import NOW, actor, by_name, family  # noqa: F401


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    yield


def test_auskunft_und_spuren_loeschen(family: Family) -> None:  # noqa: F811
    finn, paul = by_name(family, "Finn"), by_name(family, "Paul")
    chore = family.create_chore(SYSTEM, "Tisch", [finn.id, paul.id], recurrence=Recurrence.DAILY, due=NOW, rotation=True)
    family.claim(actor(family, "Finn"), chore.id, finn.id, NOW, photo="abc.jpg")
    family.give_stars(SYSTEM, finn.id, 2, "lieb", NOW)
    family.give_stars(SYSTEM, paul.id, 1, "nett", NOW)
    with pytest.raises(PermissionDenied):
        family.export_member(actor(family, "Finn"), finn.id)
    data = family.export_member(SYSTEM, finn.id)
    assert data["member"]["name"] == "Finn"
    assert [h["event"] for h in data["chores"][0]["history"]] == ["completed"]
    assert [e["reason"] for e in data["star_log"]] == ["lieb"]

    photos = family.remove_member(SYSTEM, finn.id)
    assert photos == ["abc.jpg"] and chore.photo is None
    assert all(h.get("member") != finn.id for h in chore.history)
    assert chore.last_completed_by is None
    assert [e["member"] for e in family.star_log] == [paul.id]
    assert finn.id not in Family.from_dict(family.to_dict()).members


async def test_sparsame_pushes(hass: HomeAssistant) -> None:
    entry = MockConfigEntry(domain=DOMAIN)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    payload = {"title": "Sternchenplan", "message": "Finn hat „Bad“ erledigt.",
               "data": {"image": "/api/x.jpg", "actions": [{"action": "A"}], "tag": "t"}}
    assert scrub(hass, payload) == payload
    entry.runtime_data.family.set_private_push(SYSTEM, True)
    hidden = scrub(hass, payload)
    assert "Finn" not in hidden["message"] and "image" not in hidden["data"]
    assert hidden["data"]["actions"] == [{"action": "A"}]
    assert "Finn" not in scrub(hass, {"title": "x", "message": "Finn: 2 offen"})["message"]


async def test_loeschen_ueber_dienst_entfernt_foto(
    hass: HomeAssistant, hass_admin_user, hass_read_only_user, hass_ws_client
) -> None:
    entry = MockConfigEntry(domain=DOMAIN)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    fam = entry.runtime_data.family
    fam.add_member(SYSTEM, "Papa", Role.PARENT, user_id=hass_admin_user.id)
    finn = fam.add_member(SYSTEM, "Finn", Role.CHILD, user_id=hass_read_only_user.id)
    chore = fam.create_chore(SYSTEM, "Zimmer", [finn.id], requires_photo=True)
    folder = photo_dir(hass)
    await hass.async_add_executor_job(lambda: folder.mkdir(parents=True, exist_ok=True))
    file = folder / "zimmer.jpg"
    await hass.async_add_executor_job(file.write_bytes, b"x")
    fam.claim(SYSTEM, chore.id, finn.id, NOW - timedelta(hours=1), photo="zimmer.jpg")
    await entry.runtime_data.async_save()

    # Auskunft nur für Eltern
    client = await hass_ws_client(hass)
    await client.send_json_auto_id({"type": f"{DOMAIN}/export", "member": finn.id})
    result = await client.receive_json()
    assert result["success"] and result["result"]["member"]["name"] == "Finn"

    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            DOMAIN, "forget_member", {"member": "Finn"}, blocking=True,
            context=Context(user_id=hass_read_only_user.id),
        )
    async_mock_service(hass, "notify", "noop")
    await hass.services.async_call(
        DOMAIN, "forget_member", {"member": "Finn"}, blocking=True,
        context=Context(user_id=hass_admin_user.id),
    )
    assert finn.id not in fam.members
    assert not await hass.async_add_executor_job(file.exists)
