"""Freigeben direkt aus der Push-Nachricht (Companion-App-Knöpfe).

Die Knöpfe lösen in Home Assistant das Ereignis `mobile_app_notification_action`
aus. Es trägt das HA-Konto des Handys, deshalb prüfen wir die Rechte wie bei
jedem Dienst: Nur Eltern dürfen freigeben.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.util import dt as dt_util

from .core import Family, FamilyError, Role
from .photos import signed_url

if TYPE_CHECKING:
    from . import SternchenplanConfigEntry

_LOGGER = logging.getLogger(__name__)

PREFIX = "STERNCHENPLAN"
APPROVE, REJECT, GIVE, REFUSE = "APPROVE", "REJECT", "GIVE", "REFUSE"

_TEXT = {
    "de": {
        "claimed": "{name} hat „{chore}“ erledigt. Freigeben?",
        "redeemed": "{name} möchte „{reward}“ einlösen.",
        "approve": "✓ Freigeben",
        "reject": "Ablehnen",
        "give": "✓ Geben",
        "refuse": "Ablehnen",
    },
    "en": {
        "claimed": "{name} finished “{chore}”. Approve?",
        "redeemed": "{name} wants to redeem “{reward}”.",
        "approve": "✓ Approve",
        "reject": "Reject",
        "give": "✓ Give",
        "refuse": "Refuse",
    },
}


def _text(hass: HomeAssistant) -> dict[str, str]:
    return _TEXT["de" if (hass.config.language or "").startswith("de") else "en"]


def _tag(item_id: str) -> str:
    return f"sternchenplan-{item_id}"


def _parents(family: Family) -> list[str]:
    return [
        m.notify_service.removeprefix("notify.")
        for m in family.members.values()
        if m.role is Role.PARENT and m.notify_service
    ]


async def _send(hass: HomeAssistant, service: str, payload: dict[str, Any]) -> None:
    if not hass.services.has_service("notify", service):
        _LOGGER.warning("Benachrichtigungsdienst notify.%s gibt es nicht", service)
        return
    if not service.startswith("mobile_app"):
        # Knöpfe und Bilder versteht nur die Companion-App
        payload = {k: v for k, v in payload.items() if k != "data"}
    await hass.services.async_call("notify", service, payload, blocking=False)


async def async_ask_parents(hass: HomeAssistant, family: Family, event: dict[str, Any]) -> None:
    """Push an alle Eltern mit Knöpfen zum Freigeben oder Ablehnen."""
    text = _text(hass)
    member = family.members.get(event["member"])
    if member is None:
        return
    if event["type"] == "needs_approval":
        item = event["chore"]
        message = text["claimed"].format(name=member.name, chore=event["name"])
        actions = [(APPROVE, text["approve"]), (REJECT, text["reject"])]
    else:
        item = event["redemption"]
        message = text["redeemed"].format(name=member.name, reward=event["reward"])
        actions = [(GIVE, text["give"]), (REFUSE, text["refuse"])]
    data: dict[str, Any] = {
        "tag": _tag(item),
        "actions": [{"action": f"{PREFIX}:{a}:{item}", "title": t} for a, t in actions],
    }
    chore = family.chores.get(item)
    if chore is not None and chore.photo:
        data["image"] = signed_url(hass, chore.photo)
    payload = {"title": "Sternchenplan", "message": message, "data": data}
    for service in _parents(family):
        await _send(hass, service, dict(payload))


async def _clear(hass: HomeAssistant, family: Family, item_id: str) -> None:
    """Die Frage auf den anderen Eltern-Handys wegräumen."""
    for service in _parents(family):
        if service.startswith("mobile_app") and hass.services.has_service("notify", service):
            await hass.services.async_call(
                "notify", service,
                {"message": "clear_notification", "data": {"tag": _tag(item_id)}},
                blocking=False,
            )


@callback
def async_setup_actions(
    hass: HomeAssistant, entry: SternchenplanConfigEntry
) -> Callable[[], None]:
    async def handle(event: Event) -> None:
        parts = str(event.data.get("action", "")).split(":")
        if len(parts) != 3 or parts[0] != PREFIX:
            return
        _, what, item_id = parts
        data = entry.runtime_data
        user_id = event.context.user_id
        user = await hass.auth.async_get_user(user_id) if user_id else None
        actor = data.family.actor_for_user(user_id, is_admin=bool(user and user.is_admin))
        now = dt_util.utcnow()
        family = data.family
        try:
            if what == APPROVE:
                family.approve(actor, item_id, now)
            elif what == REJECT:
                family.reject(actor, item_id, now)
            elif what == GIVE:
                family.approve_redemption(actor, item_id, now)
            elif what == REFUSE:
                family.reject_redemption(actor, item_id, now)
            else:
                return
        except FamilyError as err:
            # z. B. schon vom anderen Elternteil erledigt, oder kein Elternkonto
            _LOGGER.info("Knopf in der Push-Nachricht ignoriert: %s", err)
            return
        await data.async_save()
        await _clear(hass, family, item_id)

    return hass.bus.async_listen("mobile_app_notification_action", handle)
