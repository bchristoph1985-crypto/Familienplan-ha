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


# Startaufgaben: Schlüssel -> (Name, Wiederholung, Punkte, je Kind einzeln, ab Alter)
# Die Altersgrenzen sind Richtwerte, Eltern können sie je Aufgabe ändern.
STARTER_CHORES: dict[str, tuple[str, Recurrence, int, bool, int]] = {
    "table": ("Tisch decken", Recurrence.DAILY, 1, False, 4),
    "dishwasher": ("Spülmaschine ausräumen", Recurrence.DAILY, 2, False, 7),
    "trash": ("Müll rausbringen", Recurrence.DAILY, 1, False, 8),
    "room": ("Zimmer aufräumen", Recurrence.WEEKLY, 3, True, 4),
    "bathroom": ("Bad putzen", Recurrence.WEEKLY, 5, False, 10),
    "vacuum": ("Staubsaugen", Recurrence.WEEKLY, 3, False, 8),
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


def suitable_starters(ages: list[int | None]) -> list[str]:
    """Startaufgaben, für die mindestens ein Kind alt genug ist."""
    known = [a for a in ages if a is not None]
    if not known or len(known) < len(ages):
        return list(STARTER_CHORES)
    oldest = max(known)
    return [key for key, spec in STARTER_CHORES.items() if oldest >= spec[4]]


def build_family(
    people: list[Person],
    parent_ids: list[str],
    extra_children: list[str],
    starters: list[str],
    now: datetime,
    *,
    ages: dict[str, int] | None = None,
    english: bool = False,
) -> Family:
    """Familie aus den Antworten des Assistenten bauen.

    `ages` ordnet Kindernamen ihr Alter zu. Startaufgaben bekommen ein
    Mindestalter und gehen nur an Kinder, die alt genug sind.
    """
    ages = ages or {}
    family = Family()
    for person in people:
        role = Role.PARENT if person.entity_id in parent_ids else Role.CHILD
        family.add_member(
            SYSTEM, person.name, role, user_id=person.user_id, notify_service=person.notify_service
        )
    for name in extra_children:
        family.add_member(SYSTEM, name, Role.CHILD)

    children = [m for m in family.members.values() if m.role is Role.CHILD]
    for child in children:
        if child.name in ages:
            family.set_age(SYSTEM, child.id, ages[child.name], now)
    for key in starters:
        if key not in STARTER_CHORES:
            continue
        name, recurrence, points, per_child, min_age = STARTER_CHORES[key]
        if english:
            name = STARTER_NAMES_EN[key]
        fitting = [c for c in children if c.old_enough(min_age, now)]
        if not fitting:
            continue
        due = _first_due(recurrence, now)
        if per_child:
            for child in fitting:
                family.create_chore(
                    SYSTEM, f"{name} ({child.name})", [child.id],
                    points=points, recurrence=recurrence, due=due, min_age=min_age,
                )
        else:
            # Alle Kinder eintragen: Wer zu jung ist, wird übersprungen und
            # rückt automatisch nach, sobald das Alter erreicht ist.
            family.create_chore(
                SYSTEM, name, [c.id for c in children],
                points=points, recurrence=recurrence, due=due,
                rotation=len(children) > 1, min_age=min_age,
            )
    return family


def split_names(value: str) -> list[str]:
    return [n.strip() for n in (value or "").replace(";", ",").split(",") if n.strip()]
