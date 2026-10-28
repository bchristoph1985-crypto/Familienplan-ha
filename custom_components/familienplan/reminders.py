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
    CONF_ANNOUNCE_NOTIFY,
    CONF_ANNOUNCE_TIMES,
    CONF_PARENT_SUMMARY_TIME,
    CONF_REMINDER_TIMES,
    CONF_SPEAKERS,
    CONF_TTS_ENGINE,
    DEFAULT_ANNOUNCE_TIMES,
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
        "say_child": "{name}, bei dir ist noch offen: {list}.",
        "say_and": "und",
        "say_done": "Alle Aufgaben für heute sind erledigt.",
    },
    "en": {
        "title": "Familienplan",
        "open": "Still open today: {list}",
        "overdue": "overdue",
        "summary_child": "{name}: {count} open",
        "summary_done": "All chores for today are done.",
        "summary_approval": "Waiting for approval: {list}",
        "say_child": "{name}, you still have to do: {list}.",
        "say_and": "and",
        "say_done": "All chores for today are done.",
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


def _spoken_list(items: list[str], word_and: str) -> str:
    if len(items) < 2:
        return "".join(items)
    return f"{', '.join(items[:-1])} {word_and} {items[-1]}"


def announcement(hass: HomeAssistant, family: Family, now: datetime) -> str | None:
    """Ansagetext für den Lautsprecher: wer hat heute noch was offen. None, wenn nichts."""
    text = _text(hass)
    until = _end_of_day(now)
    parts = []
    for member in family.members.values():
        if member.role is not Role.CHILD or member.is_away(now):
            continue
        chores = family.open_until(member.id, now, until)
        if chores:
            names = _spoken_list([c.name for c in chores], text["say_and"])
            parts.append(text["say_child"].format(name=member.name, list=names))
    return " ".join(parts) or None


def announce_configured(entry: FamilienplanConfigEntry) -> bool:
    options = entry.options
    return bool(
        (options.get(CONF_TTS_ENGINE) and options.get(CONF_SPEAKERS))
        or options.get(CONF_ANNOUNCE_NOTIFY)
    )


async def async_announce(hass: HomeAssistant, entry: FamilienplanConfigEntry, message: str) -> None:
    """Ansage über die eingestellten Lautsprecher.

    Weg 1: eine TTS-Engine von HA auf beliebige Mediaplayer (Sonos, Google,
    HomePod über AirPlay, ...). Weg 2: Benachrichtigungsdienste, die selbst
    sprechen, z. B. Alexa Media Player. Beides geht auch gleichzeitig.
    """
    options = entry.options
    engine = options.get(CONF_TTS_ENGINE)
    speakers = options.get(CONF_SPEAKERS) or []
    if engine and speakers:
        try:
            await hass.services.async_call(
                "tts",
                "speak",
                {"entity_id": engine, "media_player_entity_id": speakers, "message": message},
                blocking=True,
            )
        except Exception:  # noqa: BLE001 – ein toter Lautsprecher darf nichts anderes stoppen
            _LOGGER.exception("Ansage über %s fehlgeschlagen", engine)
    for service in options.get(CONF_ANNOUNCE_NOTIFY) or []:
        service = service.removeprefix("notify.")
        if not hass.services.has_service("notify", service):
            _LOGGER.warning("Benachrichtigungsdienst notify.%s gibt es nicht", service)
            continue
        payload: dict = {"message": message}
        if service.startswith("alexa_media"):
            payload["data"] = {"type": "announce"}
        await hass.services.async_call("notify", service, payload, blocking=False)


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
        announce_times = parse_times(options.get(CONF_ANNOUNCE_TIMES, DEFAULT_ANNOUNCE_TIMES))
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

    async def announce(now: datetime) -> None:
        now = dt_util.utcnow()
        if message := announcement(hass, entry.runtime_data.family, now):
            await async_announce(hass, entry, message)

    unsubs = [
        async_track_time_change(hass, remind_children, hour=t.hour, minute=t.minute, second=0)
        for t in child_times
    ]
    unsubs += [
        async_track_time_change(hass, summary_for_parents, hour=t.hour, minute=t.minute, second=0)
        for t in parent_times
    ]
    if announce_configured(entry):
        unsubs += [
            async_track_time_change(hass, announce, hour=t.hour, minute=t.minute, second=0)
            for t in announce_times
        ]
    return unsubs
