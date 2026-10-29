"""Websocket-Schnittstelle für die Dashboard-Karte.

Die Karte abonniert `sternchenplan/subscribe` und bekommt bei jeder Änderung
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

from .const import DOMAIN, DONATE_URL, SIGNAL_UPDATED
from .core import Family, Member, badge_status, level_floor
from .photos import signed_url
from .takeover import takeover_terms


def _progress(member: Member, today) -> dict[str, Any]:
    p = member.progress
    level = p.level
    return {
        "level": level,
        "earned": p.earned,
        "level_from": level_floor(level),
        "level_to": level_floor(level + 1),
        "streak": p.current_streak(today),
        "streak_today": p.streak_day == today,
        "best_streak": p.best_streak,
        "done": p.done,
        "badges": badge_status(p),
    }


def snapshot(
    hass: HomeAssistant,
    entry,
    now: datetime,
    user_id: str | None,
    is_admin: bool,
) -> dict[str, Any]:
    family: Family = entry.runtime_data.family
    actor = family.actor_for_user(user_id, is_admin=is_admin)
    allowed, multiplier, _, _ = takeover_terms(entry, now)

    def iso(value: datetime | None) -> str | None:
        return value.isoformat() if value else None

    return {
        "me": actor.member.id if actor.member else None,
        "is_manager": actor.is_manager,
        "tablet": actor.tablet and not actor.is_manager,
        "donate_url": DONATE_URL if actor.is_manager else None,
        "takeover": {"allowed": allowed, "multiplier": multiplier},
        "family_goal": family.goal.to_dict() if family.goal else None,
        "money": {"rate": family.money_rate, "payday": family.payday},
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
                "has_devices": bool(m.devices),
                "locked": bool(family.locked.get(m.id)),
                "pass_until": iso(m.pass_until) if m.has_pass(now) else None,
                "age": m.age(now),
                "progress": _progress(m, now.astimezone(family.tz).date()),
                "goal": m.goal_reward_id if m.goal_reward_id in family.rewards else None,
                "money": m.money,
                "allowance": m.allowance,
                # Kontoauszug sehen Eltern und das Kind selbst
                "money_log": (
                    family.money_history(m.id)
                    if actor.is_manager or actor.tablet or (actor.member and actor.member.id == m.id)
                    else []
                ),
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
                "requires_photo": c.requires_photo,
                "min_age": c.min_age,
                "claim_multiplier": c.claim_multiplier,
                "claim_taken_from": c.claim_taken_from,
                # Fotos sehen nur Eltern, über einen kurz gültigen Link.
                "photo_url": (
                    signed_url(hass, c.photo) if c.photo and actor.is_manager else None
                ),
                "assignees": list(c.assignees),
                "responsible": family.responsible(c, now),
                "claimed_by": c.claimed_by,
                "last_completed_by": c.last_completed_by,
                "last_completed_at": iso(c.last_completed_at),
                "steps": list(c.steps),
                "steps_done": list(c.steps_done),
            }
            for c in family.chores.values()
        ],
        "rewards": [
            {"id": r.id, "name": r.name, "cost": r.cost, "members": list(r.members)}
            for r in family.rewards.values()
        ],
        # Eltern sehen alle offenen Einlösungen, Kinder nur ihre eigenen.
        "redemptions": [
            {
                "id": r.id,
                "reward_name": r.reward_name,
                "member_id": r.member_id,
                "cost": r.cost,
                "requested_at": iso(r.requested_at),
            }
            for r in family.pending_redemptions()
            if actor.is_manager
            or actor.tablet
            or (actor.member and actor.member.id == r.member_id)
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
        connection.send_error(msg["id"], "not_loaded", "Sternchenplan ist nicht eingerichtet.")
        return
    entry = entries[0]
    user = connection.user

    @callback
    def send() -> None:
        connection.send_message(
            websocket_api.event_message(
                msg["id"],
                snapshot(hass, entry, dt_util.utcnow(), user.id, user.is_admin),
            )
        )

    connection.subscriptions[msg["id"]] = async_dispatcher_connect(hass, SIGNAL_UPDATED, send)
    connection.send_result(msg["id"])
    send()
