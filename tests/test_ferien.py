"""Ferien-Pause, Wochentage und Bilder-Modus."""

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
from .test_progress import _done

# NOW: Montag, 2. November 2026, 17:00 UTC


def test_ferien_pause(family: Family) -> None:  # noqa: F811
    finn = by_name(family, "Finn")
    chore = family.create_chore(
        SYSTEM, "Müll", [finn.id], recurrence=Recurrence.DAILY, due=NOW + timedelta(hours=2)
    )
    family.set_devices(SYSTEM, finn.id, ["switch.ps5"])
    _done(family, "Finn", NOW - timedelta(days=1))  # Serie läuft
    with pytest.raises(PermissionDenied):
        family.set_pause(actor(family, "Finn"), NOW, NOW + timedelta(days=7))
    family.set_pause(SYSTEM, NOW, NOW + timedelta(days=7))
    later = NOW + timedelta(days=3)
    family.refresh(later)
    assert family.responsible(chore, later) == []
    assert chore.state is ChoreState.OPEN  # nicht überfällig
    assert not family.should_lock(finn.id, later)

    after = NOW + timedelta(days=7, minutes=1)
    assert family.refresh(after)
    assert family.pause_until is None
    assert chore.due > after
    assert chore.due.hour == 19  # Uhrzeit bleibt
    _done(family, "Finn", after)
    assert finn.progress.streak == 2  # Ferien reißen die Serie nicht


def test_pause_vorzeitig_beenden(family: Family) -> None:  # noqa: F811
    family.set_pause(SYSTEM, NOW + timedelta(days=1), NOW + timedelta(days=5))
    family.end_pause(SYSTEM, NOW)  # noch nicht angefangen: einfach weg
    assert family.pause_until is None
    with pytest.raises(FamilyError):
        family.end_pause(SYSTEM, NOW)
    family.set_pause(SYSTEM, NOW, NOW + timedelta(days=5))
    family.end_pause(SYSTEM, NOW + timedelta(days=1))
    assert not family.is_paused(NOW + timedelta(days=2))
    restored = Family.from_dict(family.to_dict())
    assert restored.pause_until is None


def test_nur_an_schultagen(family: Family) -> None:  # noqa: F811
    finn = by_name(family, "Finn")
    friday = NOW + timedelta(days=4)
    chore = family.create_chore(
        SYSTEM, "Ranzen", [finn.id], recurrence=Recurrence.DAILY,
        due=friday, weekdays=[0, 1, 2, 3, 4],
    )
    family.claim(actor(family, "Finn"), chore.id, finn.id, friday - timedelta(hours=1))
    assert chore.due.weekday() == 0  # Montag statt Samstag
    assert (chore.due - friday).days == 3
    # Start an einem Sonntag springt auf Montag
    sunday = NOW + timedelta(days=6)
    c2 = family.create_chore(SYSTEM, "X", [finn.id], recurrence=Recurrence.DAILY, due=sunday, weekdays=[0])
    assert c2.due.weekday() == 0
    with pytest.raises(FamilyError):
        family.create_chore(SYSTEM, "Y", [finn.id], weekdays=[7])


def test_bilder_modus(family: Family) -> None:  # noqa: F811
    finn = by_name(family, "Finn")
    with pytest.raises(PermissionDenied):
        family.set_picture_mode(actor(family, "Finn"), finn.id, True)
    family.set_picture_mode(SYSTEM, finn.id, True)
    assert Family.from_dict(family.to_dict()).members[finn.id].picture_mode
