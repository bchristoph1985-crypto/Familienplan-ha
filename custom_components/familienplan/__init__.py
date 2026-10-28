"""Familienplan: Aufgaben für Familien, komplett lokal in Home Assistant."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.storage import Store
from homeassistant.helpers.typing import ConfigType
from homeassistant.util import dt as dt_util

from .const import DOMAIN, SIGNAL_UPDATED, STORAGE_VERSION
from .core import Family
from .services import async_register_services

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
    return True


async def async_setup_entry(hass: HomeAssistant, entry: FamilienplanConfigEntry) -> bool:
    store: Store = Store(hass, STORAGE_VERSION, f"{DOMAIN}.{entry.entry_id}")
    data = FamilienplanData(hass, store, Family.from_dict(await store.async_load()))
    entry.runtime_data = data

    await data.async_tick()
    entry.async_on_unload(
        async_track_time_interval(hass, data.async_tick, timedelta(minutes=1))
    )
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: FamilienplanConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_remove_entry(hass: HomeAssistant, entry: FamilienplanConfigEntry) -> None:
    """Beim Löschen der Integration bleiben keine Familiendaten zurück."""
    await Store(hass, STORAGE_VERSION, f"{DOMAIN}.{entry.entry_id}").async_remove()
