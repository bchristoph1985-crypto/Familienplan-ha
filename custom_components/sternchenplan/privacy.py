"""Sparsame Push-Nachrichten.

Pushes an Handys laufen über die Server von Google bzw. Apple. Ist „sparsam“
eingeschaltet, stehen darin keine Namen, Aufgaben oder Fotos mehr, nur ein
Hinweis, in Sternchenplan nachzusehen. Knöpfe zum Freigeben bleiben.
"""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant

from .const import DOMAIN

_TEXT = {
    "de": {"news": "Es gibt Neuigkeiten. Schau in Sternchenplan nach.",
           "approve": "Etwas wartet auf deine Freigabe."},
    "en": {"news": "There's something new. Have a look in Sternchenplan.",
           "approve": "Something is waiting for your approval."},
}


def is_private(hass: HomeAssistant) -> bool:
    entries = hass.config_entries.async_loaded_entries(DOMAIN)
    return bool(entries) and entries[0].runtime_data.family.private_push


def scrub(hass: HomeAssistant, payload: dict[str, Any]) -> dict[str, Any]:
    """Nachricht ohne persönliche Angaben, wenn sparsame Pushes an sind."""
    if not is_private(hass):
        return payload
    text = _TEXT["de" if (hass.config.language or "").startswith("de") else "en"]
    data = dict(payload.get("data") or {})
    data.pop("image", None)
    key = "approve" if data.get("actions") else "news"
    result = {**payload, "title": "Sternchenplan", "message": text[key]}
    if data:
        result["data"] = data
    else:
        result.pop("data", None)
    return result
