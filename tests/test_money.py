"""Taschengeld: Sterne tauschen, Wochengeld, Auszahlen."""

from __future__ import annotations

from datetime import timedelta

import pytest

from custom_components.sternchenplan.core import SYSTEM, Family, FamilyError, PermissionDenied

from .test_core import NOW, actor, by_name, family  # noqa: F401
from .test_progress import _done

# NOW ist Montag, 2. November 2026


def test_sterne_tauschen(family: Family) -> None:  # noqa: F811
    finn = by_name(family, "Finn")
    _done(family, "Finn", NOW, points=25)
    with pytest.raises(FamilyError):
        family.exchange(actor(family, "Finn"), finn.id, 1, NOW)  # noch ausgeschaltet
    with pytest.raises(PermissionDenied):
        family.set_money(actor(family, "Finn"), 10, 6)
    family.set_money(SYSTEM, 10, 6)
    family.exchange(actor(family, "Finn"), finn.id, 2, NOW)
    assert finn.points == 5
    assert finn.money == 200
    assert finn.progress.earned == 25  # Level bleibt
    with pytest.raises(FamilyError):
        family.exchange(actor(family, "Finn"), finn.id, 1, NOW)
    with pytest.raises(PermissionDenied):
        family.exchange(actor(family, "Paul"), finn.id, 1, NOW)
    assert family.money_history(finn.id)[0]["stars"] == 20


def test_wochengeld_einmal_pro_woche(family: Family) -> None:  # noqa: F811
    finn = by_name(family, "Finn")
    family.set_money(SYSTEM, 0, 0)  # Zahltag Montag
    family.set_allowance(SYSTEM, finn.id, 300, NOW)
    # Heute ist schon Montag: nicht rückwirkend
    assert not family.pay_allowances(NOW)
    assert finn.money == 0
    next_monday = NOW + timedelta(days=7)
    assert family.refresh(next_monday)
    assert finn.money == 300
    assert {"type": "allowance", "member": finn.id, "cents": 300} in family.pop_events()
    assert not family.pay_allowances(next_monday + timedelta(hours=3))
    assert not family.pay_allowances(next_monday + timedelta(days=3))
    family.pay_allowances(next_monday + timedelta(days=7))
    assert finn.money == 600


def test_auszahlen_und_buchen(family: Family) -> None:  # noqa: F811
    finn = by_name(family, "Finn")
    family.adjust_money(SYSTEM, finn.id, 550, "Oma", NOW)
    with pytest.raises(FamilyError):
        family.adjust_money(SYSTEM, finn.id, -600, "", NOW)
    family.payout(SYSTEM, finn.id, 200, NOW)
    assert finn.money == 350
    with pytest.raises(PermissionDenied):
        family.payout(actor(family, "Finn"), finn.id, None, NOW)
    family.payout(SYSTEM, finn.id, None, NOW)
    assert finn.money == 0
    kinds = [e["kind"] for e in family.money_history(finn.id)]
    assert kinds == ["payout", "payout", "adjust"]
    with pytest.raises(FamilyError):
        family.set_allowance(SYSTEM, by_name(family, "Papa").id, 100, NOW)

    restored = Family.from_dict(family.to_dict())
    assert len(restored.money_log) == 3
    assert by_name(restored, "Finn").money == 0
