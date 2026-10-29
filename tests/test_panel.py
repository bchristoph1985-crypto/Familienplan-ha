"""Menüpunkt in der Seitenleiste."""

from __future__ import annotations

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.components import frontend
from homeassistant.core import HomeAssistant

from custom_components.sternchenplan.const import DOMAIN, PANEL_URL


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    yield


async def test_menuepunkt_kommt_und_geht(hass: HomeAssistant) -> None:
    # Das echte Frontend-Paket fehlt im Testpaket. Die Panel-Verwaltung
    # braucht es nicht, darum nur als geladen markieren.
    hass.config.components.add("frontend")
    entry = MockConfigEntry(domain=DOMAIN)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    panel = hass.data[frontend.DATA_PANELS][PANEL_URL]
    assert panel.sidebar_title == "Sternchenplan"
    assert panel.require_admin is False
    assert panel.config["_panel_custom"]["name"] == "sternchenplan-panel"

    await hass.config_entries.async_unload(entry.entry_id)
    assert PANEL_URL not in hass.data[frontend.DATA_PANELS]
