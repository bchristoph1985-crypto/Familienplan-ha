"""Sternchenplan ist kostenlos: keine Testphase, keine Lizenz, alles bleibt an."""

from __future__ import annotations

from homeassistant.core import HomeAssistant

from .test_consequences import (  # noqa: F401
    _state,
    _tick,
    auto_enable_custom_integrations,
    setup,
)


async def test_kein_pro_menue(hass: HomeAssistant, setup) -> None:  # noqa: F811
    flow = await hass.config_entries.options.async_init(setup.entry_id)
    assert "pro" not in flow["menu_options"]
    assert "consequences" in flow["menu_options"]


async def test_sperre_auch_nach_einem_jahr(
    hass: HomeAssistant, setup, freezer  # noqa: F811
) -> None:
    # Früher endete die Testphase nach 30 Tagen. Heute sperrt es auch ein Jahr später.
    await _tick(hass, freezer, "2027-11-02 20:01:00+00:00")
    assert _state(hass, "switch.ps5") == "off"
