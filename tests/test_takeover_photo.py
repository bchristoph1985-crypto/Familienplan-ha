"""Wegmopsen-Zeitfenster und Fotonachweis in einem Test-Home-Assistant."""

from __future__ import annotations

import os
import time
from datetime import datetime

import aiohttp
import pytest
from freezegun.api import FrozenDateTimeFactory
from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.core import Context, HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.util import dt as dt_util

from custom_components.sternchenplan.const import DOMAIN
from custom_components.sternchenplan.core import SYSTEM, ChoreState, Role
from custom_components.sternchenplan.photos import cleanup, forget_missing, photo_dir
from custom_components.sternchenplan.websocket_api import snapshot


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    yield


@pytest.fixture
async def setup(hass: HomeAssistant, hass_admin_user, hass_read_only_user, tmp_path):
    hass.config.config_dir = str(tmp_path)
    entry = MockConfigEntry(domain=DOMAIN, title="Familie Test")
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    family = entry.runtime_data.family
    family.add_member(SYSTEM, "Papa", Role.PARENT, user_id=hass_admin_user.id)
    family.add_member(SYSTEM, "Finn", Role.CHILD)
    family.add_member(SYSTEM, "Paul", Role.CHILD, user_id=hass_read_only_user.id)
    await entry.runtime_data.async_save()
    return entry


def _local(hour: int, minute: int = 0) -> datetime:
    return dt_util.as_utc(
        dt_util.now().replace(year=2026, month=11, day=2, hour=hour, minute=minute, second=0, microsecond=0)
    )


def _ids(entry):
    family = entry.runtime_data.family
    by = {m.name: m.id for m in family.members.values()}
    return family, by


async def test_uebernehmen_erst_ab_1630_doppelt_ab_19(
    hass: HomeAssistant, setup, hass_read_only_user, freezer: FrozenDateTimeFactory
) -> None:
    family, by = _ids(setup)
    a = family.create_chore(SYSTEM, "Müll", [by["Finn"]], points=2)
    b = family.create_chore(SYSTEM, "Tisch", [by["Finn"]], points=2)
    ctx = Context(user_id=hass_read_only_user.id)

    freezer.move_to(_local(15, 0))
    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            DOMAIN, "take_over_chore", {"chore_id": a.id}, blocking=True, context=ctx
        )

    freezer.move_to(_local(17, 0))
    await hass.services.async_call(DOMAIN, "take_over_chore", {"chore_id": a.id}, blocking=True, context=ctx)
    assert family.members[by["Paul"]].points == 2

    freezer.move_to(_local(19, 30))
    await hass.services.async_call(DOMAIN, "take_over_chore", {"chore_id": b.id}, blocking=True, context=ctx)
    assert family.members[by["Paul"]].points == 6
    assert family.members[by["Finn"]].points == 0


async def _upload(client, chore_id: str, data: bytes = b"\xff\xd8fakejpeg", ctype: str = "image/jpeg", mode: str = "claim"):
    form = aiohttp.FormData()
    form.add_field("chore_id", chore_id)
    form.add_field("mode", mode)
    form.add_field("file", data, filename="x.jpg", content_type=ctype)
    return await client.post("/api/sternchenplan/photo", data=form)


