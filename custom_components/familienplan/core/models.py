"""Datenmodell des Aufgaben-Kerns.

Dieses Paket importiert bewusst nichts aus Home Assistant. So lässt sich die
Logik ohne HA testen und später wiederverwenden.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any


class Role(StrEnum):
    PARENT = "parent"
    CHILD = "child"


class Recurrence(StrEnum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"


class ChoreState(StrEnum):
    OPEN = "open"
    CLAIMED = "claimed"  # vom Kind gemeldet, wartet auf Elternfreigabe
    DONE = "done"  # nur bei einmaligen Aufgaben dauerhaft
    OVERDUE = "overdue"


@dataclass
class Member:
    id: str
    name: str
    role: Role
    user_id: str | None = None
    notify_service: str | None = None
    points: int = 0
    away_from: datetime | None = None
    away_until: datetime | None = None
    substitute_id: str | None = None
    devices: list[str] = field(default_factory=list)
    pass_until: datetime | None = None

    def has_pass(self, now: datetime) -> bool:
        return self.pass_until is not None and now < self.pass_until

    def is_away(self, now: datetime) -> bool:
        if self.away_until is None or now >= self.away_until:
            return False
        return self.away_from is None or now >= self.away_from

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role.value,
            "user_id": self.user_id,
            "notify_service": self.notify_service,
            "points": self.points,
            "away_from": self.away_from.isoformat() if self.away_from else None,
            "away_until": self.away_until.isoformat() if self.away_until else None,
            "substitute_id": self.substitute_id,
            "devices": list(self.devices),
            "pass_until": self.pass_until.isoformat() if self.pass_until else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Member:
        return cls(
            id=data["id"],
            name=data["name"],
            role=Role(data["role"]),
            user_id=data.get("user_id"),
            notify_service=data.get("notify_service"),
            points=int(data.get("points", 0)),
            away_from=_parse_dt(data.get("away_from")),
            away_until=_parse_dt(data.get("away_until")),
            substitute_id=data.get("substitute_id"),
            devices=list(data.get("devices", [])),
            pass_until=_parse_dt(data.get("pass_until")),
        )


@dataclass
class Chore:
    id: str
    name: str
    assignees: list[str]
    points: int = 1
    recurrence: Recurrence = Recurrence.NONE
    due: datetime | None = None
    rotation: bool = False
    rotation_index: int = 0
    requires_approval: bool = False
    state: ChoreState = ChoreState.OPEN
    claimed_by: str | None = None
    last_completed_by: str | None = None
    last_completed_at: datetime | None = None
    history: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "assignees": list(self.assignees),
            "points": self.points,
            "recurrence": self.recurrence.value,
            "due": self.due.isoformat() if self.due else None,
            "rotation": self.rotation,
            "rotation_index": self.rotation_index,
            "requires_approval": self.requires_approval,
            "state": self.state.value,
            "claimed_by": self.claimed_by,
            "last_completed_by": self.last_completed_by,
            "last_completed_at": (
                self.last_completed_at.isoformat() if self.last_completed_at else None
            ),
            "history": list(self.history),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Chore:
        return cls(
            id=data["id"],
            name=data["name"],
            assignees=list(data.get("assignees", [])),
            points=int(data.get("points", 1)),
            recurrence=Recurrence(data.get("recurrence", Recurrence.NONE)),
            due=_parse_dt(data.get("due")),
            rotation=bool(data.get("rotation", False)),
            rotation_index=int(data.get("rotation_index", 0)),
            requires_approval=bool(data.get("requires_approval", False)),
            state=ChoreState(data.get("state", ChoreState.OPEN)),
            claimed_by=data.get("claimed_by"),
            last_completed_by=data.get("last_completed_by"),
            last_completed_at=_parse_dt(data.get("last_completed_at")),
            history=list(data.get("history", [])),
        )


def _parse_dt(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value else None
