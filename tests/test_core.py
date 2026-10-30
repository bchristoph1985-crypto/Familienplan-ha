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
    fam.add_member(SYSTEM, "Finn", Role.CHILD, user_id="u_lucas")
    fam.add_member(SYSTEM, "Paul", Role.CHILD, user_id="u_osmo")
    return fam


def by_name(fam: Family, name: str):
    return next(m for m in fam.members.values() if m.name == name)


def actor(fam: Family, name: str) -> Actor:
    return fam.actor_for_user(by_name(fam, name).user_id, is_admin=False)


def test_kind_darf_keine_aufgabe_anlegen(family: Family) -> None:
    finn = by_name(family, "Finn")
    with pytest.raises(PermissionDenied):
        family.create_chore(actor(family, "Finn"), "Müll", [finn.id])


def test_unbekanntes_konto_ohne_admin_ist_kein_elternteil(family: Family) -> None:
    fremd = family.actor_for_user("u_fremd", is_admin=False)
    assert not fremd.is_manager
    assert family.actor_for_user("u_fremd", is_admin=True).is_manager


def test_einfache_aufgabe_erledigen_gibt_punkte(family: Family) -> None:
    finn = by_name(family, "Finn")
    chore = family.create_chore(SYSTEM, "Tisch decken", [finn.id], points=2)
    family.claim(actor(family, "Finn"), chore.id, finn.id, NOW)
    assert chore.state is ChoreState.DONE
    assert finn.points == 2


def test_kind_kann_nicht_fuer_geschwister_melden(family: Family) -> None:
    finn, paul = by_name(family, "Finn"), by_name(family, "Paul")
    chore = family.create_chore(SYSTEM, "Müll", [paul.id])
    with pytest.raises(PermissionDenied):
        family.claim(actor(family, "Finn"), chore.id, paul.id, NOW)
    with pytest.raises(PermissionDenied):
        family.claim(actor(family, "Finn"), chore.id, finn.id, NOW)
    assert chore.state is ChoreState.OPEN


def test_freigabe_ablauf(family: Family) -> None:
    finn = by_name(family, "Finn")
    chore = family.create_chore(
        SYSTEM, "Bad putzen", [finn.id], points=5, requires_approval=True
    )
    family.claim(actor(family, "Finn"), chore.id, finn.id, NOW)
    assert chore.state is ChoreState.CLAIMED
    assert finn.points == 0

    with pytest.raises(PermissionDenied):
        family.approve(actor(family, "Finn"), chore.id, NOW)

    family.approve(actor(family, "Papa"), chore.id, NOW)
    assert chore.state is ChoreState.DONE
    assert finn.points == 5


def test_ablehnen_und_eigene_meldung_zuruecknehmen(family: Family) -> None:
    finn, paul = by_name(family, "Finn"), by_name(family, "Paul")
    chore = family.create_chore(
        SYSTEM, "Zimmer", [finn.id, paul.id], requires_approval=True
    )
    family.claim(actor(family, "Finn"), chore.id, finn.id, NOW)
    with pytest.raises(PermissionDenied):
        family.undo_claim(actor(family, "Paul"), chore.id)
    family.undo_claim(actor(family, "Finn"), chore.id)
    assert chore.state is ChoreState.OPEN

    family.claim(actor(family, "Finn"), chore.id, finn.id, NOW)
    family.reject(actor(family, "Papa"), chore.id, NOW)
    assert chore.state is ChoreState.OPEN
    assert finn.points == 0


def test_rotation_wechselt_nach_erledigung(family: Family) -> None:
    finn, paul = by_name(family, "Finn"), by_name(family, "Paul")
    chore = family.create_chore(
        SYSTEM,
        "Spülmaschine",
        [finn.id, paul.id],
        recurrence=Recurrence.DAILY,
        due=NOW,
        rotation=True,
    )
    assert family.responsible(chore, NOW) == [finn.id]
    family.claim(actor(family, "Finn"), chore.id, finn.id, NOW)
    assert family.responsible(chore, NOW) == [paul.id]
    assert chore.state is ChoreState.OPEN
    assert chore.due == NOW + timedelta(days=1)


