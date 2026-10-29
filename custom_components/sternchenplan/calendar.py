"""Kalender: Fristen der Aufgaben, einer für die Familie und einer je Kind."""

from __future__ import annotations

from datetime import datetime, timedelta

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.util import dt as dt_util

from . import SternchenplanConfigEntry, SternchenplanData
from .const import DOMAIN, SIGNAL_UPDATED
from .core import Chore, Role

# Ein Termin ist die halbe Stunde vor der Frist.
SLOT = timedelta(minutes=30)
LOOKAHEAD = timedelta(days=30)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SternchenplanConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    data = entry.runtime_data
    known: set[str] = set()
    async_add_entities([ChoreCalendar(entry, None)])

    @callback
    def sync_children() -> None:
        current = {m.id for m in data.family.members.values() if m.role is Role.CHILD}
        if new := current - known:
            async_add_entities(ChoreCalendar(entry, member_id) for member_id in new)
        registry = er.async_get(hass)
        for member_id in known - current:
            if entity_id := registry.async_get_entity_id(
                "calendar", DOMAIN, f"{entry.entry_id}_calendar_{member_id}"
            ):
                registry.async_remove(entity_id)
        known.clear()
        known.update(current)

    sync_children()
    entry.async_on_unload(async_dispatcher_connect(hass, SIGNAL_UPDATED, sync_children))


class ChoreCalendar(CalendarEntity):
    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, entry: SternchenplanConfigEntry, member_id: str | None) -> None:
        self._data: SternchenplanData = entry.runtime_data
        self._member_id = member_id
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, entry.entry_id)}, name=entry.title)
        if member_id is None:
            self._attr_unique_id = f"{entry.entry_id}_calendar"
            self._attr_translation_key = "family_calendar"
        else:
            self._attr_unique_id = f"{entry.entry_id}_calendar_{member_id}"
            self._attr_translation_key = "child_calendar"
            self._attr_translation_placeholders = {
                "member": self._data.family.members[member_id].name
            }

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(self.hass, SIGNAL_UPDATED, self.async_write_ha_state)
        )

    @property
    def available(self) -> bool:
        return self._member_id is None or self._member_id in self._data.family.members

    def _event(self, due: datetime, chore: Chore, who: list[str]) -> CalendarEvent:
        family = self._data.family
        names = ", ".join(family.members[m].name for m in who if m in family.members)
        summary = f"{chore.icon or '⭐'} {chore.name}"
        if self._member_id is None and names:
            summary += f" ({names})"
        lines = [f"⭐ {chore.points}"]
        if chore.steps:
            lines += [f"☐ {s}" for s in chore.steps]
        return CalendarEvent(
            start=due - SLOT,
            end=due,
            summary=summary,
            description="\n".join(lines),
            uid=f"{chore.id}-{int(due.timestamp())}",
        )

    @property
    def event(self) -> CalendarEvent | None:
        now = dt_util.utcnow()
        found = self._data.family.occurrences(now, now + LOOKAHEAD, self._member_id, limit=50)
        return self._event(*found[0]) if found else None

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        found = self._data.family.occurrences(
            dt_util.as_utc(start_date) - SLOT, dt_util.as_utc(end_date) + SLOT, self._member_id
        )
        return [
            e for e in (self._event(*o) for o in found)
            if e.end > start_date and e.start < end_date
        ]
