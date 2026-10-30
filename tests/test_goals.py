"""Sparziel pro Kind und gemeinsames Familienziel."""

from __future__ import annotations

import pytest

from custom_components.sternchenplan.core import SYSTEM, Family, FamilyError, PermissionDenied

from .test_core import NOW, actor, by_name, family  # noqa: F401
from .test_progress import _done


def test_sparziel_meldet_einmal_wenn_es_reicht(family: Family) -> None:  # noqa: F811
    finn = by_name(family, "Finn")
    kino = family.create_reward(SYSTEM, "Kino", 5)
    family.set_goal(actor(family, "Finn"), finn.id, kino.id)
    _done(family, "Finn", NOW, points=3)
    assert not any(e["type"] == "goal_ready" for e in family.pop_events())
    _done(family, "Finn", NOW, points=3)
    assert {"type": "goal_ready", "member": finn.id, "reward": "Kino"} in family.pop_events()
    _done(family, "Finn", NOW)
    assert not any(e["type"] == "goal_ready" for e in family.pop_events())
    # Einlösen erfüllt das Ziel
    family.redeem(actor(family, "Finn"), kino.id, finn.id, NOW)
    assert finn.goal_reward_id is None


def test_sparziel_nur_fuer_sich_und_passende_belohnung(family: Family) -> None:  # noqa: F811
    finn, paul = by_name(family, "Finn"), by_name(family, "Paul")
    nur_osmo = family.create_reward(SYSTEM, "Lego", 50, [paul.id])
    alle = family.create_reward(SYSTEM, "Eis", 5)
    with pytest.raises(PermissionDenied):
        family.set_goal(actor(family, "Finn"), paul.id, alle.id)
    with pytest.raises(FamilyError):
        family.set_goal(actor(family, "Finn"), finn.id, nur_osmo.id)
    family.set_goal(SYSTEM, finn.id, alle.id)
    family.delete_reward(SYSTEM, alle.id)
    assert finn.goal_reward_id is None


def test_familienziel_sammelt_von_allen_kindern(family: Family) -> None:  # noqa: F811
    with pytest.raises(PermissionDenied):
        family.set_family_goal(actor(family, "Finn"), "Freizeitpark", 10, NOW)
    family.set_family_goal(SYSTEM, "Freizeitpark", 10, NOW)
    _done(family, "Finn", NOW, points=4)
    _done(family, "Paul", NOW, points=4)
    assert family.goal.progress == 8
    assert by_name(family, "Finn").points == 4  # nichts abgezogen
    family.pop_events()
    _done(family, "Paul", NOW, points=5)
    assert family.goal.progress == 10
    assert family.goal.reached_at == NOW
    assert {"type": "family_goal", "name": "Freizeitpark"} in family.pop_events()
    _done(family, "Finn", NOW, points=5)
    assert not any(e["type"] == "family_goal" for e in family.pop_events())

    restored = Family.from_dict(family.to_dict())
    assert restored.goal.name == "Freizeitpark"
    assert restored.goal.reached_at == NOW
    family.clear_family_goal(SYSTEM)
    assert family.goal is None
