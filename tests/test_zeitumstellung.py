"""Zeitumstellung: 19 Uhr bleibt 19 Uhr."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from custom_components.sternchenplan.core import SYSTEM, Family, Recurrence, Role

BERLIN = ZoneInfo("Europe/Berlin")


@pytest.mark.parametrize(
    ("start", "recurrence", "expected"),
    [
        (datetime(2026, 10, 24, 19, tzinfo=BERLIN), Recurrence.DAILY, datetime(2026, 10, 25, 19, tzinfo=BERLIN)),
        (datetime(2026, 10, 24, 19, tzinfo=BERLIN), Recurrence.WEEKLY, datetime(2026, 10, 31, 19, tzinfo=BERLIN)),
        (datetime(2027, 3, 27, 7, 30, tzinfo=BERLIN), Recurrence.DAILY, datetime(2027, 3, 28, 7, 30, tzinfo=BERLIN)),
        (datetime(2027, 3, 20, 18, tzinfo=BERLIN), Recurrence.BIWEEKLY, datetime(2027, 4, 3, 18, tzinfo=BERLIN)),
    ],
)
def test_uhrzeit_bleibt_ueber_zeitumstellung(start, recurrence, expected) -> None:
    fam = Family()
    fam.tz = BERLIN
    kid = fam.add_member(SYSTEM, "Mia", Role.CHILD)
    chore = fam.create_chore(SYSTEM, "Tisch", [kid.id], recurrence=recurrence, due=start.astimezone(UTC))
    fam.claim(SYSTEM, chore.id, kid.id, start.astimezone(UTC))
    assert chore.due == expected


def test_wochentage_und_kalender_ueber_zeitumstellung() -> None:
    fam = Family()
    fam.tz = BERLIN
    kid = fam.add_member(SYSTEM, "Mia", Role.CHILD)
    start = datetime(2026, 10, 23, 19, tzinfo=BERLIN)  # Freitag
    chore = fam.create_chore(SYSTEM, "Müll", [kid.id], recurrence=Recurrence.DAILY,
                             due=start.astimezone(UTC), weekdays=[0, 4])  # Mo + Fr
    fam.claim(SYSTEM, chore.id, kid.id, start.astimezone(UTC))
    assert chore.due == datetime(2026, 10, 26, 19, tzinfo=BERLIN)  # Montag, nach der Umstellung
    plan = fam.occurrences(start.astimezone(UTC), start.astimezone(UTC) + timedelta(days=14))
    assert len(plan) == 3 and all(d.astimezone(BERLIN).hour == 19 for d, _c, _w in plan)