def test_verspaetete_erledigung_haelt_den_takt(family: Family) -> None:
    finn = by_name(family, "Finn")
    first_due = NOW - timedelta(days=3)
    chore = family.create_chore(
        SYSTEM, "Pflanzen", [finn.id], recurrence=Recurrence.WEEKLY, due=first_due
    )
    family.refresh(NOW)
    assert chore.state is ChoreState.OVERDUE
    family.claim(actor(family, "Finn"), chore.id, finn.id, NOW)
    assert chore.due == first_due + timedelta(weeks=1)
    assert chore.due > NOW


def test_doppelt_melden_wird_abgelehnt(family: Family) -> None:
    finn = by_name(family, "Finn")
    chore = family.create_chore(SYSTEM, "Einmalig", [finn.id])
    family.claim(actor(family, "Finn"), chore.id, finn.id, NOW)
    with pytest.raises(FamilyError):
        family.claim(actor(family, "Finn"), chore.id, finn.id, NOW)
    assert finn.points == 1


def test_mitglied_entfernen_raeumt_aufgaben_auf(family: Family) -> None:
    finn, paul = by_name(family, "Finn"), by_name(family, "Paul")
    chore = family.create_chore(
        SYSTEM,
        "Tonnen",
        [finn.id, paul.id],
        recurrence=Recurrence.WEEKLY,
        due=NOW,
        rotation=True,
    )
    chore.rotation_index = 1
    family.remove_member(SYSTEM, paul.id)
    assert chore.assignees == [finn.id]
    assert family.responsible(chore, NOW) == [finn.id]


def test_speichern_und_laden(family: Family) -> None:
    finn = by_name(family, "Finn")
    chore = family.create_chore(
        SYSTEM, "Müll", [finn.id], recurrence=Recurrence.DAILY, due=NOW, points=2
    )
    family.claim(SYSTEM, chore.id, finn.id, NOW)
    loaded = Family.from_dict(family.to_dict())
    assert loaded.to_dict() == family.to_dict()
    assert loaded.chores[chore.id].due == NOW + timedelta(days=1)


def test_ein_ha_konto_nur_einmal(family: Family) -> None:
    with pytest.raises(FamilyError):
        family.add_member(SYSTEM, "Doppelt", Role.CHILD, user_id="u_lucas")


# -- Abwesenheit und Vertretung ---------------------------------------------


def test_rotation_ueberspringt_abwesende(family: Family) -> None:
    finn, paul = by_name(family, "Finn"), by_name(family, "Paul")
    chore = family.create_chore(
        SYSTEM, "Spülmaschine", [finn.id, paul.id],
        recurrence=Recurrence.DAILY, due=NOW, rotation=True,
    )
    family.set_absence(SYSTEM, finn.id, NOW + timedelta(days=3))
    assert family.responsible(chore, NOW) == [paul.id]
    family.claim(actor(family, "Paul"), chore.id, paul.id, NOW)
    # nach Paul wäre wieder Finn dran, der ist aber noch weg
    assert family.responsible(chore, NOW) == [paul.id]
    # nach der Rückkehr ist Finn wieder dran
    assert family.responsible(chore, NOW + timedelta(days=4)) == [finn.id]


def test_vertretung_ohne_rotation(family: Family) -> None:
    finn, paul = by_name(family, "Finn"), by_name(family, "Paul")
    chore = family.create_chore(SYSTEM, "Hamster füttern", [finn.id])
    family.set_absence(SYSTEM, finn.id, NOW + timedelta(days=2), substitute_id=paul.id)
    assert family.responsible(chore, NOW) == [paul.id]
    # Paul darf jetzt melden, Finn nicht
    family.claim(actor(family, "Paul"), chore.id, paul.id, NOW)
    assert paul.points == 1


def test_niemand_da_aufgabe_ruht(family: Family) -> None:
    finn = by_name(family, "Finn")
    chore = family.create_chore(
        SYSTEM, "Zimmer", [finn.id], recurrence=Recurrence.DAILY,
        due=NOW - timedelta(hours=1),
    )
    family.set_absence(SYSTEM, finn.id, NOW + timedelta(days=1))
    family.refresh(NOW)
    assert chore.state is ChoreState.OPEN
    assert family.responsible(chore, NOW) == []


def test_abwesenheit_endet_automatisch(family: Family) -> None:
    finn = by_name(family, "Finn")
    family.set_absence(
        SYSTEM, finn.id, NOW + timedelta(days=1), start=NOW - timedelta(days=1)
    )
    assert finn.is_away(NOW)
    assert family.refresh(NOW + timedelta(days=2))
    assert finn.away_until is None


