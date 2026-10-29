"""Konsequenzen: Internet der Freizeitgeräte sperren, solange Aufgaben überfällig sind.

Gesteuert werden nur die Schalter, die Eltern je Kind ausgewählt haben, z. B.
die „Internetzugang“-Schalter der FRITZ!Box-Integration. Gesperrt wird nur im
Sperrfenster (Standard 20:00 bis 05:00). Freigegeben werden nur Geräte, die
Sternchenplan selbst gesperrt hat.
"""

from __future__ import annotations

import logging
from datetime import datetime, time, timedelta
from typing import TYPE_CHECKING

from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.core import Context, HomeAssistant
from homeassistant.util import dt as dt_util

from .const import (
    CONF_CONSEQUENCES,
    CONF_LOCK_TIME,
    CONF_RELEASE_TIME,
    DEFAULT_LOCK_TIME,
    DEFAULT_RELEASE_TIME,
)
from .core import Role

if TYPE_CHECKING:
    from . import SternchenplanConfigEntry

_LOGGER = logging.getLogger(__name__)


def in_window(local_time: time, start: time, end: time) -> bool:
    """Liegt die Uhrzeit im Fenster? Fenster über Mitternacht sind erlaubt."""
    if start == end:
        return True
    if start < end:
        return start <= local_time < end
    return local_time >= start or local_time < end


def _times(entry: SternchenplanConfigEntry) -> tuple[time, time]:
    options = entry.options
    try:
        return (
            time.fromisoformat(options.get(CONF_LOCK_TIME, DEFAULT_LOCK_TIME)),
            time.fromisoformat(options.get(CONF_RELEASE_TIME, DEFAULT_RELEASE_TIME)),
        )
    except ValueError:
        _LOGGER.error("Ungültige Sperrzeit, nehme Standard")
        return time.fromisoformat(DEFAULT_LOCK_TIME), time.fromisoformat(DEFAULT_RELEASE_TIME)


def next_release(entry: SternchenplanConfigEntry, now: datetime) -> datetime:
    """Nächstes Ende des Sperrfensters, z. B. morgen 05:00. Standard für Freikarten."""
    _, end = _times(entry)
    local = dt_util.as_local(now)
    release = local.replace(hour=end.hour, minute=end.minute, second=0, microsecond=0)
    if release <= local:
        release += timedelta(days=1)
    return dt_util.as_utc(release)


async def _switch(hass: HomeAssistant, entity_ids: list[str], on: bool, context: Context) -> None:
    if entity_ids:
        await hass.services.async_call(
            "switch",
            "turn_on" if on else "turn_off",
            {"entity_id": entity_ids},
            blocking=True,
            context=context,
        )


async def async_apply(hass: HomeAssistant, entry: SternchenplanConfigEntry, now: datetime | None = None) -> bool:
    """Sperren und Freigaben an den aktuellen Stand anpassen.

    Läuft jede Minute und nach jeder Änderung. Gibt True zurück, wenn sich der
    gespeicherte Sperrstand geändert hat.
    """
    family = entry.runtime_data.family
    now = now or dt_util.utcnow()
    # Ohne Pro wird nichts gesperrt, bereits gesperrte Geräte werden freigegeben.
    enabled = entry.options.get(CONF_CONSEQUENCES, False) and entry.runtime_data.pro
    start, end = _times(entry)
    window = in_window(dt_util.as_local(now).time(), start, end)
    context = Context()
    changed = False

    for member in family.members.values():
        if member.role is not Role.CHILD:
            continue
        locked = family.locked.get(member.id, [])
        want = enabled and window and family.should_lock(member.id, now)

        stale = [e for e in locked if e not in member.devices]
        if stale:
            # Gerät wurde aus der Liste genommen: freigeben und vergessen.
            await _switch(hass, [e for e in stale if _is(hass, e, STATE_OFF)], True, context)
            locked = [e for e in locked if e in member.devices]
            family.locked[member.id] = locked
            changed = True

        if want:
            # Auch erneut ausschalten, falls jemand ein Gerät wieder
            # eingeschaltet hat. Nur Geräte, die gerade an sind.
            to_lock = [e for e in member.devices if _is(hass, e, STATE_ON)]
            if to_lock:
                await _switch(hass, to_lock, False, context)
            new_locked = sorted(set(locked) | set(to_lock))
            if new_locked != locked:
                family.locked[member.id] = new_locked
                changed = True
        elif locked:
            # Nur freigeben, was noch aus ist. Was schon wieder an ist, ist
            # erledigt. Was gerade nicht erreichbar ist (Router neu gestartet),
            # bleibt gemerkt und wird beim nächsten Durchlauf freigegeben.
            to_release = [e for e in locked if _is(hass, e, STATE_OFF)]
            await _switch(hass, to_release, True, context)
            pending = [e for e in locked if not _is(hass, e, STATE_OFF) and not _is(hass, e, STATE_ON)]
            if pending:
                family.locked[member.id] = pending
            else:
                family.locked.pop(member.id, None)
            changed = True

    for member_id in [m for m, devices in family.locked.items() if not devices]:
        del family.locked[member_id]
        changed = True
    return changed


def _is(hass: HomeAssistant, entity_id: str, wanted: str) -> bool:
    state = hass.states.get(entity_id)
    return state is not None and state.state == wanted
