"""Fotogalerie: Fotos sammeln, ansehen (nur Eltern), löschen."""

from __future__ import annotations

from datetime import timedelta

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.core import Context, HomeAssistant
from homeassistant.exceptions import ServiceValidationError

from custom_components.sternchenplan.const import DOMAIN
from custom_components.sternchenplan.core import SYSTEM, Family, PermissionDenied, Recurrence, Role
from custom_components.sternchenplan.photos import forget_missing, photo_dir

from .test_core import NOW, actor, by_name, family  # noqa: F401


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    yield


def test_galerie_sammelt_jede_runde(family: Family) -> None:  # noqa: F811
    finn, paul = by_name(family, "Finn"), by_name(family, "Paul")
    chore = family.create_chore(SYSTEM, "Zimmer", [finn.id], recurrence=Recurrence.DAILY, due=NOW, requires_photo=True)
    family.claim(actor(family, "Finn"), chore.id, finn.id, NOW, photo="a.jpg")
    family.reject(SYSTEM, chore.id, NOW)
    family.claim(actor(family, "Finn"), chore.id, finn.id, NOW + timedelta(minutes=5), photo="b.jpg")
    assert [e["file"] for e in family.gallery()] == ["b.jpg", "a.jpg"]
    assert family.gallery()[0]["name"] == "Zimmer" and family.gallery()[0]["member"] == finn.id
    assert Family.from_dict(family.to_dict()).photo_log == family.photo_log

    with pytest.raises(PermissionDenied):
        family.delete_photo(actor(family, "Paul"), "a.jpg")
    family.delete_photo(SYSTEM, "b.jpg")
    assert [e["file"] for e in family.gallery()] == ["a.jpg"] and chore.photo is None

    # Person löschen: alle ihre Fotos gehen mit, nicht nur das letzte
    assert family.remove_member(SYSTEM, finn.id) == ["a.jpg"]
    assert family.gallery() == [] and paul.id in family.members


async def test_galerie_nur_fuer_eltern_und_loeschen(
    hass: HomeAssistant, hass_admin_user, hass_read_only_user, hass_ws_client, hass_read_only_access_token
) -> None:
    entry = MockConfigEntry(domain=DOMAIN)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    fam = entry.runtime_data.family
    fam.add_member(SYSTEM, "Papa", Role.PARENT, user_id=hass_admin_user.id)
    lena = fam.add_member(SYSTEM, "Lena", Role.CHILD, user_id=hass_read_only_user.id)
    chore = fam.create_chore(SYSTEM, "Bad", [lena.id], requires_photo=True)
    folder = photo_dir(hass)
    await hass.async_add_executor_job(lambda: folder.mkdir(parents=True, exist_ok=True))
    for name in ("x.jpg", "y.jpg"):
        await hass.async_add_executor_job((folder / name).write_bytes, b"x")
    fam.claim(SYSTEM, chore.id, lena.id, NOW, photo="x.jpg")
    fam._keep_photo(chore, lena.id, NOW + timedelta(hours=1), "y.jpg")

    async def gallery(client):
        await client.send_json_auto_id({"type": f"{DOMAIN}/subscribe"})
        await client.receive_json()
        return (await client.receive_json())["event"]["gallery"]

    parent = await gallery(await hass_ws_client(hass))
    assert [e["file"] for e in parent] == ["y.jpg", "x.jpg"] and "authSig=" in parent[0]["url"]
    assert await gallery(await hass_ws_client(hass, hass_read_only_access_token)) == []

    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            DOMAIN, "delete_photo", {"file": "y.jpg"}, blocking=True,
            context=Context(user_id=hass_read_only_user.id),
        )
    await hass.services.async_call(
        DOMAIN, "delete_photo", {"file": "y.jpg"}, blocking=True,
        context=Context(user_id=hass_admin_user.id),
    )
    assert not await hass.async_add_executor_job((folder / "y.jpg").exists)
    assert [e["file"] for e in fam.gallery()] == ["x.jpg"]

    # Löschfrist hat das Foto entfernt: es verschwindet auch aus der Galerie
    await hass.async_add_executor_job((folder / "x.jpg").unlink)
    assert await hass.async_add_executor_job(forget_missing, hass, entry)
    assert fam.gallery() == []
