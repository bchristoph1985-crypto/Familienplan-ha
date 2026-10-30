"""Das Haus prüft selbst: Sensoren haken Aufgaben ab oder sagen „Jetzt bist du dran“.

Beispiele: Saugroboter „docked“ → Staubsaugen erledigt. Spülmaschine „off“ →
„Spülmaschine ausräumen, jetzt bist du dran“. Die Kopplung steht an der Aufgabe,
die Eltern stellen sie in der Karte ein. Keine Automation nötig.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import TYPE_CHECKING

from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import Event, EventStateChangedData, HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.util import dt as dt_util

from .const import SIGNAL_UPDATED
from .privacy import scrub
from .core import SYSTEM, ChoreState, FamilyError, Recurrence

if TYPE_CHECKING:
    from . import SternchenplanConfigEntry

_LOGGER = logging.getLogger(__name__)

TEXT = {
    "de": {"start": "Jetzt bist du dran: {chore}", "done": "🏠 Das Haus hat gesehen: „{chore}“ ist erledigt. ⭐ +{points}"},
    "en": {"start": "Your turn now: {chore}", "done": "🏠 The house noticed: “{chore}” is done. ⭐ +{points}"},
}


def _matches(state: str | None, wanted: str) -> bool:
    return state is not None and state.lower() == wanted.strip().lower()


@callback
def async_setup_house(hass: HomeAssistant, entry: SternchenplanConfigEntry) -> list[Callable[[], None]]:
    data = entry.runtime_data
    family = data.family
    tracked: dict[str, Callable[[], None]] = {}
    text = TEXT["de" if (hass.config.language or "").startswith("de") else "en"]

    async def notify(member_id: str, message: str) -> None:
        member = family.members.get(member_id)
        if member is None or not member.notify_service:
            return
        service = member.notify_service.removeprefix("notify.")
        if hass.services.has_service("notify", service):
            await hass.services.async_call(
                "notify", service, scrub(hass, {"title": "Sternchenplan", "message": message}), blocking=False
            )

    async def changed(event: Event[EventStateChangedData]) -> None:
        entity_id = event.data["entity_id"]
        new, old = event.data["new_state"], event.data["old_state"]
        if new is None or old is None or old.state == new.state:
            return
        if old.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            # Gerät war kurz weg (WLAN, Neustart) und meldet sich zurück: das ist kein
            # neues Ereignis. Sonst käme „Wäsche aufhängen“ nach jedem Aussetzer erneut.
            return
        now = dt_util.utcnow()
        save = False
        for chore in list(family.chores.values()):
            if chore.done_entity == entity_id and _matches(new.state, chore.done_state):
                try:
                    member_id = family.house_done(chore.id, now)
                except FamilyError as err:
                    _LOGGER.debug("Haus-Prüfung für %s übersprungen: %s", chore.name, err)
                    continue
                if member_id:
                    save = True
                    await notify(member_id, text["done"].format(chore=chore.name, points=chore.points))
            if chore.start_entity == entity_id and _matches(new.state, chore.start_state):
                if chore.recurrence is Recurrence.ON_DEMAND:
                    # Bei Bedarf: Das Gerät macht die Aufgabe fällig, der Push kommt beim Speichern.
                    if family.has("demand") and family.trigger_chore(SYSTEM, chore.id, now):
                        save = True
                    continue
                if chore.state in (ChoreState.OPEN, ChoreState.OVERDUE):
                    for member_id in family.responsible(chore, now):
                        await notify(member_id, text["start"].format(chore=chore.name))
        if save:
            await data.async_save()

    @callback
    def sync() -> None:
        wanted = {
            e for c in family.chores.values() for e in (c.done_entity, c.start_entity) if e
        }
        for entity_id in set(tracked) - wanted:
            tracked.pop(entity_id)()
        for entity_id in wanted - set(tracked):
            tracked[entity_id] = async_track_state_change_event(hass, [entity_id], changed)

    @callback
    def stop() -> None:
        for unsub in tracked.values():
            unsub()
        tracked.clear()

    sync()
    return [async_dispatcher_connect(hass, SIGNAL_UPDATED, sync), stop]
