"""NFC-Aufkleber und Sprachbefehle."""

from __future__ import annotations

import pytest
from pytest_homeassistant_custom_component.common import async_mock_service

from homeassistant.components import conversation
from homeassistant.core import Context, HomeAssistant
from homeassistant.setup import async_setup_component

from custom_components.sternchenplan.const import DOMAIN
from custom_components.sternchenplan.core import SYSTEM, ChoreState, Family, FamilyError

from .test_core import NOW, by_name, family  # noqa: F401
from .test_reminders import auto_enable_custom_integrations, entry  # noqa: F401


def test_gesprochenes_zuordnen(family: Family) -> None:  # noqa: F811
    lucas = by_name(family, "Lucas")
    muell = family.create_chore(SYSTEM, "Müll rausbringen", [lucas.id])
    tisch = family.create_chore(SYSTEM, "Tisch decken", [lucas.id])
    assert family.match_chore(lucas.id, "den Müll rausgebracht", NOW) is muell
    assert family.match_chore(lucas.id, "den tisch gedeckt", NOW) is tisch
    assert family.match_chore(lucas.id, "Hausaufgaben", NOW) is None
    foto = family.create_chore(SYSTEM, "Zimmer", [lucas.id], requires_photo=True)
    with pytest.raises(FamilyError):
        family.claim_hands_free(lucas.id, foto, NOW)
    family.claim_hands_free(lucas.id, muell, NOW)
    assert muell.state is ChoreState.DONE


@pytest.fixture
async def voice(hass: HomeAssistant, entry):  # noqa: F811
    assert await async_setup_component(hass, "homeassistant", {})
    assert await async_setup_component(hass, "conversation", {})
    await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()
    return entry


async def _say(hass: HomeAssistant, text: str, user_id: str | None = None) -> str:
    result = await conversation.async_converse(
        hass, text, None, Context(user_id=user_id), language="de"
    )
    return result.response.speech["plain"]["speech"]


async def test_sprachbefehle(hass: HomeAssistant, voice, hass_read_only_user) -> None:
    fam = voice.runtime_data.family
    lucas = next(m for m in fam.members.values() if m.name == "Lucas")
    muell = next(c for c in fam.chores.values() if c.name == "Müll")

    assert "noch offen: Müll" in await _say(hass, "Was muss Lucas noch machen")
    assert "Wer bist du" in await _say(hass, "Ich habe den Müll rausgebracht")
    answer = await _say(hass, "Ich habe den Müll rausgebracht", hass_read_only_user.id)
    assert answer.startswith("Super, Lucas")
    assert muell.state is not ChoreState.OVERDUE and lucas.points == 1
    assert "1 Sterne" in await _say(hass, "Wie viele Sterne hat Lucas")
    assert "kein Kind namens Paul" in await _say(hass, "Paul hat den Müll rausgebracht")
    # Lucas darf nicht für Osmo melden
    assert "nur für dich" in await _say(hass, "Osmo hat den Tisch gedeckt", hass_read_only_user.id)


async def test_nfc_aufkleber(hass: HomeAssistant, entry, hass_admin_user, hass_read_only_user) -> None:  # noqa: F811
    lucas_calls = async_mock_service(hass, "notify", "lucas_handy")
    fam = entry.runtime_data.family
    muell = next(c for c in fam.chores.values() if c.name == "Müll")

    # Anlernen: Eltern drücken in der Karte, dann Aufkleber scannen
    await hass.services.async_call(DOMAIN, "learn_tag", {"chore_id": muell.id}, blocking=True)
    hass.bus.async_fire("tag_scanned", {"tag_id": "tonne-1"}, context=Context(user_id=hass_admin_user.id))
    await hass.async_block_till_done()
    assert muell.tag_id == "tonne-1"
    assert muell.state is ChoreState.OPEN

    # Lucas scannt mit seinem Handy
    hass.bus.async_fire("tag_scanned", {"tag_id": "tonne-1"}, context=Context(user_id=hass_read_only_user.id))
    await hass.async_block_till_done()
    assert muell.last_completed_by is not None
    assert "Super, Lucas" in lucas_calls[-1].data["message"]

    # Noch mal: nichts mehr offen
    hass.bus.async_fire("tag_scanned", {"tag_id": "tonne-1"}, context=Context(user_id=hass_read_only_user.id))
    await hass.async_block_till_done()
    assert "nichts offen" in lucas_calls[-1].data["message"]
    # Fremder Aufkleber: ignoriert
    hass.bus.async_fire("tag_scanned", {"tag_id": "haustuer"})
    await hass.async_block_till_done()
