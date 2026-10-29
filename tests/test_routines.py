"""Routinen: Aufgaben mit Schritten zum einzelnen Abhaken."""

from __future__ import annotations

from datetime import timedelta

import pytest

from custom_components.sternchenplan.core import (
    SYSTEM,
    ChoreState,
    Family,
    FamilyError,
    PermissionDenied,
    Recurrence,
)

from .test_core import NOW, actor, by_name, family  # noqa: F401

STEPS = ["Anziehen", "Zähne putzen", "Bett machen"]


def _routine(fam: Family, **kw):
    lucas = by_name(fam, "Lucas")
    return lucas, fam.create_chore(
        SYSTEM, "Morgenroutine", [lucas.id], points=3, recurrence=Recurrence.DAILY,
        due=NOW + timedelta(hours=1), steps=[" Anziehen ", "", "Zähne putzen", "Bett machen"], **kw
    )


def test_schritte_abhaken_meldet_am_ende(family: Family) -> None:  # noqa: F811
    lucas, chore = _routine(family)
    assert chore.steps == STEPS  # leere Zeilen und Leerzeichen raus
    kid = actor(family, "Lucas")
    family.check_step(kid, chore.id, lucas.id, 0, True, NOW)
    family.check_step(kid, chore.id, lucas.id, 2, True, NOW)
    family.check_step(kid, chore.id, lucas.id, 2, False, NOW)
    assert chore.steps_done == [0]
    assert lucas.points == 0
    family.check_step(kid, chore.id, lucas.id, 1, True, NOW)
    family.check_step(kid, chore.id, lucas.id, 2, True, NOW)
    assert lucas.points == 3
    assert chore.steps_done == []  # neue Runde für morgen
    assert chore.state is ChoreState.OPEN


def test_schritte_mit_foto_und_freigabe(family: Family) -> None:  # noqa: F811
    lucas, chore = _routine(family, requires_photo=True)
    kid = actor(family, "Lucas")
    for i in range(3):
        family.check_step(kid, chore.id, lucas.id, i, True, NOW)
    assert chore.state is ChoreState.OPEN  # Foto fehlt noch, Kind tippt selbst
    family.claim(kid, chore.id, lucas.id, NOW, photo="x.jpg")
    assert chore.state is ChoreState.CLAIMED
    family.reject(SYSTEM, chore.id, NOW)
    assert chore.steps_done == []


def test_schritte_rechte_und_grenzen(family: Family) -> None:  # noqa: F811
    lucas, chore = _routine(family)
    with pytest.raises(PermissionDenied):
        family.check_step(actor(family, "Osmo"), chore.id, lucas.id, 0, True, NOW)
    with pytest.raises(FamilyError):
        family.check_step(actor(family, "Lucas"), chore.id, lucas.id, 5, True, NOW)
    with pytest.raises(FamilyError):
        family.create_chore(SYSTEM, "Zu lang", [lucas.id], steps=[str(i) for i in range(13)])
    family.check_step(actor(family, "Lucas"), chore.id, lucas.id, 0, True, NOW)
    family.update_chore(SYSTEM, chore.id, NOW, steps=["Neu"])
    assert chore.steps == ["Neu"] and chore.steps_done == []
    restored = Family.from_dict(family.to_dict())
    assert restored.chores[chore.id].steps == ["Neu"]