def test_geplante_abwesenheit_beginnt_spaeter(family: Family) -> None:
    finn = by_name(family, "Finn")
    family.set_absence(
        SYSTEM, finn.id, NOW + timedelta(days=5), start=NOW + timedelta(days=2)
    )
    assert not finn.is_away(NOW)
    assert finn.is_away(NOW + timedelta(days=3))


def test_kind_darf_keine_abwesenheit_setzen(family: Family) -> None:
    finn = by_name(family, "Finn")
    with pytest.raises(PermissionDenied):
        family.set_absence(actor(family, "Finn"), finn.id, NOW + timedelta(days=1))
    with pytest.raises(FamilyError):
        family.set_absence(SYSTEM, finn.id, NOW + timedelta(days=1), substitute_id=finn.id)


def test_offen_bis_fuer_erinnerungen(family: Family) -> None:
    finn = by_name(family, "Finn")
    heute = family.create_chore(SYSTEM, "Heute", [finn.id], recurrence=Recurrence.DAILY, due=NOW)
    family.create_chore(
        SYSTEM, "Morgen", [finn.id], recurrence=Recurrence.DAILY, due=NOW + timedelta(days=1)
    )
    ohne = family.create_chore(SYSTEM, "Ohne Frist", [finn.id])
    ids = {c.id for c in family.open_until(finn.id, NOW, NOW + timedelta(hours=6))}
    assert ids == {heute.id, ohne.id}


# -- Bearbeiten -------------------------------------------------------------


def test_bearbeiten_aendert_nur_angegebenes(family: Family) -> None:
    finn, paul = by_name(family, "Finn"), by_name(family, "Paul")
    chore = family.create_chore(
        SYSTEM, "Müll", [finn.id], points=1, recurrence=Recurrence.DAILY, due=NOW
    )
    family.update_chore(SYSTEM, chore.id, NOW, name="Müll + Gelber Sack", points=3)
    assert chore.name == "Müll + Gelber Sack"
    assert chore.points == 3
    assert chore.assignees == [finn.id]
    assert chore.due == NOW
    family.update_chore(SYSTEM, chore.id, NOW, assignees=[paul.id, finn.id], rotation=True)
    assert family.responsible(chore, NOW) == [paul.id]


def test_kind_darf_nicht_bearbeiten(family: Family) -> None:
    finn = by_name(family, "Finn")
    chore = family.create_chore(SYSTEM, "Müll", [finn.id], points=1)
    with pytest.raises(PermissionDenied):
        family.update_chore(actor(family, "Finn"), chore.id, NOW, points=50)
    assert chore.points == 1


def test_bearbeiten_regeln(family: Family) -> None:
    finn = by_name(family, "Finn")
    chore = family.create_chore(SYSTEM, "Müll", [finn.id], recurrence=Recurrence.DAILY, due=NOW)
    with pytest.raises(FamilyError):
        family.update_chore(SYSTEM, chore.id, NOW, clear_due=True)
    with pytest.raises(FamilyError):
        family.update_chore(SYSTEM, chore.id, NOW, assignees=[])
    with pytest.raises(FamilyError):
        family.update_chore(SYSTEM, chore.id, NOW, name="  ")
    assert chore.name == "Müll" and chore.due == NOW


def test_neue_frist_hebt_ueberfaellig_auf(family: Family) -> None:
    finn = by_name(family, "Finn")
    chore = family.create_chore(
        SYSTEM, "Zimmer", [finn.id], recurrence=Recurrence.WEEKLY, due=NOW - timedelta(hours=2)
    )
    family.refresh(NOW)
    assert chore.state is ChoreState.OVERDUE
    family.update_chore(SYSTEM, chore.id, NOW, due=NOW + timedelta(days=1))
    assert chore.state is ChoreState.OPEN


def test_freigabe_abschalten_bucht_offene_meldung(family: Family) -> None:
    finn = by_name(family, "Finn")
    chore = family.create_chore(SYSTEM, "Bad", [finn.id], points=5, requires_approval=True)
    family.claim(actor(family, "Finn"), chore.id, finn.id, NOW)
    family.update_chore(SYSTEM, chore.id, NOW, requires_approval=False)
    assert chore.state is ChoreState.DONE
    assert finn.points == 5


# -- Konsequenzen -----------------------------------------------------------


