"""Hilfen für die einfache Einrichtung: Familie erkennen, Handys zuordnen, Startaufgaben."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.util import dt as dt_util, slugify

from .core import SYSTEM, Family, Recurrence, Role


@dataclass
class Person:
    entity_id: str
    name: str
    user_id: str | None
    notify_service: str | None


def notify_for_person(hass: HomeAssistant, state) -> str | None:
    """Push-Dienst der Companion-App einer Person, z. B. mobile_app_fold_7_benni."""
    ent_reg = er.async_get(hass)
    dev_reg = dr.async_get(hass)
    for tracker in state.attributes.get("device_trackers", []):
        entry = ent_reg.async_get(tracker)
        if entry is None or entry.platform != "mobile_app" or entry.device_id is None:
            continue
        device = dev_reg.async_get(entry.device_id)
        if device is None:
            continue
        service = f"mobile_app_{slugify(device.name_by_user or device.name or '')}"
        if hass.services.has_service("notify", service):
            return service
    return None


def find_people(hass: HomeAssistant) -> list[Person]:
    """Alle Personen aus HA (Einstellungen → Personen), mit Konto und Handy."""
    people = []
    for state in sorted(hass.states.async_all("person"), key=lambda s: s.name.casefold()):
        people.append(
            Person(
                entity_id=state.entity_id,
                name=state.name,
                user_id=state.attributes.get("user_id"),
                notify_service=notify_for_person(hass, state),
            )
        )
    return people


# Startaufgaben: Schlüssel -> (Name, Wiederholung, Punkte, je Kind einzeln)
STARTER_CHORES: dict[str, tuple[str, Recurrence, int, bool]] = {
    "table": ("Tisch decken", Recurrence.DAILY, 1, False),
    "dishwasher": ("Spülmaschine ausräumen", Recurrence.DAILY, 2, False),
    "trash": ("Müll rausbringen", Recurrence.DAILY, 1, False),
    "room": ("Zimmer aufräumen", Recurrence.WEEKLY, 3, True),
    "bathroom": ("Bad putzen", Recurrence.WEEKLY, 5, False),
    "vacuum": ("Staubsaugen", Recurrence.WEEKLY, 3, False),
}
DEFAULT_STARTERS = ["dishwasher", "trash", "room"]
STARTER_NAMES_EN = {
    "table": "Set the table",
    "dishwasher": "Empty the dishwasher",
    "trash": "Take out the trash",
    "room": "Tidy up room",
    "bathroom": "Clean the bathroom",
    "vacuum": "Vacuum",
}


def _first_due(recurrence: Recurrence, now: datetime) -> datetime:
    """Täglich: heute 19:00 (oder morgen). Wöchentlich: nächster Samstag 12:00."""
    local = dt_util.as_local(now)
    if recurrence is Recurrence.DAILY:
        due = local.replace(hour=19, minute=0, second=0, microsecond=0)
        if due <= local:
            due += timedelta(days=1)
    else:
        due = local.replace(hour=12, minute=0, second=0, microsecond=0)
        due += timedelta(days=(5 - local.weekday()) % 7)
        if due <= local:
            due += timedelta(days=7)
    return dt_util.as_utc(due)


def build_family(
    people: list[Person],
    parent_ids: list[str],
    extra_children: list[str],
    starters: list[str],
    now: datetime,
    *,
    english: bool = False,
) -> Family:
    """Familie aus den Antworten des Assistenten bauen."""
    family = Family()
    for person in people:
        role = Role.PARENT if person.entity_id in parent_ids else Role.CHILD
        family.add_member(
            SYSTEM, person.name, role, user_id=person.user_id, notify_service=person.notify_service
        )
    for name in extra_children:
        family.add_member(SYSTEM, name, Role.CHILD)

    children = [m for m in family.members.values() if m.role is Role.CHILD]
    if not children:
        return family
    for key in starters:
        if key not in STARTER_CHORES:
            continue
        name, recurrence, points, per_child = STARTER_CHORES[key]
        if english:
            name = STARTER_NAMES_EN[key]
        due = _first_due(recurrence, now)
        if per_child:
            for child in children:
                family.create_chore(
                    SYSTEM, f"{name} ({child.name})", [child.id],
                    points=points, recurrence=recurrence, due=due,
                )
        else:
            family.create_chore(
                SYSTEM, name, [c.id for c in children],
                points=points, recurrence=recurrence, due=due, rotation=len(children) > 1,
            )
    return family


def split_names(value: str) -> list[str]:
    return [n.strip() for n in (value or "").replace(";", ",").split(",") if n.strip()]
