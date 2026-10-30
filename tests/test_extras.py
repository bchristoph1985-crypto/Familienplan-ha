"""Zusatzfunktionen: Auswahl, Haustier, Lampe, Bildschirmzeit, Bedarf, Familienrat, Urkunde, Eltern."""

from __future__ import annotations

from datetime import timedelta

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_mock_service

from homeassistant.core import Context, HomeAssistant
from homeassistant.util import dt as dt_util

from custom_components.sternchenplan.const import DOMAIN
from custom_components.sternchenplan.core import (
    DEFAULT_FEATURES,
    SYSTEM,
    ChoreState,
    Family,
    FamilyError,
    PermissionDenied,
    Recurrence,
    Role,
)

from .test_core import NOW, actor, by_name, family  # noqa: F401


def test_funktionen_waehlen_und_speichern(family: Family) -> None:  # noqa: F811
    assert family.features == set(DEFAULT_FEATURES) and not family.has("parents")
    with pytest.raises(PermissionDenied):
        family.set_features(actor(family, "Finn"), ["pet"])
    with pytest.raises(FamilyError):
        family.set_features(SYSTEM, ["disco"])
    family.set_features(SYSTEM, ["pet", "vote"])
    assert Family.from_dict(family.to_dict()).features == {"pet", "vote"}
    # Alte Stände ohne Auswahl: alles Übliche an
    old = family.to_dict()
    del old["features"]
    assert Family.from_dict(old).features == set(DEFAULT_FEATURES)


def test_neue_funktionen_bleiben_fuer_bestehende_familien_an(family: Family) -> None:  # noqa: F811
    # Gespeichert vor 0.35: es gab noch kein „levels“ und kein „helping“
    old = family.to_dict()
    old["features"] = ["pet", "vote"]
    old.pop("features_known")
    assert Family.from_dict(old).features == {"pet", "vote", "levels", "helping"}
    # Wer sie danach abwählt, behält das auch nach dem Neustart
    family.set_features(SYSTEM, ["pet"])
    assert Family.from_dict(family.to_dict()).features == {"pet"}


async def test_geschwistern_helfen_abwaehlbar(hass: HomeAssistant) -> None:
    from homeassistant.exceptions import ServiceValidationError  # noqa: PLC0415

    entry = MockConfigEntry(domain=DOMAIN)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    fam = entry.runtime_data.family
    lena = fam.add_member(SYSTEM, "Lena", Role.CHILD)
    tom = fam.add_member(SYSTEM, "Tom", Role.CHILD)
    chore = fam.create_chore(SYSTEM, "Tisch", [lena.id], due=dt_util.utcnow() - timedelta(hours=1))
    fam.set_features(SYSTEM, [f for f in DEFAULT_FEATURES if f != "helping"])
    with pytest.raises(ServiceValidationError, match="ausgeschaltet"):
        await hass.services.async_call(
            DOMAIN, "take_over_chore", {"chore_id": chore.id, "member": tom.id}, blocking=True
        )


def test_haustier_nur_fuer_sich_selbst(family: Family) -> None:  # noqa: F811
    finn, paul = by_name(family, "Finn"), by_name(family, "Paul")
    family.set_pet(actor(family, "Finn"), finn.id, "dragon", "  Feuerzahn  ")
    assert (finn.pet, finn.pet_name) == ("dragon", "Feuerzahn")
    with pytest.raises(PermissionDenied):
        family.set_pet(actor(family, "Finn"), paul.id, "cat", "Mimi")
    with pytest.raises(FamilyError):
        family.set_pet(SYSTEM, paul.id, "trex", "")
    family.set_features(SYSTEM, [])
    with pytest.raises(FamilyError):
        family.set_pet(SYSTEM, paul.id, "cat", "")


