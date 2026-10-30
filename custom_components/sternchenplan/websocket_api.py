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

from .const import (
    CONF_CONSEQUENCES,
    CONF_LOCK_TIME,
    CONF_RELEASE_TIME,
    DEFAULT_LOCK_TIME,
    DEFAULT_RELEASE_TIME,
    DOMAIN,
    DONATE_URL,
    HOUSE_FIELDS,
    SIGNAL_UPDATED,
)
from .core import Family, FamilyError, Member, badge_status, level_floor
from .handsfree import learning
from .photos import delete_after_review, signed_url
from .takeover import takeover_terms

GALLERY_LIMIT = 120


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

    today = now.astimezone(family.tz).date()
    month = None
    if family.has("certificate"):
        year, mon = family.previous_month(today)
        month = {
            "prev": {"year": year, "month": mon, "rows": family.month_report(year, mon)},
            "now": {"year": today.year, "month": today.month,
                    "rows": family.month_report(today.year, today.month)},
        }

    return {
        "features": sorted(family.features),
        "private_push": family.private_push,
        "screen": {"rate": family.screen_rate, "max": family.screen_max},
        "vote": family.vote,
        "month": month,
        "me": actor.member.id if actor.member else None,
        "is_manager": actor.is_manager,
        "tablet": actor.tablet and not actor.is_manager,
        "donate_url": DONATE_URL if actor.is_manager else None,
        "takeover": {"allowed": allowed and family.has("helping"), "multiplier": multiplier},
        "family_goal": family.goal.to_dict() if family.goal else None,
        "money": {"rate": family.money_rate, "payday": family.payday},
        "pause": (
            {"from": iso(family.pause_from), "until": iso(family.pause_until),
             "active": family.is_paused(now)}
            if family.pause_until else None
        ),
        "weather": (
            {"entity": family.weather_entity, "bad": family.bad_weather,
             "state": (st.state if (st := hass.states.get(family.weather_entity)) else None)}
            if family.weather_entity else None
        ),
        "report": {"day": family.report_day, "hour": family.report_hour},
        "week": family.week_report(now) if actor.is_manager else [],
        "presets": [dict(p) for p in family.presets] if actor.is_manager else [],
        "learning_tag": learning(hass) if actor.is_manager else None,
        "photo_delete": delete_after_review(entry) if actor.is_manager else None,
        # Internetsperre: Schalter und Zeiten nur für Eltern
        "lock": (
            {"enabled": bool(entry.options.get(CONF_CONSEQUENCES, False)),
             "lock_time": entry.options.get(CONF_LOCK_TIME, DEFAULT_LOCK_TIME),
             "release_time": entry.options.get(CONF_RELEASE_TIME, DEFAULT_RELEASE_TIME)}
            if actor.is_manager else None
        ),
        # Fotogalerie nur für Eltern, mit kurz gültigen Links
        "gallery": [
            {"file": e["file"], "url": signed_url(hass, e["file"]), "name": e["name"],
             "member": e["member"], "at": e["at"]}
            for e in family.gallery()[:GALLERY_LIMIT]
        ] if actor.is_manager else [],
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
                "devices": list(m.devices) if actor.is_manager else [],
                "locked": bool(family.locked.get(m.id)),
                "pass_until": iso(m.pass_until) if m.has_pass(now) else None,
                "age": m.age(now),
                "progress": _progress(m, now.astimezone(family.tz).date()),
                "goal": m.goal_reward_id if m.goal_reward_id in family.rewards else None,
                "money": m.money,
                "picture_mode": m.picture_mode,
                "theme": m.theme,
                "pet": m.pet,
                "pet_name": m.pet_name,
                "lamp": m.lamp if actor.is_manager else "",
                "screen_devices": list(m.screen_devices) if actor.is_manager else [],
                "has_screen": bool(m.screen_devices),
                "screen_until": iso(m.screen_until) if family.screen_active(m, now) else None,
                "screen_left": family.screen_left_today(m, now),
                # Bonus und Abzug sehen Eltern und das Kind selbst
                "star_log": (
                    family.star_history(m.id, 10)
                    if actor.is_manager or actor.tablet or (actor.member and actor.member.id == m.id)
                    else []
                ),
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
                "weekdays": list(c.weekdays),
                "icon": c.icon,
                "outdoor": c.outdoor,
                "has_tag": bool(c.tag_id),
                **{k: getattr(c, k) for k in HOUSE_FIELDS},
                "weather_shift": c.weather_shift,
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
    websocket_api.async_register_command(hass, ws_export)


@websocket_api.websocket_command(
    {vol.Required("type"): f"{DOMAIN}/export", vol.Required("member"): str}
)
@callback
def ws_export(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """Datenauskunft: alles über eine Person als JSON. Nur für Eltern."""
    entries = hass.config_entries.async_loaded_entries(DOMAIN)
    if not entries:
        connection.send_error(msg["id"], "not_loaded", "Sternchenplan ist nicht eingerichtet.")
        return
    family: Family = entries[0].runtime_data.family
    actor = family.actor_for_user(connection.user.id, is_admin=connection.user.is_admin)
    try:
        data = family.export_member(actor, msg["member"])
    except FamilyError as err:
        connection.send_error(msg["id"], "not_allowed", str(err))
        return
    connection.send_result(msg["id"], data)


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
