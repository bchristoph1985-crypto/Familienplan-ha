"""Sparziel pro Kind und gemeinsames Familienziel."""

from __future__ import annotations

import pytest

from custom_components.sternchenplan.core import SYSTEM, Family, FamilyError, PermissionDenied

from .test_core import NOW, actor, by_name, family  # noqa: F401
from .test_progress import _done


def test_sparziel_meldet_einmal_wenn_es_reicht(family: Family) -> None:  # noqa: F811
    lucas = by_name(family, "Lucas")
    kino = family.create_reward(SYSTEM, "Kino", 5)
    family.set_goal(actor(family, "Lucas"), lucas.id, kino.id)
    _done(family, "Lucas", NOW, points=3)
    assert not any(e["type"] == "goal_ready" for e in family.pop_events())
    _done(family, "Lucas", NOW, points=3)
    assert {"type": "goal_ready", "member": lucas.id, "reward": "Kino"} in family.pop_events()
    _done(family, "Lucas", NOW)
    assert not any(e["type"] == "goal_ready" for e in family.pop_events())
    # Einlösen erfüllt das Ziel
    family.redeem(actor(family, "Lucas"), kino.id, lucas.id, NOW)
    assert lucas.goal_reward_id is None


def test_sparziel_nur_fuer_sich_und_passende_belohnung(family: Family) -> None:  # noqa: F811
    lucas, osmo = by_name(family, "Lucas"), by_name(family, "Osmo")
    nur_osmo = family.create_reward(SYSTEM, "Lego", 50, [osmo.id])
    alle = family.create_reward(SYSTEM, "Eis", 5)
    with pytest.raises(PermissionDenied):
        family.set_goal(actor(family, "Lucas"), osmo.id, alle.id)
    with pytest.raises(FamilyError):
        family.set_goal(actor(family, "Lucas"), lucas.id, nur_osmo.id)
    family.set_goal(SYSTEM, lucas.id, alle.id)
    family.delete_reward(SYSTEM, alle.id)
    assert lucas.goal_reward_id is None


def test_familienziel_sammelt_von_allen_kindern(family: Family) -> None:  # noqa: F811
    with pytest.raises(PermissionDenied):
        family.set_family_goal(actor(family, "Lucas"), "Freizeitpark", 10, NOW)
    family.set_family_goal(SYSTEM, "Freizeitpark", 10, NOW)
    _done(family, "Lucas", NOW, points=4)
    _done(family, "Osmo", NOW, points=4)
    assert family.goal.progress == 8
    assert by_name(family, "Lucas").points == 4  # nichts abgezogen
    family.pop_events()
    _done(family, "Osmo", NOW, points=5)
    assert family.goal.progress == 10
    assert family.goal.reached_at == NOW
    assert {"type": "family_goal", "name": "Freizeitpark"} in family.pop_events()
    _done(family, "Lucas", NOW, points=5)
    assert not any(e["type"] == "family_goal" for e in family.pop_events())

    restored = Family.from_dict(family.to_dict())
    assert restored.goal.name == "Freizeitpark"
    assert restored.goal.reached_at == NOW
    family.clear_family_goal(SYSTEM)
    assert family.goal is None