def test_alles_geschafft_meldet_sich_einmal(family: Family) -> None:  # noqa: F811
    finn = by_name(family, "Finn")
    a = family.create_chore(SYSTEM, "Tisch", [finn.id], recurrence=Recurrence.DAILY, due=NOW)
    b = family.create_chore(SYSTEM, "Müll", [finn.id], recurrence=Recurrence.DAILY, due=NOW)
    family.claim(actor(family, "Finn"), a.id, finn.id, NOW)
    assert not [e for e in family.pop_events() if e["type"] == "all_done"]
    family.claim(actor(family, "Finn"), b.id, finn.id, NOW)
    assert [e for e in family.pop_events() if e["type"] == "all_done"] == [
        {"type": "all_done", "member": finn.id}
    ]


def test_ueberfaellig_gibt_ereignis_fuer_lampe(family: Family) -> None:  # noqa: F811
    finn = by_name(family, "Finn")
    family.create_chore(SYSTEM, "Müll", [finn.id], recurrence=Recurrence.DAILY, due=NOW)
    family.refresh(NOW + timedelta(minutes=1))
    assert {"type": "overdue", "member": finn.id} in [
        {k: e[k] for k in ("type", "member")} for e in family.pop_events()
    ]


def test_bildschirmzeit(family: Family) -> None:  # noqa: F811
    finn = by_name(family, "Finn")
    finn.points = 10
    kid = actor(family, "Finn")
    with pytest.raises(FamilyError):
        family.buy_screen_time(kid, finn.id, 15, NOW)  # nicht eingeschaltet
    family.set_screen(SYSTEM, 5, 30)
    with pytest.raises(FamilyError):
        family.buy_screen_time(kid, finn.id, 15, NOW)  # keine Geräte
    family.set_screen_devices(SYSTEM, finn.id, ["switch.tv"])
    with pytest.raises(FamilyError):
        family.buy_screen_time(kid, finn.id, 12, NOW)  # nur 5er-Schritte
    family.buy_screen_time(kid, finn.id, 15, NOW)
    assert finn.points == 7 and finn.screen_until == NOW + timedelta(minutes=15)
    assert family.screen_active(finn, NOW)
    with pytest.raises(FamilyError):
        family.buy_screen_time(kid, finn.id, 20, NOW)  # Tageslimit 30
    family.buy_screen_time(kid, finn.id, 15, NOW + timedelta(minutes=5))
    assert finn.screen_until == NOW + timedelta(minutes=30)
    family.pop_events()
    family.refresh(NOW + timedelta(minutes=26))
    assert [e["type"] for e in family.pop_events()] == ["screen_ending"]
    family.refresh(NOW + timedelta(minutes=30))
    assert [e["type"] for e in family.pop_events()] == ["screen_over"]
    assert finn.screen_until is None
    # Neuer Tag, neues Kontingent
    assert family.screen_left_today(finn, NOW + timedelta(days=1)) == 30


def test_bildschirmzeit_nicht_bei_ueberfaelligem(family: Family) -> None:  # noqa: F811
    finn = by_name(family, "Finn")
    finn.points = 10
    family.set_screen(SYSTEM, 5, 60)
    family.set_screen_devices(SYSTEM, finn.id, ["switch.tv"])
    family.set_devices(SYSTEM, finn.id, ["switch.internet"])
    family.create_chore(SYSTEM, "Müll", [finn.id], recurrence=Recurrence.DAILY, due=NOW)
    family.refresh(NOW + timedelta(minutes=1))
    with pytest.raises(FamilyError):
        family.buy_screen_time(actor(family, "Finn"), finn.id, 10, NOW + timedelta(minutes=2))