async def test_foto_hochladen_und_nur_eltern_sehen_es(
    hass: HomeAssistant, setup, hass_client, hass_read_only_access_token, aiohttp_client, hass_admin_user, hass_read_only_user
) -> None:
    family, by = _ids(setup)
    chore = family.create_chore(
        SYSTEM, "Bad", [by["Paul"]], points=3, requires_photo=True, requires_approval=True
    )
    await setup.runtime_data.async_save()

    await hass_client()  # startet den HTTP-Server im Test
    # Kind lädt hoch (eigenes Token)
    kid = await aiohttp_client(hass.http.app, headers={"Authorization": f"Bearer {hass_read_only_access_token}"})
    bad = await _upload(kid, chore.id, b"<html>", "text/html")
    assert bad.status == 415
    assert chore.state is ChoreState.OPEN

    resp = await _upload(kid, chore.id)
    assert resp.status == 200, await resp.text()
    assert chore.state is ChoreState.CLAIMED
    assert chore.photo and (photo_dir(hass) / chore.photo).is_file()

    # Kind sieht keinen Link, Eltern schon
    now = dt_util.utcnow()
    kid_view = snapshot(hass, setup, now, hass_read_only_user.id, False)
    parent_view = snapshot(hass, setup, now, hass_admin_user.id, True)
    assert next(c for c in kid_view["chores"] if c["id"] == chore.id)["photo_url"] is None
    url = next(c for c in parent_view["chores"] if c["id"] == chore.id)["photo_url"]
    assert url and "authSig=" in url

    # Signierter Link funktioniert ohne Anmeldung, ohne Signatur nicht
    anon = await aiohttp_client(hass.http.app)
    assert (await anon.get(url)).status == 200
    assert (await anon.get(f"/api/sternchenplan/photo/{chore.photo}")).status == 401

    # Zweiter Upload auf gemeldete Aufgabe wird abgelehnt und nichts gespeichert
    files_before = set(os.listdir(photo_dir(hass)))
    again = await _upload(kid, chore.id)
    assert again.status == 400
    assert set(os.listdir(photo_dir(hass))) == files_before


async def test_fotos_werden_nach_frist_geloescht(hass: HomeAssistant, setup) -> None:
    family, by = _ids(setup)
    chore = family.create_chore(SYSTEM, "Bad", [by["Paul"]])
    folder = photo_dir(hass)
    folder.mkdir(parents=True, exist_ok=True)
    old = folder / "alt.jpg"
    new = folder / "neu.jpg"
    old.write_bytes(b"x")
    new.write_bytes(b"x")
    eight_days = time.time() - 8 * 86400
    os.utime(old, (eight_days, eight_days))
    chore.photo = "alt.jpg"

    assert await hass.async_add_executor_job(cleanup, hass, setup)
    assert not old.exists() and new.exists()
    assert forget_missing(hass, setup)
    assert chore.photo is None


async def _photo_claim(hass, setup, kid_client):
    family, by = _ids(setup)
    chore = family.create_chore(SYSTEM, "Zimmer", [by["Paul"]], points=2, requires_photo=True)
    await setup.runtime_data.async_save()
    resp = await _upload(kid_client, chore.id)
    assert resp.status == 200, await resp.text()
    assert chore.state is ChoreState.CLAIMED  # Foto geht immer an die Eltern
    return chore, photo_dir(hass) / chore.photo


@pytest.mark.parametrize(("delete", "kept"), [(True, False), (False, True)])
async def test_foto_nach_bestaetigung(
    hass: HomeAssistant, setup, hass_client, hass_read_only_access_token, aiohttp_client,
    hass_admin_user, delete, kept,
) -> None:
    hass.config_entries.async_update_entry(setup, options={"photo_delete_after_review": delete})
    await hass.async_block_till_done()
    await hass_client()
    kid = await aiohttp_client(hass.http.app, headers={"Authorization": f"Bearer {hass_read_only_access_token}"})
    chore, path = await _photo_claim(hass, setup, kid)
    await hass.services.async_call(
        DOMAIN, "approve_chore", {"chore_id": chore.id}, blocking=True,
        context=Context(user_id=hass_admin_user.id),
    )
    assert path.exists() is kept
    assert (chore.photo is not None) is kept


async def test_zuruecknehmen_loescht_foto_immer(
    hass: HomeAssistant, setup, hass_client, hass_read_only_access_token, aiohttp_client,
    hass_read_only_user,
) -> None:
    hass.config_entries.async_update_entry(setup, options={"photo_delete_after_review": False})
    await hass.async_block_till_done()
    await hass_client()
    kid = await aiohttp_client(hass.http.app, headers={"Authorization": f"Bearer {hass_read_only_access_token}"})
    chore, path = await _photo_claim(hass, setup, kid)
    await hass.services.async_call(
        DOMAIN, "undo_claim", {"chore_id": chore.id}, blocking=True,
        context=Context(user_id=hass_read_only_user.id),
    )
    assert not path.exists()
    assert chore.photo is None
