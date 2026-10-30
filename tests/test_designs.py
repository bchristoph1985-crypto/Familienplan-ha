"""Designs zum Aussuchen: jedes Kind wählt sein eigenes."""

from __future__ import annotations

import pytest

from custom_components.sternchenplan.core import SYSTEM, Family, FamilyError, PermissionDenied

from .test_core import actor, by_name, family  # noqa: F401


def test_kind_waehlt_eigenes_design(family: Family) -> None:  # noqa: F811
    finn, paul = by_name(family, "Finn"), by_name(family, "Paul")
    family.set_theme(actor(family, "Finn"), finn.id, "space")
    assert finn.theme == "space"
    with pytest.raises(PermissionDenied):
        family.set_theme(actor(family, "Finn"), paul.id, "candy")
    with pytest.raises(FamilyError):
        family.set_theme(SYSTEM, paul.id, "disco")
    family.set_theme(SYSTEM, paul.id, "ocean")
    loaded = Family.from_dict(family.to_dict())
    assert by_name(loaded, "Paul").theme == "ocean"
    family.set_theme(SYSTEM, finn.id, "")
    assert finn.theme == ""
