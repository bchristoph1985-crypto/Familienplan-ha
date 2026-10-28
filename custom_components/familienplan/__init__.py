"""Familienplan: Aufgaben für Familien, komplett lokal in Home Assistant."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from pathlib import Path

from homeassistant.components.frontend import DATA_EXTRA_MODULE_URL, add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.storage import Store
from homeassistant.helpers.typing import ConfigType
from homeassistant.util import dt as dt_util

from .const import CARD_URL, DOMAIN, SIGNAL_UPDATED, STORAGE_VERSION, VERSION
from .core import Family
from .reminders import async_setup_reminders
from .services import async_register_services
from .websocket_api import async_register_websocket

PLATFORMS = [Platform.SENSOR]
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

type FamilienplanConfigEntry = ConfigEntry[FamilienplanData]


@dataclass
class FamilienplanData:
    hass: HomeAssistant
    store: Store
    family: Family

    async def async_save(self) -> None:
        """Speichern und alle Entitäten informieren. Nach jeder Änderung aufrufen."""
        await self.store.async_save(self.family.to_dict())
        async_dispatcher_send(self.hass, SIGNAL_UPDATED)

    async def async_tick(self, _now=None) -> None:
        if self.family.refresh(dt_util.utcnow()):
            await self.async_save()


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    async_register_services(hass)
    async_register_websocket(hass)
    await _async_register_card(hass)
    return True


async def _async_register_card(hass: HomeAssistant) -> None:
    """Die Dashboard-Karte mitliefern, ohne dass man eine Ressource anlegen muss."""
    if hass.http is None:
        return
    await hass.http.async_register_static_paths(
        [
            StaticPathConfig(
                CARD_URL,
                str(Path(__file__).parent / "frontend" / "familienplan-card.js"),
                cache_headers=False,
            )
        ]
    )
    if DATA_EXTRA_MODULE_URL in hass.data:
        add_extra_js_url(hass, f"{CARD_URL}?v={VERSION}")


async def async_setup_entry(hass: HomeAssistant, entry: FamilienplanConfigEntry) -> bool:
    store: Store = Store(hass, STORAGE_VERSION, f"{DOMAIN}.{entry.entry_id}")
    data = FamilienplanData(hass, store, Family.from_dict(await store.async_load()))
    entry.runtime_data = data

    await data.async_tick()
    entry.async_on_unload(
        async_track_time_interval(hass, data.async_tick, timedelta(minutes=1))
    )
    for unsub in async_setup_reminders(hass, entry):
        entry.async_on_unload(unsub)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: FamilienplanConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_remove_entry(hass: HomeAssistant, entry: FamilienplanConfigEntry) -> None:
    """Beim Löschen der Integration bleiben keine Familiendaten zurück."""
    await Store(hass, STORAGE_VERSION, f"{DOMAIN}.{entry.entry_id}").async_remove()