def test_aufgabe_bei_bedarf(family: Family) -> None:  # noqa: F811
    finn, paul = by_name(family, "Finn"), by_name(family, "Paul")
    chore = family.create_chore(
        SYSTEM, "Wäsche aufhängen", [finn.id, paul.id], recurrence=Recurrence.ON_DEMAND, rotation=True
    )
    assert chore.state is ChoreState.DONE and chore.due is None
    assert not family.open_for(finn.id, NOW)
    assert family.trigger_chore(SYSTEM, chore.id, NOW)
    assert not family.trigger_chore(SYSTEM, chore.id, NOW)  # schon offen
    assert chore.state is ChoreState.OPEN and chore.due == NOW + timedelta(hours=2)
    demand = [e for e in family.pop_events() if e["type"] == "demand"]
    assert demand[0]["members"] == [finn.id]
    family.claim(actor(family, "Finn"), chore.id, finn.id, NOW)
    assert chore.state is ChoreState.DONE and chore.due is None
    assert family.responsible(chore, NOW) == [paul.id]  # reihum weiter
    with pytest.raises(PermissionDenied):
        family.trigger_chore(actor(family, "Paul"), chore.id, NOW)


def test_familienrat(family: Family) -> None:  # noqa: F811
    finn, paul, papa = by_name(family, "Finn"), by_name(family, "Paul"), by_name(family, "Papa")
    with pytest.raises(PermissionDenied):
        family.start_vote(actor(family, "Finn"), "Wohin?", ["Zoo", "Kino"], 24, NOW)
    with pytest.raises(FamilyError):
        family.start_vote(SYSTEM, "Wohin?", ["Zoo"], 24, NOW)
    family.start_vote(SYSTEM, "Wohin am Samstag?", ["Zoo", "Kino", "Schwimmbad"], 24, NOW)
    family.cast_vote(actor(family, "Finn"), finn.id, 1, NOW)
    family.cast_vote(actor(family, "Finn"), finn.id, 2, NOW)  # umentschieden
    with pytest.raises(PermissionDenied):
        family.cast_vote(actor(family, "Finn"), paul.id, 0, NOW)
    family.cast_vote(actor(family, "Paul"), paul.id, 2, NOW)
    assert family.vote["closed_at"] is None
    family.cast_vote(actor(family, "Papa"), papa.id, 0, NOW)  # alle haben abgestimmt
    assert family.vote["winner"] == 2
    result = [e for e in family.pop_events() if e["type"] == "vote_result"][0]
    assert result["winner"] == "Schwimmbad"
    with pytest.raises(FamilyError):
        family.cast_vote(actor(family, "Paul"), paul.id, 0, NOW)
    family.refresh(NOW + timedelta(days=4))
    assert family.vote is None


def test_familienrat_gleichstand_nach_ablauf(family: Family) -> None:  # noqa: F811
    finn, paul = by_name(family, "Finn"), by_name(family, "Paul")
    family.start_vote(SYSTEM, "Essen?", ["Pizza", "Nudeln"], 2, NOW)
    family.cast_vote(actor(family, "Finn"), finn.id, 0, NOW)
    family.cast_vote(actor(family, "Paul"), paul.id, 1, NOW)
    family.refresh(NOW + timedelta(hours=3))
    assert family.vote["closed_at"] and family.vote["winner"] is None
    result = [e for e in family.pop_events() if e["type"] == "vote_result"][0]
    assert result["tie"] == ["Pizza", "Nudeln"]


def test_monatsurkunde(family: Family) -> None:  # noqa: F811
    finn = by_name(family, "Finn")
    chore = family.create_chore(SYSTEM, "Tisch", [finn.id], recurrence=Recurrence.DAILY, due=NOW, points=2)
    family.claim(actor(family, "Finn"), chore.id, finn.id, NOW)
    family.claim(actor(family, "Finn"), chore.id, finn.id, NOW + timedelta(days=1))
    family.give_stars(SYSTEM, finn.id, 3, "lieb", NOW)
    rows = {r["name"]: r for r in family.month_report(2026, 11)}
    assert set(rows) == {"Finn", "Paul"}  # Eltern nur mit „Eltern machen mit“
    assert rows["Finn"]["done"] == 2 and rows["Finn"]["stars"] == 4 and rows["Finn"]["bonus"] == 3
    assert rows["Finn"]["favourite"] == "Tisch" and "first" in rows["Finn"]["badges"]
    assert family.month_report(2026, 10)[0]["done"] == 0
    assert family.previous_month(NOW.date()) == (2026, 10)


