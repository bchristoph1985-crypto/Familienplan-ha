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
    birth_year: int | None = None

    def age(self, now: datetime) -> int | None:
        """Alter in Jahren, auf das Jahr genau. None, wenn nicht bekannt."""
        return None if self.birth_year is None else now.year - self.birth_year

    def old_enough(self, min_age: int, now: datetime) -> bool:
        """Unbekanntes Alter zählt als alt genug, damit nichts unbemerkt ruht."""
        age = self.age(now)
        return min_age <= 0 or age is None or age >= min_age

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
            "birth_year": self.birth_year,
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
            birth_year=data.get("birth_year"),
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
    requires_photo: bool = False
    min_age: int = 0  # 0 = für alle
    state: ChoreState = ChoreState.OPEN
    claimed_by: str | None = None
    # Bei Übernahme durch Geschwister: Punkte-Faktor und von wem übernommen
    claim_multiplier: int = 1
    claim_taken_from: str | None = None
    photo: str | None = None  # Dateiname des letzten Fotonachweises
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
            "requires_photo": self.requires_photo,
            "min_age": self.min_age,
            "claim_multiplier": self.claim_multiplier,
            "claim_taken_from": self.claim_taken_from,
            "photo": self.photo,
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
            requires_photo=bool(data.get("requires_photo", False)),
            min_age=int(data.get("min_age", 0)),
            claim_multiplier=int(data.get("claim_multiplier", 1)),
            claim_taken_from=data.get("claim_taken_from"),
            photo=data.get("photo"),
            state=ChoreState(data.get("state", ChoreState.OPEN)),
            claimed_by=data.get("claimed_by"),
            last_completed_by=data.get("last_completed_by"),
            last_completed_at=_parse_dt(data.get("last_completed_at")),
            history=list(data.get("history", [])),
        )


class RedemptionState(StrEnum):
    PENDING = "pending"  # Kind hat eingelöst, Punkte sind schon abgezogen
    APPROVED = "approved"
    REJECTED = "rejected"  # Punkte wurden zurückgegeben


@dataclass
class Reward:
    """Belohnung, die Kinder mit Punkten einlösen. Eltern legen sie selbst fest."""

    id: str
    name: str
    cost: int
    members: list[str] = field(default_factory=list)  # leer = alle Kinder

    def available_for(self, member_id: str) -> bool:
        return not self.members or member_id in self.members

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "name": self.name, "cost": self.cost, "members": list(self.members)}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Reward:
        return cls(
            id=data["id"],
            name=data["name"],
            cost=int(data.get("cost", 0)),
            members=list(data.get("members", [])),
        )


@dataclass
class Redemption:
    id: str
    reward_id: str
    reward_name: str  # bleibt lesbar, auch wenn die Belohnung gelöscht wird
    member_id: str
    cost: int
    requested_at: datetime
    state: RedemptionState = RedemptionState.PENDING
    decided_at: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "reward_id": self.reward_id,
            "reward_name": self.reward_name,
            "member_id": self.member_id,
            "cost": self.cost,
            "requested_at": self.requested_at.isoformat(),
            "state": self.state.value,
            "decided_at": self.decided_at.isoformat() if self.decided_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Redemption:
        return cls(
            id=data["id"],
            reward_id=data["reward_id"],
            reward_name=data.get("reward_name", ""),
            member_id=data["member_id"],
            cost=int(data.get("cost", 0)),
            requested_at=datetime.fromisoformat(data["requested_at"]),
            state=RedemptionState(data.get("state", RedemptionState.PENDING)),
            decided_at=_parse_dt(data.get("decided_at")),
        )


def _parse_dt(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value else None
