"""Zimmerlampe als Ampel: kurz orange, wenn etwas offen ist, grün, wenn alles geschafft ist.

Die Lampe leuchtet ein paar Sekunden in der Farbe und kehrt dann genau in den
Zustand von vorher zurück (aus bleibt aus, Helligkeit und Farbe wie vorher).
Nachts bleibt sie in Ruhe.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_call_later
from homeassistant.util import dt as dt_util

_LOGGER = logging.getLogger(__name__)

ORANGE = (255, 120, 0)
GREEN = (0, 220, 70)
SECONDS = 6
QUIET_FROM, QUIET_UNTIL = 21, 7  # keine Lichtzeichen zwischen 21 und 7 Uhr
_COLOR_MODES = {"hs", "rgb", "rgbw", "rgbww", "xy"}

# Lampe -> (Zustand von vorher, Abbrechen des Zurückstellens)
_PENDING: dict[str, tuple[dict[str, Any] | None, Callable[[], None]]] = {}


def _restore_data(state) -> dict[str, Any] | None:
    """Was wir brauchen, um die Lampe wieder so hinzustellen. None heißt: war aus."""
    if state.state != "on":
        return None
    attrs = state.attributes
    data: dict[str, Any] = {}
    if attrs.get("brightness") is not None:
        data["brightness"] = attrs["brightness"]
    mode = attrs.get("color_mode")
    if mode == "color_temp" and attrs.get("color_temp_kelvin"):
        data["color_temp_kelvin"] = attrs["color_temp_kelvin"]
    elif mode in _COLOR_MODES and attrs.get("hs_color"):
        data["hs_color"] = attrs["hs_color"]
    return data


async def async_flash(hass: HomeAssistant, entity_id: str, color: tuple[int, int, int]) -> None:
    if not entity_id:
        return
    hour = dt_util.now().hour
    if hour >= QUIET_FROM or hour < QUIET_UNTIL:
        return
    state = hass.states.get(entity_id)
    if state is None or state.state not in ("on", "off"):
        return
    if entity_id in _PENDING:
        # Läuft schon ein Lichtzeichen: den echten Zustand von davor behalten.
        before, cancel = _PENDING.pop(entity_id)
        cancel()
    else:
        before = _restore_data(state)
    data: dict[str, Any] = {"entity_id": entity_id, "brightness": 255}
    if _COLOR_MODES & set(state.attributes.get("supported_color_modes") or []):
        data["rgb_color"] = list(color)
    try:
        await hass.services.async_call("light", "turn_on", data, blocking=True)
    except Exception:  # noqa: BLE001 – eine kaputte Lampe darf nichts anderes stoppen
        _LOGGER.warning("Lichtzeichen an %s ging nicht", entity_id)
        return

    async def restore(_now) -> None:
        _PENDING.pop(entity_id, None)
        if before is None:
            await hass.services.async_call("light", "turn_off", {"entity_id": entity_id})
        else:
            await hass.services.async_call("light", "turn_on", {"entity_id": entity_id, **before})

    _PENDING[entity_id] = (before, async_call_later(hass, SECONDS, restore))
