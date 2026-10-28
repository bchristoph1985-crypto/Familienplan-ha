"""Erinnerungen per HA-Push: an Kinder zu festen Uhrzeiten, Sammelnachricht an Eltern."""

from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import datetime, time, timedelta
from typing import TYPE_CHECKING

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_time_change
from homeassistant.util import dt as dt_util

from .const import (
    CONF_PARENT_SUMMARY_TIME,
    CONF_REMINDER_TIMES,
    DEFAULT_PARENT_SUMMARY_TIME,
    DEFAULT_REMINDER_TIMES,
)
from .core import ChoreState, Family, Role

if TYPE_CHECKING:
    from . import FamilienplanConfigEntry

_LOGGER = logging.getLogger(__name__)

_TEXT = {
    "de": {
        "title": "Familienplan",
        "open": "Noch offen heute: {list}",
        "overdue": "überfällig",
        "summary_child": "{name}: {count} offen",
        "summary_done": "Alle Aufgaben für heute erledigt.",
        "summary_approval": "Wartet auf Freigabe: {list}",
    },
    "en": {
        "title": "Familienplan",
        "open": "Still open today: {list}",
        "overdue": "overdue",
        "summary_child": "{name}: {count} open",
        "summary_done": "All chores for today are done.",
        "summary_approval": "Waiting for approval: {list}",
    },
}


def parse_times(value: str) -> list[time]:
    """'15:00, 17:00' -> [time(15), time(17)]. Wirft ValueError bei Unsinn."""
    result = []
    for part in value.replace(";", ",").split(","):
        part = part.strip()
        if part:
            result.append(time.fromisoformat(part))
    return sorted(set(result))


def _text(hass: HomeAssistant) -> dict[str, str]:
    return _TEXT["de" if (hass.config.language or "").startswith("de") else "en"]


def _end_of_day(now: datetime) -> datetime:
    local = dt_util.as_local(now)
    end = datetime.combine(local.date() + timedelta(days=1), time(), local.tzinfo)
    return dt_util.as_utc(end)


def child_message(hass: HomeAssistant, family: Family, member_id: str, now: datetime) -> str | None:
    text = _text(hass)
    chores = family.open_until(member_id, now, _end_of_day(now))
    if not chores:
        return None
    names = [
        f"{c.name} ({text['overdue']})" if c.state is ChoreState.OVERDUE else c.name
        for c in chores
    ]
    return text["open"].format(list=", ".join(names))


def parent_message(hass: HomeAssistant, family: Family, now: datetime) -> str:
    text = _text(hass)
    until = _end_of_day(now)
    lines = []
    for member in family.members.values():
        if member.role is not Role.CHILD or member.is_away(now):
            continue
        if count := len(family.open_until(member.id, now, until)):
            lines.append(text["summary_child"].format(name=member.name, count=count))
    if not lines:
        lines.append(text["summary_done"])
    waiting = [c.name for c in family.chores.values() if c.state is ChoreState.CLAIMED]
    if waiting:
        lines.append(text["summary_approval"].format(list=", ".join(waiting)))
    return "\n".join(lines)


async def _notify(hass: HomeAssistant, service: str, title: str, message: str) -> None:
    service = service.removeprefix("notify.")
    if not hass.services.has_service("notify", service):
        _LOGGER.warning("Benachrichtigungsdienst notify.%s gibt es nicht", service)
        return
    await hass.services.async_call(
        "notify", service, {"title": title, "message": message}, blocking=False
    )


@callback
def async_setup_reminders(
    hass: HomeAssistant, entry: FamilienplanConfigEntry
) -> list[Callable[[], None]]:
    """Zeitpläne anlegen. Gibt die Abmelde-Funktionen zurück."""
    options = entry.options
    try:
        child_times = parse_times(options.get(CONF_REMINDER_TIMES, DEFAULT_REMINDER_TIMES))
        parent_times = parse_times(
            options.get(CONF_PARENT_SUMMARY_TIME, DEFAULT_PARENT_SUMMARY_TIME)
        )
    except ValueError:
        _LOGGER.error("Ungültige Uhrzeit in den Erinnerungs-Einstellungen")
        return []

    async def remind_children(now: datetime) -> None:
        family = entry.runtime_data.family
        now = dt_util.utcnow()
        for member in family.members.values():
            if member.role is not Role.CHILD or not member.notify_service:
                continue
            if member.is_away(now):
                continue
            if message := child_message(hass, family, member.id, now):
                await _notify(hass, member.notify_service, _text(hass)["title"], message)

    async def summary_for_parents(now: datetime) -> None:
        family = entry.runtime_data.family
        now = dt_util.utcnow()
        message = parent_message(hass, family, now)
        for member in family.members.values():
            if member.role is Role.PARENT and member.notify_service:
                await _notify(hass, member.notify_service, _text(hass)["title"], message)

    unsubs = [
        async_track_time_change(hass, remind_children, hour=t.hour, minute=t.minute, second=0)
        for t in child_times
    ]
    unsubs += [
        async_track_time_change(hass, summary_for_parents, hour=t.hour, minute=t.minute, second=0)
        for t in parent_times
    ]
    return unsubs
