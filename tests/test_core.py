"""Tests für den Aufgaben-Kern, laufen ohne Home Assistant."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from custom_components.familienplan.core import (
    SYSTEM,
    Actor,
    ChoreState,
    Family,
    FamilyError,
    PermissionDenied,
    Recurrence,
    Role,
)

NOW = datetime(2026, 11, 2, 17, 0, tzinfo=timezone.utc)


@pytest.fixture
def family() -> Family:
    fam = Family()
    fam.add_member(SYSTEM, "Papa", Role.PARENT, user_id="u_papa")
    fam.add_member(SYSTEM, "Lucas", Role.CHILD, user_id="u_lucas")
    fam.add_member(SYSTEM, "Osmo", Role.CHILD, user_id="u_osmo")
    return fam


def by_name(fam: Family, name: str):
    return next(m for m in fam.members.values() if m.name == name)


def actor(fam: Family, name: str) -> Actor:
    return fam.actor_for_user(by_name(fam, name).user_id, is_admin=False)


def test_kind_darf_keine_aufgabe_anlegen(family: Family) -> None:
    lucas = by_name(family, "Lucas")
    with pytest.raises(PermissionDenied):
        family.create_chore(actor(family, "Lucas"), "Müll", [lucas.id])


def test_unbekanntes_konto_ohne_admin_ist_kein_elternteil(family: Family) -> None:
    fremd = family.actor_for_user("u_fremd", is_admin=False)
    assert not fremd.is_manager
    assert family.actor_for_user("u_fremd", is_admin=True).is_manager


def test_einfache_aufgabe_erledigen_gibt_punkte(family: Family) -> None:
    lucas = by_name(family, "Lucas")
    chore = family.create_chore(SYSTEM, "Tisch decken", [lucas.id], points=2)
    family.claim(actor(family, "Lucas"), chore.id, lucas.id, NOW)
    assert chore.state is ChoreState.DONE
    assert lucas.points == 2


def test_kind_kann_nicht_fuer_geschwister_melden(family: Family) -> None:
    lucas, osmo = by_name(family, "Lucas"), by_name(family, "Osmo")
    chore = family.create_chore(SYSTEM, "Müll", [osmo.id])
    with pytest.raises(PermissionDenied):
        family.claim(actor(family, "Lucas"), chore.id, osmo.id, NOW)
    with pytest.raises(PermissionDenied):
        family.claim(actor(family, "Lucas"), chore.id, lucas.id, NOW)
    assert chore.state is ChoreState.OPEN


def test_freigabe_ablauf(family: Family) -> None:
    lucas = by_name(family, "Lucas")
    chore = family.create_chore(
        SYSTEM, "Bad putzen", [lucas.id], points=5, requires_approval=True
    )
    family.claim(actor(family, "Lucas"), chore.id, lucas.id, NOW)
    assert chore.state is ChoreState.CLAIMED
    assert lucas.points == 0

    with pytest.raises(PermissionDenied):
        family.approve(actor(family, "Lucas"), chore.id, NOW)

    family.approve(actor(family, "Papa"), chore.id, NOW)
    assert chore.state is ChoreState.DONE
    assert lucas.points == 5


def test_ablehnen_und_eigene_meldung_zuruecknehmen(family: Family) -> None:
    lucas, osmo = by_name(family, "Lucas"), by_name(family, "Osmo")
    chore = family.create_chore(
        SYSTEM, "Zimmer", [lucas.id, osmo.id], requires_approval=True
    )
    family.claim(actor(family, "Lucas"), chore.id, lucas.id, NOW)
    with pytest.raises(PermissionDenied):
        family.undo_claim(actor(family, "Osmo"), chore.id)
    family.undo_claim(actor(family, "Lucas"), chore.id)
    assert chore.state is ChoreState.OPEN

    family.claim(actor(family, "Lucas"), chore.id, lucas.id, NOW)
    family.reject(actor(family, "Papa"), chore.id, NOW)
    assert chore.state is ChoreState.OPEN
    assert lucas.points == 0


def test_rotation_wechselt_nach_erledigung(family: Family) -> None:
    lucas, osmo = by_name(family, "Lucas"), by_name(family, "Osmo")
    chore = family.create_chore(
        SYSTEM,
        "Spülmaschine",
        [lucas.id, osmo.id],
        recurrence=Recurrence.DAILY,
        due=NOW,
        rotation=True,
    )
    assert family.responsible(chore, NOW) == [lucas.id]
    family.claim(actor(family, "Lucas"), chore.id, lucas.id, NOW)
    assert family.responsible(chore, NOW) == [osmo.id]
    assert chore.state is ChoreState.OPEN
    assert chore.due == NOW + timedelta(days=1)


def test_verspaetete_erledigung_haelt_den_takt(family: Family) -> None:
    lucas = by_name(family, "Lucas")
    first_due = NOW - timedelta(days=3)
    chore = family.create_chore(
        SYSTEM, "Pflanzen", [lucas.id], recurrence=Recurrence.WEEKLY, due=first_due
    )
    family.refresh(NOW)
    assert chore.state is ChoreState.OVERDUE
    family.claim(actor(family, "Lucas"), chore.id, lucas.id, NOW)
    assert chore.due == first_due + timedelta(weeks=1)
    assert chore.due > NOW


def test_doppelt_melden_wird_abgelehnt(family: Family) -> None:
    lucas = by_name(family, "Lucas")
    chore = family.create_chore(SYSTEM, "Einmalig", [lucas.id])
    family.claim(actor(family, "Lucas"), chore.id, lucas.id, NOW)
    with pytest.raises(FamilyError):
        family.claim(actor(family, "Lucas"), chore.id, lucas.id, NOW)
    assert lucas.points == 1


def test_mitglied_entfernen_raeumt_aufgaben_auf(family: Family) -> None:
    lucas, osmo = by_name(family, "Lucas"), by_name(family, "Osmo")
    chore = family.create_chore(
        SYSTEM,
        "Tonnen",
        [lucas.id, osmo.id],
        recurrence=Recurrence.WEEKLY,
        due=NOW,
        rotation=True,
    )
    chore.rotation_index = 1
    family.remove_member(SYSTEM, osmo.id)
    assert chore.assignees == [lucas.id]
    assert family.responsible(chore, NOW) == [lucas.id]


def test_speichern_und_laden(family: Family) -> None:
    lucas = by_name(family, "Lucas")
    chore = family.create_chore(
        SYSTEM, "Müll", [lucas.id], recurrence=Recurrence.DAILY, due=NOW, points=2
    )
    family.claim(SYSTEM, chore.id, lucas.id, NOW)
    loaded = Family.from_dict(family.to_dict())
    assert loaded.to_dict() == family.to_dict()
    assert loaded.chores[chore.id].due == NOW + timedelta(days=1)


def test_ein_ha_konto_nur_einmal(family: Family) -> None:
    with pytest.raises(FamilyError):
        family.add_member(SYSTEM, "Doppelt", Role.CHILD, user_id="u_lucas")


# -- Abwesenheit und Vertretung ---------------------------------------------


def test_rotation_ueberspringt_abwesende(family: Family) -> None:
    lucas, osmo = by_name(family, "Lucas"), by_name(family, "Osmo")
    chore = family.create_chore(
        SYSTEM, "Spülmaschine", [lucas.id, osmo.id],
        recurrence=Recurrence.DAILY, due=NOW, rotation=True,
    )
    family.set_absence(SYSTEM, lucas.id, NOW + timedelta(days=3))
    assert family.responsible(chore, NOW) == [osmo.id]
    family.claim(actor(family, "Osmo"), chore.id, osmo.id, NOW)
    # nach Osmo wäre wieder Lucas dran, der ist aber noch weg
    assert family.responsible(chore, NOW) == [osmo.id]
    # nach der Rückkehr ist Lucas wieder dran
    assert family.responsible(chore, NOW + timedelta(days=4)) == [lucas.id]


def test_vertretung_ohne_rotation(family: Family) -> None:
    lucas, osmo = by_name(family, "Lucas"), by_name(family, "Osmo")
    chore = family.create_chore(SYSTEM, "Hamster füttern", [lucas.id])
    family.set_absence(SYSTEM, lucas.id, NOW + timedelta(days=2), substitute_id=osmo.id)
    assert family.responsible(chore, NOW) == [osmo.id]
    # Osmo darf jetzt melden, Lucas nicht
    family.claim(actor(family, "Osmo"), chore.id, osmo.id, NOW)
    assert osmo.points == 1


def test_niemand_da_aufgabe_ruht(family: Family) -> None:
    lucas = by_name(family, "Lucas")
    chore = family.create_chore(
        SYSTEM, "Zimmer", [lucas.id], recurrence=Recurrence.DAILY,
        due=NOW - timedelta(hours=1),
    )
    family.set_absence(SYSTEM, lucas.id, NOW + timedelta(days=1))
    family.refresh(NOW)
    assert chore.state is ChoreState.OPEN
    assert family.responsible(chore, NOW) == []


def test_abwesenheit_endet_automatisch(family: Family) -> None:
    lucas = by_name(family, "Lucas")
    family.set_absence(
        SYSTEM, lucas.id, NOW + timedelta(days=1), start=NOW - timedelta(days=1)
    )
    assert lucas.is_away(NOW)
    assert family.refresh(NOW + timedelta(days=2))
    assert lucas.away_until is None


def test_geplante_abwesenheit_beginnt_spaeter(family: Family) -> None:
    lucas = by_name(family, "Lucas")
    family.set_absence(
        SYSTEM, lucas.id, NOW + timedelta(days=5), start=NOW + timedelta(days=2)
    )
    assert not lucas.is_away(NOW)
    assert lucas.is_away(NOW + timedelta(days=3))


def test_kind_darf_keine_abwesenheit_setzen(family: Family) -> None:
    lucas = by_name(family, "Lucas")
    with pytest.raises(PermissionDenied):
        family.set_absence(actor(family, "Lucas"), lucas.id, NOW + timedelta(days=1))
    with pytest.raises(FamilyError):
        family.set_absence(SYSTEM, lucas.id, NOW + timedelta(days=1), substitute_id=lucas.id)


def test_offen_bis_fuer_erinnerungen(family: Family) -> None:
    lucas = by_name(family, "Lucas")
    heute = family.create_chore(SYSTEM, "Heute", [lucas.id], recurrence=Recurrence.DAILY, due=NOW)
    family.create_chore(
        SYSTEM, "Morgen", [lucas.id], recurrence=Recurrence.DAILY, due=NOW + timedelta(days=1)
    )
    ohne = family.create_chore(SYSTEM, "Ohne Frist", [lucas.id])
    ids = {c.id for c in family.open_until(lucas.id, NOW, NOW + timedelta(hours=6))}
    assert ids == {heute.id, ohne.id}