def test_eltern_machen_mit(family: Family) -> None:  # noqa: F811
    papa, finn = by_name(family, "Papa"), by_name(family, "Finn")
    family.set_family_goal(SYSTEM, "Zoo", 10, NOW)
    chore = family.create_chore(SYSTEM, "Rasen", [papa.id], points=4)
    family.claim(actor(family, "Papa"), chore.id, papa.id, NOW)
    assert family.goal.progress == 0  # ohne Feature zählen nur Kinder
    assert "Papa" not in {r["name"] for r in family.week_report(NOW + timedelta(hours=1))}
    family.set_features(SYSTEM, [*family.features, "parents"])
    chore2 = family.create_chore(SYSTEM, "Auto", [papa.id], points=3)
    family.claim(actor(family, "Papa"), chore2.id, papa.id, NOW)
    assert family.goal.progress == 3
    week = {r["name"]: r for r in family.week_report(NOW + timedelta(hours=1))}
    assert week["Papa"]["stars"] == 7 and "Finn" in week
    assert finn.points == 0


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    yield


async def test_bildschirmzeit_schaltet_geraete(
    hass: HomeAssistant, hass_admin_user, hass_read_only_user
) -> None:
    entry = MockConfigEntry(domain=DOMAIN)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    data = entry.runtime_data
    fam = data.family
    fam.add_member(SYSTEM, "Papa", Role.PARENT, user_id=hass_admin_user.id)
    finn = fam.add_member(SYSTEM, "Finn", Role.CHILD, user_id=hass_read_only_user.id)
    finn.points = 5
    hass.states.async_set("switch.tv", "off")
    on = async_mock_service(hass, "switch", "turn_on")
    off = async_mock_service(hass, "switch", "turn_off")
    await data.async_save()

    admin = Context(user_id=hass_admin_user.id)
    await hass.services.async_call(DOMAIN, "set_screen", {"rate": 10, "max_minutes": 60}, blocking=True, context=admin)
    await hass.services.async_call(
        DOMAIN, "set_screen_devices", {"member": "Finn", "devices": ["switch.tv"]}, blocking=True, context=admin
    )
    await hass.services.async_call(
        DOMAIN, "buy_screen_time", {"minutes": 20}, blocking=True, context=Context(user_id=hass_read_only_user.id)
    )
    assert finn.points == 3
    assert [c.data["entity_id"] for c in on] == ["switch.tv"]
    # Kind macht den Fernseher früher selbst aus: er bleibt aus
    await data.async_tick()
    assert len(on) == 1
    hass.states.async_set("switch.tv", "on")
    finn.screen_until = dt_util.utcnow() - timedelta(seconds=1)
    await data.async_tick()
    assert [c.data["entity_id"] for c in off] == ["switch.tv"]
    assert fam.screen_on == {}


async def test_lampe_blinkt_und_kehrt_zurueck(hass: HomeAssistant, freezer) -> None:
    from custom_components.sternchenplan.lamp import GREEN, async_flash

    freezer.move_to("2026-11-02 15:00:00+00:00")
    hass.states.async_set(
        "light.zimmer", "on", {"brightness": 80, "color_mode": "color_temp", "color_temp_kelvin": 2700,
                               "supported_color_modes": ["color_temp", "hs"]},
    )
    on = async_mock_service(hass, "light", "turn_on")
    await async_flash(hass, "light.zimmer", GREEN)
    assert on[-1].data["rgb_color"] == list(GREEN)
    freezer.tick(timedelta(seconds=7))
    from pytest_homeassistant_custom_component.common import async_fire_time_changed

    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert on[-1].data == {"entity_id": "light.zimmer", "brightness": 80, "color_temp_kelvin": 2700}