def test_sperre_nur_bei_ueberfaelligem(family: Family) -> None:
    finn = by_name(family, "Finn")
    family.set_devices(SYSTEM, finn.id, ["switch.ps5_internet"])
    chore = family.create_chore(
        SYSTEM, "Müll", [finn.id], recurrence=Recurrence.DAILY, due=NOW - timedelta(hours=1)
    )
    assert not family.should_lock(finn.id, NOW)  # noch nicht als überfällig erkannt
    family.refresh(NOW)
    assert family.should_lock(finn.id, NOW)
    family.claim(actor(family, "Finn"), chore.id, finn.id, NOW)
    assert not family.should_lock(finn.id, NOW)


def test_gemeldet_wartet_auf_freigabe_sperrt_nicht(family: Family) -> None:
    finn = by_name(family, "Finn")
    family.set_devices(SYSTEM, finn.id, ["switch.ps5_internet"])
    chore = family.create_chore(
        SYSTEM, "Bad", [finn.id], recurrence=Recurrence.WEEKLY,
        due=NOW - timedelta(hours=1), requires_approval=True,
    )
    family.refresh(NOW)
    family.claim(actor(family, "Finn"), chore.id, finn.id, NOW)
    assert not family.should_lock(finn.id, NOW)


def test_freikarte_und_abwesenheit_verhindern_sperre(family: Family) -> None:
    finn = by_name(family, "Finn")
    family.set_devices(SYSTEM, finn.id, ["switch.ps5_internet"])
    family.create_chore(
        SYSTEM, "Müll", [finn.id], recurrence=Recurrence.DAILY, due=NOW - timedelta(hours=1)
    )
    family.refresh(NOW)
    family.grant_pass(SYSTEM, finn.id, NOW + timedelta(hours=2))
    assert not family.should_lock(finn.id, NOW)
    assert family.should_lock(finn.id, NOW + timedelta(hours=3))
    family.revoke_pass(SYSTEM, finn.id)
    family.set_absence(SYSTEM, finn.id, NOW + timedelta(days=1))
    assert not family.should_lock(finn.id, NOW)


def test_kind_kann_sich_nicht_freischalten(family: Family) -> None:
    finn = by_name(family, "Finn")
    with pytest.raises(PermissionDenied):
        family.grant_pass(actor(family, "Finn"), finn.id, NOW + timedelta(days=1))
    with pytest.raises(PermissionDenied):
        family.set_devices(actor(family, "Finn"), finn.id, [])
    with pytest.raises(FamilyError):
        family.set_devices(SYSTEM, by_name(family, "Papa").id, ["switch.x"])


# -- Wegmopsen und Fotonachweis --------------------------------------------------

DAY_START = NOW.replace(hour=0)


def test_kind_braucht_foto_eltern_nicht(family: Family) -> None:
    finn = by_name(family, "Finn")
    chore = family.create_chore(SYSTEM, "Bad", [finn.id], points=3, requires_photo=True)
    with pytest.raises(FamilyError):
        family.claim(actor(family, "Finn"), chore.id, finn.id, NOW)
    family.claim(actor(family, "Finn"), chore.id, finn.id, NOW, photo="a.jpg")
    # Fotos gehen immer an die Eltern, auch ohne „Freigabe nötig“
    assert chore.state is ChoreState.CLAIMED
    assert chore.photo == "a.jpg"
    family.approve(actor(family, "Papa"), chore.id, NOW)
    assert chore.state is ChoreState.DONE and finn.points == 3

    chore2 = family.create_chore(SYSTEM, "Flur", [finn.id], requires_photo=True)
    family.claim(actor(family, "Papa"), chore2.id, finn.id, NOW)
    assert chore2.state is ChoreState.DONE


def test_uebernehmen_gibt_punkte_mit_faktor_und_rotation_laeuft_weiter(family: Family) -> None:
    finn, paul = by_name(family, "Finn"), by_name(family, "Paul")
    chore = family.create_chore(
        SYSTEM, "Spülmaschine", [finn.id, paul.id], points=2, rotation=True,
        recurrence=Recurrence.DAILY, due=NOW + timedelta(hours=2),
    )
    assert family.responsible(chore, NOW) == [finn.id]
    family.take_over(actor(family, "Paul"), chore.id, paul.id, NOW, multiplier=2, day_start=DAY_START)
    assert paul.points == 4
    assert finn.points == 0
    # Weiter, als hätte Finn erledigt: jetzt ist Paul dran.
    assert family.responsible(chore, NOW) == [paul.id]
    assert chore.claim_multiplier == 1 and chore.claim_taken_from is None


