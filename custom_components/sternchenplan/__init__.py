"""Sternchenplan: Aufgaben für Familien, komplett lokal in Home Assistant."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from pathlib import Path

from homeassistant.components import frontend
from homeassistant.components.frontend import DATA_EXTRA_MODULE_URL, add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.storage import Store
from homeassistant.helpers.typing import ConfigType
from homeassistant.util import dt as dt_util

from .const import (
    CARD_URL,
    DATA_INITIAL_FAMILY,
    DOMAIN,
    PANEL_URL,
    SIGNAL_UPDATED,
    STORAGE_VERSION,
    VERSION,
)
from .consequences import async_apply
from .core import Family
from .photos import PhotoUploadView, PhotoView, cleanup, forget_missing
from .reminders import async_setup_reminders
from .services import async_register_services
from .websocket_api import async_register_websocket

PLATFORMS = [Platform.SENSOR]
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

type SternchenplanConfigEntry = ConfigEntry[SternchenplanData]


@dataclass
class SternchenplanData:
    hass: HomeAssistant
    entry: ConfigEntry
    store: Store
    family: Family

    async def async_save(self) -> None:
        """Sperren anpassen, speichern, Entitäten informieren. Nach jeder Änderung aufrufen."""
        await async_apply(self.hass, self.entry)
        await self._async_store()

    async def _async_store(self) -> None:
        await self.store.async_save(self.family.to_dict())
        async_dispatcher_send(self.hass, SIGNAL_UPDATED)

    async def async_tick(self, _now=None) -> None:
        changed = self.family.refresh(dt_util.utcnow())
        if await async_apply(self.hass, self.entry) or changed:
            await self._async_store()


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    async_register_services(hass)
    async_register_websocket(hass)
    await _async_register_card(hass)
    if hass.http is not None:
        hass.http.register_view(PhotoUploadView())
        hass.http.register_view(PhotoView())
    return True


async def _async_register_card(hass: HomeAssistant) -> None:
    """Die Dashboard-Karte mitliefern, ohne dass man eine Ressource anlegen muss."""
    if hass.http is None:
        return
    await hass.http.async_register_static_paths(
        [
            StaticPathConfig(
                CARD_URL,
                str(Path(__file__).parent / "frontend" / "sternchenplan-card.js"),
                cache_headers=False,
            )
        ]
    )
    if DATA_EXTRA_MODULE_URL in hass.data:
        add_extra_js_url(hass, f"{CARD_URL}?v={VERSION}")


async def async_setup_entry(hass: HomeAssistant, entry: SternchenplanConfigEntry) -> bool:
    store: Store = Store(hass, STORAGE_VERSION, f"{DOMAIN}.{entry.entry_id}")
    stored = await store.async_load()
    initial = entry.data.get(DATA_INITIAL_FAMILY)
    data = SternchenplanData(hass, entry, store, Family.from_dict(stored or initial))
    entry.runtime_data = data
    if initial is not None:
        # Ergebnis des Einrichtungsassistenten einmalig übernehmen.
        await data._async_store()
        hass.config_entries.async_update_entry(entry, data={})

    _async_register_panel(hass, entry)

    await data.async_tick()
    entry.async_on_unload(
        async_track_time_interval(hass, data.async_tick, timedelta(minutes=1))
    )

    async def photo_cleanup(_now=None) -> None:
        await hass.async_add_executor_job(cleanup, hass, entry)
        if await hass.async_add_executor_job(forget_missing, hass, entry):
            await data.async_save()

    entry.async_on_unload(
        async_track_time_interval(hass, photo_cleanup, timedelta(hours=1))
    )
    for unsub in async_setup_reminders(hass, entry):
        entry.async_on_unload(unsub)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


@callback
def _async_register_panel(hass: HomeAssistant, entry: SternchenplanConfigEntry) -> None:
    """Eigener Menüpunkt „Sternchenplan“ in der Seitenleiste. Kein Dashboard nötig."""
    if "frontend" not in hass.config.components or PANEL_URL in hass.data.get(
        frontend.DATA_PANELS, {}
    ):
        return
    frontend.async_register_built_in_panel(
        hass,
        component_name="custom",
        sidebar_title="Sternchenplan",
        sidebar_icon="mdi:account-group",
        frontend_url_path=PANEL_URL,
        config={
            "_panel_custom": {
                "name": "sternchenplan-panel",
                "module_url": f"{CARD_URL}?v={VERSION}",
                "embed_iframe": False,
                "trust_external": False,
            }
        },
        require_admin=False,
    )
    entry.async_on_unload(lambda: frontend.async_remove_panel(hass, PANEL_URL, warn_if_unknown=False))


async def async_unload_entry(hass: HomeAssistant, entry: SternchenplanConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_remove_entry(hass: HomeAssistant, entry: SternchenplanConfigEntry) -> None:
    """Beim Löschen der Integration bleiben keine Familiendaten zurück."""
    await Store(hass, STORAGE_VERSION, f"{DOMAIN}.{entry.entry_id}").async_remove()
