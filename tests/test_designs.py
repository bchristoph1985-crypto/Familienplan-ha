"""Designs zum Aussuchen: jedes Kind wählt sein eigenes."""

from __future__ import annotations

import pytest

from custom_components.sternchenplan.core import SYSTEM, Family, FamilyError, PermissionDenied

from .test_core import actor, by_name, family  # noqa: F401


def test_kind_waehlt_eigenes_design(family: Family) -> None:  # noqa: F811
    lucas, osmo = by_name(family, "Lucas"), by_name(family, "Osmo")
    family.set_theme(actor(family, "Lucas"), lucas.id, "space")
    assert lucas.theme == "space"
    with pytest.raises(PermissionDenied):
        family.set_theme(actor(family, "Lucas"), osmo.id, "candy")
    with pytest.raises(FamilyError):
        family.set_theme(SYSTEM, osmo.id, "disco")
    family.set_theme(SYSTEM, osmo.id, "ocean")
    loaded = Family.from_dict(family.to_dict())
    assert by_name(loaded, "Osmo").theme == "ocean"
    family.set_theme(SYSTEM, lucas.id, "")
    assert lucas.theme == ""
