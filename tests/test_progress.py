"""Level, Serien und Abzeichen. Laufen ohne Home Assistant."""

from __future__ import annotations

from datetime import date, timedelta, timezone
from zoneinfo import ZoneInfo

from custom_components.sternchenplan.core import SYSTEM, Family, Recurrence, level_floor, level_for

from .test_core import NOW, actor, by_name, family  # noqa: F401


def _done(fam: Family, name: str, when, points: int = 1) -> None:
    kid = by_name(fam, name)
    chore = fam.create_chore(SYSTEM, f"Aufgabe {when}", [kid.id], points=points)
    fam.claim(actor(fam, name), chore.id, kid.id, when)


def test_level_stufen() -> None:
    assert [level_floor(n) for n in range(1, 6)] == [0, 5, 15, 30, 50]
    assert level_for(0) == 1
    assert level_for(4) == 1
    assert level_for(5) == 2
    assert level_for(49) == 4
    assert level_for(50) == 5


def test_level_bleibt_beim_einloesen(family: Family) -> None:  # noqa: F811
    lucas = by_name(family, "Lucas")
    _done(family, "Lucas", NOW, points=6)
    assert lucas.progress.level == 2
    reward = family.create_reward(SYSTEM, "Eis", 6, [lucas.id])
    family.redeem(actor(family, "Lucas"), reward.id, lucas.id, NOW)
    assert lucas.points == 0
    assert lucas.progress.earned == 6
    assert lucas.progress.level == 2


def test_level_up_und_abzeichen_als_ereignis(family: Family) -> None:  # noqa: F811
    lucas = by_name(family, "Lucas")
    _done(family, "Lucas", NOW, points=5)
    events = family.pop_events()
    assert {"type": "level", "member": lucas.id, "level": 2} in events
    assert any(e["type"] == "badge" and e["badge"] == "first" for e in events)
    assert family.pop_events() == []
    # Das erste Abzeichen gibt es nur einmal
    _done(family, "Lucas", NOW)
    assert not any(e.get("badge") == "first" for e in family.pop_events())


def test_serie_zaehlt_tage_und_reisst(family: Family) -> None:  # noqa: F811
    lucas = by_name(family, "Lucas")
    for day in range(3):
        _done(family, "Lucas", NOW + timedelta(days=day))
        _done(family, "Lucas", NOW + timedelta(days=day, hours=1))  # zweimal am Tag zählt einmal
    assert lucas.progress.streak == 3
    assert "streak3" in lucas.progress.badges
    third = (NOW + timedelta(days=2)).date()
    assert lucas.progress.current_streak(third) == 3
    assert lucas.progress.current_streak(third + timedelta(days=1)) == 3  # heute noch nichts
    assert lucas.progress.current_streak(third + timedelta(days=2)) == 0  # gestern verpasst
    _done(family, "Lucas", NOW + timedelta(days=4))
    assert lucas.progress.streak == 1
    assert lucas.progress.best_streak == 3


def test_serie_nach_ortszeit(family: Family) -> None:  # noqa: F811
    family.tz = ZoneInfo("Europe/Berlin")
    lucas = by_name(family, "Lucas")
    # 23:30 UTC ist in Berlin schon der nächste Tag
    late = NOW.replace(hour=23, minute=30)
    _done(family, "Lucas", late)
    assert lucas.progress.streak_day == date(2026, 11, 3)


def test_fruehaufsteher_helfer_und_fotos(family: Family) -> None:  # noqa: F811
    lucas, osmo = by_name(family, "Lucas"), by_name(family, "Osmo")
    morning = NOW.replace(hour=6, tzinfo=timezone.utc)
    for i in range(5):
        _done(family, "Lucas", morning + timedelta(minutes=i))
    assert lucas.progress.early == 5
    assert "early5" in lucas.progress.badges

    chore = family.create_chore(SYSTEM, "Müll", [osmo.id], due=NOW - timedelta(hours=1))
    family.take_over(
        actor(family, "Lucas"), chore.id, lucas.id, NOW, day_start=NOW.replace(hour=0)
    )
    assert lucas.progress.taken_over == 1
    assert "helper1" in lucas.progress.badges

    photo = family.create_chore(SYSTEM, "Zimmer", [lucas.id], requires_photo=True)
    family.claim(actor(family, "Lucas"), photo.id, lucas.id, NOW, photo="a.jpg")
    family.approve(SYSTEM, photo.id, NOW)
    assert lucas.progress.photos == 1


def test_alter_stand_wird_geschaetzt(family: Family) -> None:  # noqa: F811
    lucas = by_name(family, "Lucas")
    chore = family.create_chore(
        SYSTEM, "Tisch", [lucas.id], recurrence=Recurrence.DAILY, due=NOW + timedelta(hours=1)
    )
    for day in range(12):
        family.claim(actor(family, "Lucas"), chore.id, lucas.id, NOW + timedelta(days=day))
    reward = family.create_reward(SYSTEM, "Kino", 5, [lucas.id])
    family.redeem(actor(family, "Lucas"), reward.id, lucas.id, NOW)
    data = family.to_dict()
    for member in data["members"]:
        del member["progress"]  # so sah es vor 0.16 aus
    restored = Family.from_dict(data)
    progress = by_name(restored, "Lucas").progress
    assert progress.earned == 12  # 7 übrig + 5 ausgegeben
    assert progress.done == 12
    assert progress.redeemed == 1
    assert {"first", "done10", "reward1"} <= set(progress.badges)
    assert restored.pop_events() == []


def test_fortschritt_wird_gespeichert(family: Family) -> None:  # noqa: F811
    _done(family, "Lucas", NOW, points=7)
    restored = Family.from_dict(family.to_dict())
    progress = by_name(restored, "Lucas").progress
    assert progress.earned == 7
    assert progress.streak == 1
    assert progress.streak_day == NOW.date()
    assert "first" in progress.badges