def test_uebernehmen_mit_freigabe_merkt_faktor(family: Family) -> None:
    finn, paul = by_name(family, "Finn"), by_name(family, "Paul")
    chore = family.create_chore(SYSTEM, "Müll", [finn.id], points=1, requires_approval=True)
    family.take_over(actor(family, "Paul"), chore.id, paul.id, NOW, multiplier=2, day_start=DAY_START)
    assert chore.state is ChoreState.CLAIMED
    assert chore.claim_taken_from == finn.id
    family.approve(actor(family, "Papa"), chore.id, NOW)
    assert paul.points == 2


def test_eigene_aufgabe_und_fuer_andere_uebernehmen_verboten(family: Family) -> None:
    finn, paul = by_name(family, "Finn"), by_name(family, "Paul")
    chore = family.create_chore(SYSTEM, "Müll", [finn.id])
    with pytest.raises(FamilyError):
        family.take_over(actor(family, "Finn"), chore.id, finn.id, NOW, day_start=DAY_START)
    with pytest.raises(PermissionDenied):
        family.take_over(actor(family, "Finn"), chore.id, paul.id, NOW, day_start=DAY_START)


def test_hoechstens_zwei_pro_tag_auch_nach_zuruecknehmen(family: Family) -> None:
    finn, paul = by_name(family, "Finn"), by_name(family, "Paul")
    chores = [
        family.create_chore(SYSTEM, f"A{i}", [finn.id], requires_approval=True) for i in range(3)
    ]
    osmo_actor = actor(family, "Paul")
    family.take_over(osmo_actor, chores[0].id, paul.id, NOW, day_start=DAY_START)
    family.undo_claim(osmo_actor, chores[0].id)
    family.take_over(osmo_actor, chores[1].id, paul.id, NOW, day_start=DAY_START)
    with pytest.raises(FamilyError):
        family.take_over(osmo_actor, chores[2].id, paul.id, NOW, day_start=DAY_START)
    # Am nächsten Tag geht es wieder.
    tomorrow = NOW + timedelta(days=1)
    family.take_over(osmo_actor, chores[2].id, paul.id, tomorrow, day_start=DAY_START + timedelta(days=1))


def test_uebernehmen_mit_fotopflicht(family: Family) -> None:
    finn, paul = by_name(family, "Finn"), by_name(family, "Paul")
    chore = family.create_chore(SYSTEM, "Bad", [finn.id], requires_photo=True)
    with pytest.raises(FamilyError):
        family.take_over(actor(family, "Paul"), chore.id, paul.id, NOW, day_start=DAY_START)
    family.take_over(actor(family, "Paul"), chore.id, paul.id, NOW, day_start=DAY_START, photo="b.jpg")
    assert chore.state is ChoreState.CLAIMED and chore.photo == "b.jpg"


# -- Alter ----------------------------------------------------------------------


def test_mindestalter_bei_rotation_und_ohne(family: Family) -> None:
    finn, paul = by_name(family, "Finn"), by_name(family, "Paul")
    family.set_age(SYSTEM, finn.id, 12, NOW)
    family.set_age(SYSTEM, paul.id, 6, NOW)
    assert paul.age(NOW) == 6
    rot = family.create_chore(
        SYSTEM, "Müll", [paul.id, finn.id], rotation=True, min_age=8,
        recurrence=Recurrence.DAILY, due=NOW,
    )
    assert family.responsible(rot, NOW) == [finn.id]
    both = family.create_chore(SYSTEM, "Bad", [paul.id, finn.id], min_age=8)
    assert family.responsible(both, NOW) == [finn.id]
    # Paul kann nicht melden, die Aufgabe ist nicht seine
    with pytest.raises(PermissionDenied):
        family.claim(actor(family, "Paul"), both.id, paul.id, NOW)
    # Zwei Jahre später rückt Paul nach
    later = NOW.replace(year=NOW.year + 2)
    assert family.responsible(both, later) == [paul.id, finn.id]


