"""Sensoren: Punkte je Mitglied und Status je Aufgabe."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.util import dt as dt_util

from . import SternchenplanConfigEntry, SternchenplanData
from .const import DOMAIN, SIGNAL_UPDATED
from .core import ChoreState


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SternchenplanConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    data = entry.runtime_data
    known_chores: set[str] = set()

    async_add_entities(MemberPointsSensor(entry, m.id) for m in data.family.members.values())

    @callback
    def sync_chores() -> None:
        current = set(data.family.chores)
        new = current - known_chores
        if new:
            async_add_entities(ChoreSensor(entry, chore_id) for chore_id in new)
        registry = er.async_get(hass)
        for chore_id in known_chores - current:
            if entity_id := registry.async_get_entity_id(
                "sensor", DOMAIN, f"{entry.entry_id}_chore_{chore_id}"
            ):
                registry.async_remove(entity_id)
        known_chores.clear()
        known_chores.update(current)

    sync_chores()
    entry.async_on_unload(async_dispatcher_connect(hass, SIGNAL_UPDATED, sync_chores))


class _SternchenplanSensor(SensorEntity):
    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, entry: SternchenplanConfigEntry) -> None:
        self._data: SternchenplanData = entry.runtime_data
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)}, name=entry.title
        )

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(self.hass, SIGNAL_UPDATED, self.async_write_ha_state)
        )


class MemberPointsSensor(_SternchenplanSensor):
    _attr_translation_key = "points"
    _attr_native_unit_of_measurement = "P"

    def __init__(self, entry: SternchenplanConfigEntry, member_id: str) -> None:
        super().__init__(entry)
        self._member_id = member_id
        member = self._data.family.members[member_id]
        self._attr_unique_id = f"{entry.entry_id}_points_{member_id}"
        self._attr_translation_placeholders = {"member": member.name}

    @property
    def available(self) -> bool:
        return self._member_id in self._data.family.members

    @property
    def native_value(self) -> int | None:
        member = self._data.family.members.get(self._member_id)
        return member.points if member else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        member = self._data.family.members.get(self._member_id)
        if member is None:
            return {}
        now = dt_util.utcnow()
        substitute = self._data.family.members.get(member.substitute_id or "")
        return {
            "member_id": member.id,
            "role": member.role.value,
            "away": member.is_away(now),
            "away_from": member.away_from.isoformat() if member.away_from else None,
            "away_until": member.away_until.isoformat() if member.away_until else None,
            "substitute": substitute.name if substitute else None,
            "devices": list(member.devices),
            "internet_locked": bool(self._data.family.locked.get(member.id)),
            "pass_until": member.pass_until.isoformat() if member.has_pass(now) else None,
            "chores": [
                {"id": c.id, "name": c.name, "state": c.state.value,
                 "due": c.due.isoformat() if c.due else None}
                for c in self._data.family.chores_for(member.id, now)
            ],
        }


class ChoreSensor(_SternchenplanSensor):
    _attr_translation_key = "chore"
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = [s.value for s in ChoreState]

    def __init__(self, entry: SternchenplanConfigEntry, chore_id: str) -> None:
        super().__init__(entry)
        self._chore_id = chore_id
        self._attr_unique_id = f"{entry.entry_id}_chore_{chore_id}"
        self._attr_translation_placeholders = {
            "chore": self._data.family.chores[chore_id].name
        }

    @property
    def available(self) -> bool:
        return self._chore_id in self._data.family.chores

    @property
    def native_value(self) -> str | None:
        chore = self._data.family.chores.get(self._chore_id)
        return chore.state.value if chore else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        family = self._data.family
        chore = family.chores.get(self._chore_id)
        if chore is None:
            return {}

        def name(member_id: str | None) -> str | None:
            member = family.members.get(member_id) if member_id else None
            return member.name if member else None

        responsible = family.responsible(chore, dt_util.utcnow())
        return {
            "chore_id": chore.id,
            "responsible": [name(m) for m in responsible],
            "paused": bool(chore.assignees) and not responsible,
            "assignees": [name(m) for m in chore.assignees],
            "points": chore.points,
            "recurrence": chore.recurrence.value,
            "due": chore.due.isoformat() if chore.due else None,
            "rotation": chore.rotation,
            "requires_approval": chore.requires_approval,
            "claimed_by": name(chore.claimed_by),
            "last_completed_by": name(chore.last_completed_by),
            "last_completed_at": (
                chore.last_completed_at.isoformat() if chore.last_completed_at else None
            ),
        }
