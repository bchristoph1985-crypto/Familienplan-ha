"""Tests für den Aufgaben-Kern, laufen ohne Home Assistant."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from custom_components.sternchenplan.core import (
    SYSTEM,
    Actor,
    ChoreState,
    Family,
    FamilyError,
    PermissionDenied,
    Recurrence,
    RedemptionState,
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


# -- Bearbeiten -------------------------------------------------------------


def test_bearbeiten_aendert_nur_angegebenes(family: Family) -> None:
    lucas, osmo = by_name(family, "Lucas"), by_name(family, "Osmo")
    chore = family.create_chore(
        SYSTEM, "Müll", [lucas.id], points=1, recurrence=Recurrence.DAILY, due=NOW
    )
    family.update_chore(SYSTEM, chore.id, NOW, name="Müll + Gelber Sack", points=3)
    assert chore.name == "Müll + Gelber Sack"
    assert chore.points == 3
    assert chore.assignees == [lucas.id]
    assert chore.due == NOW
    family.update_chore(SYSTEM, chore.id, NOW, assignees=[osmo.id, lucas.id], rotation=True)
    assert family.responsible(chore, NOW) == [osmo.id]


def test_kind_darf_nicht_bearbeiten(family: Family) -> None:
    lucas = by_name(family, "Lucas")
    chore = family.create_chore(SYSTEM, "Müll", [lucas.id], points=1)
    with pytest.raises(PermissionDenied):
        family.update_chore(actor(family, "Lucas"), chore.id, NOW, points=50)
    assert chore.points == 1


def test_bearbeiten_regeln(family: Family) -> None:
    lucas = by_name(family, "Lucas")
    chore = family.create_chore(SYSTEM, "Müll", [lucas.id], recurrence=Recurrence.DAILY, due=NOW)
    with pytest.raises(FamilyError):
        family.update_chore(SYSTEM, chore.id, NOW, clear_due=True)
    with pytest.raises(FamilyError):
        family.update_chore(SYSTEM, chore.id, NOW, assignees=[])
    with pytest.raises(FamilyError):
        family.update_chore(SYSTEM, chore.id, NOW, name="  ")
    assert chore.name == "Müll" and chore.due == NOW


def test_neue_frist_hebt_ueberfaellig_auf(family: Family) -> None:
    lucas = by_name(family, "Lucas")
    chore = family.create_chore(
        SYSTEM, "Zimmer", [lucas.id], recurrence=Recurrence.WEEKLY, due=NOW - timedelta(hours=2)
    )
    family.refresh(NOW)
    assert chore.state is ChoreState.OVERDUE
    family.update_chore(SYSTEM, chore.id, NOW, due=NOW + timedelta(days=1))
    assert chore.state is ChoreState.OPEN


def test_freigabe_abschalten_bucht_offene_meldung(family: Family) -> None:
    lucas = by_name(family, "Lucas")
    chore = family.create_chore(SYSTEM, "Bad", [lucas.id], points=5, requires_approval=True)
    family.claim(actor(family, "Lucas"), chore.id, lucas.id, NOW)
    family.update_chore(SYSTEM, chore.id, NOW, requires_approval=False)
    assert chore.state is ChoreState.DONE
    assert lucas.points == 5


# -- Konsequenzen -----------------------------------------------------------


def test_sperre_nur_bei_ueberfaelligem(family: Family) -> None:
    lucas = by_name(family, "Lucas")
    family.set_devices(SYSTEM, lucas.id, ["switch.ps5_internet"])
    chore = family.create_chore(
        SYSTEM, "Müll", [lucas.id], recurrence=Recurrence.DAILY, due=NOW - timedelta(hours=1)
    )
    assert not family.should_lock(lucas.id, NOW)  # noch nicht als überfällig erkannt
    family.refresh(NOW)
    assert family.should_lock(lucas.id, NOW)
    family.claim(actor(family, "Lucas"), chore.id, lucas.id, NOW)
    assert not family.should_lock(lucas.id, NOW)


def test_gemeldet_wartet_auf_freigabe_sperrt_nicht(family: Family) -> None:
    lucas = by_name(family, "Lucas")
    family.set_devices(SYSTEM, lucas.id, ["switch.ps5_internet"])
    chore = family.create_chore(
        SYSTEM, "Bad", [lucas.id], recurrence=Recurrence.WEEKLY,
        due=NOW - timedelta(hours=1), requires_approval=True,
    )
    family.refresh(NOW)
    family.claim(actor(family, "Lucas"), chore.id, lucas.id, NOW)
    assert not family.should_lock(lucas.id, NOW)


def test_freikarte_und_abwesenheit_verhindern_sperre(family: Family) -> None:
    lucas = by_name(family, "Lucas")
    family.set_devices(SYSTEM, lucas.id, ["switch.ps5_internet"])
    family.create_chore(
        SYSTEM, "Müll", [lucas.id], recurrence=Recurrence.DAILY, due=NOW - timedelta(hours=1)
    )
    family.refresh(NOW)
    family.grant_pass(SYSTEM, lucas.id, NOW + timedelta(hours=2))
    assert not family.should_lock(lucas.id, NOW)
    assert family.should_lock(lucas.id, NOW + timedelta(hours=3))
    family.revoke_pass(SYSTEM, lucas.id)
    family.set_absence(SYSTEM, lucas.id, NOW + timedelta(days=1))
    assert not family.should_lock(lucas.id, NOW)


def test_kind_kann_sich_nicht_freischalten(family: Family) -> None:
    lucas = by_name(family, "Lucas")
    with pytest.raises(PermissionDenied):
        family.grant_pass(actor(family, "Lucas"), lucas.id, NOW + timedelta(days=1))
    with pytest.raises(PermissionDenied):
        family.set_devices(actor(family, "Lucas"), lucas.id, [])
    with pytest.raises(FamilyError):
        family.set_devices(SYSTEM, by_name(family, "Papa").id, ["switch.x"])


# -- Wegmopsen und Fotonachweis --------------------------------------------------

DAY_START = NOW.replace(hour=0)


def test_kind_braucht_foto_eltern_nicht(family: Family) -> None:
    lucas = by_name(family, "Lucas")
    chore = family.create_chore(SYSTEM, "Bad", [lucas.id], points=3, requires_photo=True)
    with pytest.raises(FamilyError):
        family.claim(actor(family, "Lucas"), chore.id, lucas.id, NOW)
    family.claim(actor(family, "Lucas"), chore.id, lucas.id, NOW, photo="a.jpg")
    # Fotos gehen immer an die Eltern, auch ohne „Freigabe nötig“
    assert chore.state is ChoreState.CLAIMED
    assert chore.photo == "a.jpg"
    family.approve(actor(family, "Papa"), chore.id, NOW)
    assert chore.state is ChoreState.DONE and lucas.points == 3

    chore2 = family.create_chore(SYSTEM, "Flur", [lucas.id], requires_photo=True)
    family.claim(actor(family, "Papa"), chore2.id, lucas.id, NOW)
    assert chore2.state is ChoreState.DONE


def test_uebernehmen_gibt_punkte_mit_faktor_und_rotation_laeuft_weiter(family: Family) -> None:
    lucas, osmo = by_name(family, "Lucas"), by_name(family, "Osmo")
    chore = family.create_chore(
        SYSTEM, "Spülmaschine", [lucas.id, osmo.id], points=2, rotation=True,
        recurrence=Recurrence.DAILY, due=NOW + timedelta(hours=2),
    )
    assert family.responsible(chore, NOW) == [lucas.id]
    family.take_over(actor(family, "Osmo"), chore.id, osmo.id, NOW, multiplier=2, day_start=DAY_START)
    assert osmo.points == 4
    assert lucas.points == 0
    # Weiter, als hätte Lucas erledigt: jetzt ist Osmo dran.
    assert family.responsible(chore, NOW) == [osmo.id]
    assert chore.claim_multiplier == 1 and chore.claim_taken_from is None


def test_uebernehmen_mit_freigabe_merkt_faktor(family: Family) -> None:
    lucas, osmo = by_name(family, "Lucas"), by_name(family, "Osmo")
    chore = family.create_chore(SYSTEM, "Müll", [lucas.id], points=1, requires_approval=True)
    family.take_over(actor(family, "Osmo"), chore.id, osmo.id, NOW, multiplier=2, day_start=DAY_START)
    assert chore.state is ChoreState.CLAIMED
    assert chore.claim_taken_from == lucas.id
    family.approve(actor(family, "Papa"), chore.id, NOW)
    assert osmo.points == 2


def test_eigene_aufgabe_und_fuer_andere_uebernehmen_verboten(family: Family) -> None:
    lucas, osmo = by_name(family, "Lucas"), by_name(family, "Osmo")
    chore = family.create_chore(SYSTEM, "Müll", [lucas.id])
    with pytest.raises(FamilyError):
        family.take_over(actor(family, "Lucas"), chore.id, lucas.id, NOW, day_start=DAY_START)
    with pytest.raises(PermissionDenied):
        family.take_over(actor(family, "Lucas"), chore.id, osmo.id, NOW, day_start=DAY_START)


def test_hoechstens_zwei_pro_tag_auch_nach_zuruecknehmen(family: Family) -> None:
    lucas, osmo = by_name(family, "Lucas"), by_name(family, "Osmo")
    chores = [
        family.create_chore(SYSTEM, f"A{i}", [lucas.id], requires_approval=True) for i in range(3)
    ]
    osmo_actor = actor(family, "Osmo")
    family.take_over(osmo_actor, chores[0].id, osmo.id, NOW, day_start=DAY_START)
    family.undo_claim(osmo_actor, chores[0].id)
    family.take_over(osmo_actor, chores[1].id, osmo.id, NOW, day_start=DAY_START)
    with pytest.raises(FamilyError):
        family.take_over(osmo_actor, chores[2].id, osmo.id, NOW, day_start=DAY_START)
    # Am nächsten Tag geht es wieder.
    tomorrow = NOW + timedelta(days=1)
    family.take_over(osmo_actor, chores[2].id, osmo.id, tomorrow, day_start=DAY_START + timedelta(days=1))


def test_uebernehmen_mit_fotopflicht(family: Family) -> None:
    lucas, osmo = by_name(family, "Lucas"), by_name(family, "Osmo")
    chore = family.create_chore(SYSTEM, "Bad", [lucas.id], requires_photo=True)
    with pytest.raises(FamilyError):
        family.take_over(actor(family, "Osmo"), chore.id, osmo.id, NOW, day_start=DAY_START)
    family.take_over(actor(family, "Osmo"), chore.id, osmo.id, NOW, day_start=DAY_START, photo="b.jpg")
    assert chore.state is ChoreState.CLAIMED and chore.photo == "b.jpg"


# -- Alter ----------------------------------------------------------------------


def test_mindestalter_bei_rotation_und_ohne(family: Family) -> None:
    lucas, osmo = by_name(family, "Lucas"), by_name(family, "Osmo")
    family.set_age(SYSTEM, lucas.id, 12, NOW)
    family.set_age(SYSTEM, osmo.id, 6, NOW)
    assert osmo.age(NOW) == 6
    rot = family.create_chore(
        SYSTEM, "Müll", [osmo.id, lucas.id], rotation=True, min_age=8,
        recurrence=Recurrence.DAILY, due=NOW,
    )
    assert family.responsible(rot, NOW) == [lucas.id]
    both = family.create_chore(SYSTEM, "Bad", [osmo.id, lucas.id], min_age=8)
    assert family.responsible(both, NOW) == [lucas.id]
    # Osmo kann nicht melden, die Aufgabe ist nicht seine
    with pytest.raises(PermissionDenied):
        family.claim(actor(family, "Osmo"), both.id, osmo.id, NOW)
    # Zwei Jahre später rückt Osmo nach
    later = NOW.replace(year=NOW.year + 2)
    assert family.responsible(both, later) == [osmo.id, lucas.id]


def test_unbekanntes_alter_zaehlt_als_alt_genug(family: Family) -> None:
    lucas = by_name(family, "Lucas")
    chore = family.create_chore(SYSTEM, "Bad", [lucas.id], min_age=10)
    assert family.responsible(chore, NOW) == [lucas.id]


def test_zu_jung_zum_uebernehmen(family: Family) -> None:
    lucas, osmo = by_name(family, "Lucas"), by_name(family, "Osmo")
    family.set_age(SYSTEM, osmo.id, 6, NOW)
    chore = family.create_chore(SYSTEM, "Bad", [lucas.id], min_age=10)
    with pytest.raises(FamilyError):
        family.take_over(actor(family, "Osmo"), chore.id, osmo.id, NOW, day_start=NOW.replace(hour=0))


def test_alter_nur_eltern_und_gespeichert(family: Family) -> None:
    lucas = by_name(family, "Lucas")
    with pytest.raises(PermissionDenied):
        family.set_age(actor(family, "Lucas"), lucas.id, 18, NOW)
    family.set_age(SYSTEM, lucas.id, 12, NOW)
    restored = Family.from_dict(family.to_dict())
    assert restored.members[lucas.id].age(NOW) == 12


# -- Belohnungen ------------------------------------------------------------------


def test_belohnung_einloesen_bestaetigen(family: Family) -> None:
    lucas = by_name(family, "Lucas")
    lucas.points = 50
    reward = family.create_reward(SYSTEM, "Kinoabend", 40)
    redemption = family.redeem(actor(family, "Lucas"), reward.id, lucas.id, NOW)
    assert lucas.points == 10  # sofort abgezogen
    assert family.pending_redemptions() == [redemption]
    with pytest.raises(PermissionDenied):
        family.approve_redemption(actor(family, "Lucas"), redemption.id, NOW)
    family.approve_redemption(actor(family, "Papa"), redemption.id, NOW)
    assert redemption.state is RedemptionState.APPROVED
    assert lucas.points == 10
    with pytest.raises(FamilyError):
        family.reject_redemption(actor(family, "Papa"), redemption.id, NOW)


def test_ablehnen_und_zuruecknehmen_gibt_punkte_zurueck(family: Family) -> None:
    lucas, osmo = by_name(family, "Lucas"), by_name(family, "Osmo")
    lucas.points = 30
    reward = family.create_reward(SYSTEM, "Eis", 20)
    r1 = family.redeem(actor(family, "Lucas"), reward.id, lucas.id, NOW)
    family.reject_redemption(actor(family, "Papa"), r1.id, NOW)
    assert lucas.points == 30
    r2 = family.redeem(actor(family, "Lucas"), reward.id, lucas.id, NOW)
    with pytest.raises(PermissionDenied):
        family.reject_redemption(actor(family, "Osmo"), r2.id, NOW)
    family.reject_redemption(actor(family, "Lucas"), r2.id, NOW)  # selbst zurücknehmen
    assert lucas.points == 30


def test_nicht_genug_punkte_und_nur_fuer_eigene(family: Family) -> None:
    lucas, osmo = by_name(family, "Lucas"), by_name(family, "Osmo")
    lucas.points = 5
    reward = family.create_reward(SYSTEM, "Ausflug", 100)
    with pytest.raises(FamilyError):
        family.redeem(actor(family, "Lucas"), reward.id, lucas.id, NOW)
    osmo.points = 200
    with pytest.raises(PermissionDenied):
        family.redeem(actor(family, "Lucas"), reward.id, osmo.id, NOW)
    only_osmo = family.create_reward(SYSTEM, "Lego", 10, [osmo.id])
    lucas.points = 50
    with pytest.raises(FamilyError):
        family.redeem(actor(family, "Lucas"), only_osmo.id, lucas.id, NOW)
    with pytest.raises(PermissionDenied):
        family.create_reward(actor(family, "Lucas"), "Alles", 1)


def test_belohnungen_werden_gespeichert(family: Family) -> None:
    lucas, osmo = by_name(family, "Lucas"), by_name(family, "Osmo")
    lucas.points = 20
    reward = family.create_reward(SYSTEM, "Eis", 10, [lucas.id])
    family.redeem(SYSTEM, reward.id, lucas.id, NOW)
    restored = Family.from_dict(family.to_dict())
    assert restored.rewards[reward.id].members == [lucas.id]
    assert restored.pending_redemptions()[0].reward_name == "Eis"
    # Kind entfernt: die nur für Lucas gedachte Belohnung verschwindet
    family.remove_member(SYSTEM, lucas.id)
    assert reward.id not in family.rewards
