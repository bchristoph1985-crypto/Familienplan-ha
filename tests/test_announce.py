"""Ansagen über Lautsprecher."""

from __future__ import annotations

from datetime import timedelta

import pytest
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_fire_time_changed,
    async_mock_service,
)

from homeassistant.core import Context, HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.util import dt as dt_util

from custom_components.familienplan.const import DOMAIN
from custom_components.familienplan.core import SYSTEM, Recurrence, Role


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    yield


async def _setup(hass: HomeAssistant, options: dict, admin, kid) -> MockConfigEntry:
    await hass.config.async_set_time_zone("UTC")
    hass.config.language = "de"
    entry = MockConfigEntry(domain=DOMAIN, options={"reminder_times": "", "parent_summary_time": "", **options})
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    family = entry.runtime_data.family
    family.add_member(SYSTEM, "Papa", Role.PARENT, user_id=admin.id)
    lucas = family.add_member(SYSTEM, "Lucas", Role.CHILD, user_id=kid.id)
    osmo = family.add_member(SYSTEM, "Osmo", Role.CHILD)
    now = dt_util.utcnow()
    family.create_chore(SYSTEM, "Müll", [lucas.id], recurrence=Recurrence.DAILY, due=now.replace(hour=19))
    family.create_chore(SYSTEM, "Tisch decken", [lucas.id], recurrence=Recurrence.DAILY, due=now.replace(hour=19))
    family.create_chore(SYSTEM, "Bad", [osmo.id], due=now + timedelta(days=2))
    await entry.runtime_data.async_save()
    # Neu laden, damit die Zeitpläne mit den Optionen stehen.
    await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()
    return entry


async def test_ansage_ueber_tts_und_alexa(
    hass: HomeAssistant, freezer, hass_admin_user, hass_read_only_user
) -> None:
    freezer.move_to("2026-11-02 08:00:00+00:00")
    tts_calls = async_mock_service(hass, "tts", "speak")
    alexa_calls = async_mock_service(hass, "notify", "alexa_media_kueche")
    await _setup(
        hass,
        {
            "announce_times": "17:00",
            "tts_engine": "tts.piper",
            "speakers": ["media_player.kueche", "media_player.flur"],
            "announce_notify": ["alexa_media_kueche"],
        },
        hass_admin_user,
        hass_read_only_user,
    )

    freezer.move_to("2026-11-02 17:00:00+00:00")
    async_fire_time_changed(hass)
    await hass.async_block_till_done()

    assert len(tts_calls) == 1
    data = tts_calls[0].data
    assert data["entity_id"] == "tts.piper"
    assert data["media_player_entity_id"] == ["media_player.kueche", "media_player.flur"]
    assert data["message"] == "Lucas, bei dir ist noch offen: Müll und Tisch decken."
    assert len(alexa_calls) == 1
    assert alexa_calls[0].data["data"] == {"type": "announce"}


async def test_keine_ansage_wenn_alles_erledigt_oder_nichts_eingestellt(
    hass: HomeAssistant, freezer, hass_admin_user, hass_read_only_user
) -> None:
    freezer.move_to("2026-11-02 08:00:00+00:00")
    tts_calls = async_mock_service(hass, "tts", "speak")
    entry = await _setup(hass, {"announce_times": "17:00"}, hass_admin_user, hass_read_only_user)
    freezer.move_to("2026-11-02 17:00:00+00:00")
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert tts_calls == []

    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(DOMAIN, "announce", {}, blocking=True)
    assert entry.state.name == "LOADED"


async def test_dienst_ansage_nur_fuer_eltern(
    hass: HomeAssistant, freezer, hass_admin_user, hass_read_only_user
) -> None:
    freezer.move_to("2026-11-02 08:00:00+00:00")
    tts_calls = async_mock_service(hass, "tts", "speak")
    await _setup(
        hass,
        {"announce_times": "", "tts_engine": "tts.piper", "speakers": ["media_player.kueche"]},
        hass_admin_user,
        hass_read_only_user,
    )
    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            DOMAIN, "announce", {"message": "Hallo"}, blocking=True,
            context=Context(user_id=hass_read_only_user.id),
        )
    assert tts_calls == []

    await hass.services.async_call(
        DOMAIN, "announce", {"message": "Essen ist fertig"}, blocking=True,
        context=Context(user_id=hass_admin_user.id),
    )
    await hass.services.async_call(DOMAIN, "announce", {}, blocking=True)
    assert [c.data["message"] for c in tts_calls] == [
        "Essen ist fertig",
        "Lucas, bei dir ist noch offen: Müll und Tisch decken.",
    ]


async def test_optionen_ansagen(hass: HomeAssistant, hass_admin_user, hass_read_only_user) -> None:
    entry = await _setup(hass, {}, hass_admin_user, hass_read_only_user)
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "announcements"}
    )
    assert result["step_id"] == "announcements"
    bad = await hass.config_entries.options.async_configure(
        result["flow_id"], {"announce_times": "17:00", "speakers": ["media_player.kueche"]}
    )
    assert bad["errors"] == {"base": "tts_missing"}
    done = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {"announce_times": "18:00", "speakers": ["media_player.kueche"], "tts_engine": "tts.piper"},
    )
    assert done["type"] == "create_entry"
    assert entry.options["tts_engine"] == "tts.piper"
    assert entry.options["announce_notify"] == []


async def test_einloesen_schickt_push_an_eltern(
    hass: HomeAssistant, freezer, hass_admin_user, hass_read_only_user
) -> None:
    freezer.move_to("2026-11-02 08:00:00+00:00")
    entry = await _setup(hass, {}, hass_admin_user, hass_read_only_user)
    family = entry.runtime_data.family
    papa = next(m for m in family.members.values() if m.name == "Papa")
    papa.notify_service = "papa_handy"
    lucas = next(m for m in family.members.values() if m.name == "Lucas")
    lucas.points = 20
    reward = family.create_reward(SYSTEM, "Eis", 15)
    await entry.runtime_data.async_save()
    calls = async_mock_service(hass, "notify", "papa_handy")

    await hass.services.async_call(
        DOMAIN, "redeem_reward", {"reward_id": reward.id}, blocking=True,
        context=Context(user_id=hass_read_only_user.id),
    )
    await hass.async_block_till_done()
    assert lucas.points == 5
    assert calls[0].data["message"] == "Lucas möchte eine Belohnung einlösen: Eis"
    redemption = family.pending_redemptions()[0]

    # Kind kann sich nicht selbst bestätigen
    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            DOMAIN, "approve_redemption", {"redemption_id": redemption.id}, blocking=True,
            context=Context(user_id=hass_read_only_user.id),
        )
    await hass.services.async_call(
        DOMAIN, "approve_redemption", {"redemption_id": redemption.id}, blocking=True,
        context=Context(user_id=hass_admin_user.id),
    )
    assert family.pending_redemptions() == []
