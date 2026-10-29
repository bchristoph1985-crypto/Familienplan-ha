"""Bonus-Sterne und Abzug durch die Eltern."""

from __future__ import annotations

import pytest
from pytest_homeassistant_custom_component.common import async_mock_service

from homeassistant.core import HomeAssistant

from custom_components.sternchenplan.const import DOMAIN
from custom_components.sternchenplan.core import SYSTEM, Family, FamilyError, PermissionDenied

from .test_core import NOW, actor, by_name, family  # noqa: F401
from .test_reminders import auto_enable_custom_integrations, entry  # noqa: F401


def test_bonus_zaehlt_fuer_level_und_ziel(family: Family) -> None:  # noqa: F811
    lucas = by_name(family, "Lucas")
    family.set_family_goal(SYSTEM, "Zoo", 10, NOW)
    family.pop_events()
    assert family.give_stars(SYSTEM, lucas.id, 12, "Beim Einkaufen geholfen", NOW) == 12
    assert lucas.points == 12
    assert lucas.progress.earned == 12
    assert family.goal.reached_at == NOW
    types = [e["type"] for e in family.pop_events()]
    assert "stars" in types and "level" in types and "family_goal" in types
    assert family.star_history(lucas.id)[0]["reason"] == "Beim Einkaufen geholfen"


def test_abzug_nie_unter_null_und_kein_levelverlust(family: Family) -> None:  # noqa: F811
    lucas = by_name(family, "Lucas")
    family.give_stars(SYSTEM, lucas.id, 3, "", NOW)
    level = lucas.progress.level
    assert family.give_stars(SYSTEM, lucas.id, -5, "Streit", NOW) == -3
    assert lucas.points == 0
    assert lucas.progress.level == level
    family.pop_events()
    assert family.give_stars(SYSTEM, lucas.id, -2, "Streit", NOW) == 0
    assert family.pop_events() == []  # nichts abgezogen, keine Nachricht
    with pytest.raises(PermissionDenied):
        family.give_stars(actor(family, "Osmo"), lucas.id, 5, "", NOW)
    with pytest.raises(FamilyError):
        family.give_stars(SYSTEM, lucas.id, 0, "", NOW)


def test_vorschlaege(family: Family) -> None:  # noqa: F811
    assert [p["stars"] for p in family.presets] == [3, 2, -1, -2]
    preset = family.add_preset(SYSTEM, "Zimmer super", 4)
    family.delete_preset(SYSTEM, family.presets[0]["id"])
    restored = Family.from_dict(family.to_dict())
    assert [p["name"] for p in restored.presets][-1] == "Zimmer super"
    assert len(restored.presets) == 4
    with pytest.raises(FamilyError):
        family.delete_preset(SYSTEM, "gibtsnicht")
    with pytest.raises(PermissionDenied):
        family.add_preset(actor(family, "Lucas"), "Ich", 50)
    assert preset["id"]


async def test_bonus_per_dienst(hass: HomeAssistant, entry) -> None:  # noqa: F811
    lucas_calls = async_mock_service(hass, "notify", "lucas_handy")
    events = []
    hass.bus.async_listen("sternchenplan_stars", events.append)
    await hass.services.async_call(
        DOMAIN, "give_stars", {"member": "Lucas", "stars": 2, "reason": "Lieb"}, blocking=True
    )
    await hass.async_block_till_done()
    assert any("+2 Bonus: Lieb" in c.data["message"] for c in lucas_calls)
    assert events[0].data["stars"] == 2
    await hass.services.async_call(
        DOMAIN, "give_stars", {"member": "Lucas", "stars": -1, "reason": "Frech"}, blocking=True
    )
    await hass.async_block_till_done()
    assert any("-1 Sterne: Frech" in c.data["message"] for c in lucas_calls)