def test_unbekanntes_alter_zaehlt_als_alt_genug(family: Family) -> None:
    finn = by_name(family, "Finn")
    chore = family.create_chore(SYSTEM, "Bad", [finn.id], min_age=10)
    assert family.responsible(chore, NOW) == [finn.id]


def test_zu_jung_zum_uebernehmen(family: Family) -> None:
    finn, paul = by_name(family, "Finn"), by_name(family, "Paul")
    family.set_age(SYSTEM, paul.id, 6, NOW)
    chore = family.create_chore(SYSTEM, "Bad", [finn.id], min_age=10)
    with pytest.raises(FamilyError):
        family.take_over(actor(family, "Paul"), chore.id, paul.id, NOW, day_start=NOW.replace(hour=0))


def test_alter_nur_eltern_und_gespeichert(family: Family) -> None:
    finn = by_name(family, "Finn")
    with pytest.raises(PermissionDenied):
        family.set_age(actor(family, "Finn"), finn.id, 18, NOW)
    family.set_age(SYSTEM, finn.id, 12, NOW)
    restored = Family.from_dict(family.to_dict())
    assert restored.members[finn.id].age(NOW) == 12


# -- Belohnungen ------------------------------------------------------------------


def test_belohnung_einloesen_bestaetigen(family: Family) -> None:
    finn = by_name(family, "Finn")
    finn.points = 50
    reward = family.create_reward(SYSTEM, "Kinoabend", 40)
    redemption = family.redeem(actor(family, "Finn"), reward.id, finn.id, NOW)
    assert finn.points == 10  # sofort abgezogen
    assert family.pending_redemptions() == [redemption]
    with pytest.raises(PermissionDenied):
        family.approve_redemption(actor(family, "Finn"), redemption.id, NOW)
    family.approve_redemption(actor(family, "Papa"), redemption.id, NOW)
    assert redemption.state is RedemptionState.APPROVED
    assert finn.points == 10
    with pytest.raises(FamilyError):
        family.reject_redemption(actor(family, "Papa"), redemption.id, NOW)


def test_ablehnen_und_zuruecknehmen_gibt_punkte_zurueck(family: Family) -> None:
    finn, paul = by_name(family, "Finn"), by_name(family, "Paul")
    finn.points = 30
    reward = family.create_reward(SYSTEM, "Eis", 20)
    r1 = family.redeem(actor(family, "Finn"), reward.id, finn.id, NOW)
    family.reject_redemption(actor(family, "Papa"), r1.id, NOW)
    assert finn.points == 30
    r2 = family.redeem(actor(family, "Finn"), reward.id, finn.id, NOW)
    with pytest.raises(PermissionDenied):
        family.reject_redemption(actor(family, "Paul"), r2.id, NOW)
    family.reject_redemption(actor(family, "Finn"), r2.id, NOW)  # selbst zurücknehmen
    assert finn.points == 30


def test_nicht_genug_punkte_und_nur_fuer_eigene(family: Family) -> None:
    finn, paul = by_name(family, "Finn"), by_name(family, "Paul")
    finn.points = 5
    reward = family.create_reward(SYSTEM, "Ausflug", 100)
    with pytest.raises(FamilyError):
        family.redeem(actor(family, "Finn"), reward.id, finn.id, NOW)
    paul.points = 200
    with pytest.raises(PermissionDenied):
        family.redeem(actor(family, "Finn"), reward.id, paul.id, NOW)
    only_osmo = family.create_reward(SYSTEM, "Lego", 10, [paul.id])
    finn.points = 50
    with pytest.raises(FamilyError):
        family.redeem(actor(family, "Finn"), only_osmo.id, finn.id, NOW)
    with pytest.raises(PermissionDenied):
        family.create_reward(actor(family, "Finn"), "Alles", 1)


def test_belohnungen_werden_gespeichert(family: Family) -> None:
    finn, paul = by_name(family, "Finn"), by_name(family, "Paul")
    finn.points = 20
    reward = family.create_reward(SYSTEM, "Eis", 10, [finn.id])
    family.redeem(SYSTEM, reward.id, finn.id, NOW)
    restored = Family.from_dict(family.to_dict())
    assert restored.rewards[reward.id].members == [finn.id]
    assert restored.pending_redemptions()[0].reward_name == "Eis"
    # Kind entfernt: die nur für Finn gedachte Belohnung verschwindet
    family.remove_member(SYSTEM, finn.id)
    assert reward.id not in family.rewards
