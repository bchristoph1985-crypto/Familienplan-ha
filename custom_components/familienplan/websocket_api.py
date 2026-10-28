"""Websocket-Schnittstelle für die Dashboard-Karte.

Die Karte abonniert `familienplan/subscribe` und bekommt bei jeder Änderung
den kompletten Stand. Ändern läuft weiter über die Dienste, damit die
Rechteprüfung an einer Stelle bleibt.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.util import dt as dt_util

from .const import DOMAIN, SIGNAL_UPDATED
from .core import Family


def snapshot(family: Family, now: datetime, user_id: str | None, is_admin: bool) -> dict[str, Any]:
    actor = family.actor_for_user(user_id, is_admin=is_admin)

    def iso(value: datetime | None) -> str | None:
        return value.isoformat() if value else None

    return {
        "me": actor.member.id if actor.member else None,
        "is_manager": actor.is_manager,
        "members": [
            {
                "id": m.id,
                "name": m.name,
                "role": m.role.value,
                "points": m.points,
                "away": m.is_away(now),
                "away_from": iso(m.away_from),
                "away_until": iso(m.away_until),
                "substitute": m.substitute_id,
            }
            for m in family.members.values()
        ],
        "chores": [
            {
                "id": c.id,
                "name": c.name,
                "state": c.state.value,
                "points": c.points,
                "recurrence": c.recurrence.value,
                "due": iso(c.due),
                "rotation": c.rotation,
                "requires_approval": c.requires_approval,
                "assignees": list(c.assignees),
                "responsible": family.responsible(c, now),
                "claimed_by": c.claimed_by,
                "last_completed_by": c.last_completed_by,
                "last_completed_at": iso(c.last_completed_at),
            }
            for c in family.chores.values()
        ],
    }


@callback
def async_register_websocket(hass: HomeAssistant) -> None:
    websocket_api.async_register_command(hass, ws_subscribe)


@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/subscribe"})
@websocket_api.async_response
async def ws_subscribe(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    entries = hass.config_entries.async_loaded_entries(DOMAIN)
    if not entries:
        connection.send_error(msg["id"], "not_loaded", "Familienplan ist nicht eingerichtet.")
        return
    entry = entries[0]
    user = connection.user

    @callback
    def send() -> None:
        connection.send_message(
            websocket_api.event_message(
                msg["id"],
                snapshot(entry.runtime_data.family, dt_util.utcnow(), user.id, user.is_admin),
            )
        )

    connection.subscriptions[msg["id"]] = async_dispatcher_connect(hass, SIGNAL_UPDATED, send)
    connection.send_result(msg["id"])
    send()
