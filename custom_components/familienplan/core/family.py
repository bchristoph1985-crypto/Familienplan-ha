"""Regeln des Aufgaben-Kerns: Melden, Freigeben, Wiederholen, Rotieren, Rechte.

Jede Änderung läuft über eine Methode von `Family` und bekommt einen `Actor`.
Die Rechte werden hier geprüft, also serverseitig, bevor sich etwas ändert.
Es gibt keinen Wächter, der hinterher zurücksetzt.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from .models import Chore, ChoreState, Member, Recurrence, Role

HISTORY_LIMIT = 50

_INTERVALS = {
    Recurrence.DAILY: timedelta(days=1),
    Recurrence.WEEKLY: timedelta(weeks=1),
    Recurrence.BIWEEKLY: timedelta(weeks=2),
}


class FamilyError(Exception):
    """Grund, warum eine Aktion nicht ausgeführt wurde."""


class PermissionDenied(FamilyError):
    """Der Aufrufer darf diese Aktion nicht ausführen."""


@dataclass(frozen=True)
class Actor:
    """Wer eine Aktion auslöst.

    system: Aufruf ohne Benutzer, z. B. aus einer Automation. Kinderkonten
    können in HA keine Automationen anlegen, deshalb ist das vertrauenswürdig.
    """

    member: Member | None = None
    is_admin: bool = False
    system: bool = False

    @property
    def is_manager(self) -> bool:
        return (
            self.system
            or self.is_admin
            or (self.member is not None and self.member.role is Role.PARENT)
        )


SYSTEM = Actor(system=True)


class Family:
    def __init__(
        self,
        members: dict[str, Member] | None = None,
        chores: dict[str, Chore] | None = None,
    ) -> None:
        self.members: dict[str, Member] = members or {}
        self.chores: dict[str, Chore] = chores or {}

    # -- Speichern -----------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        return {
            "members": [m.to_dict() for m in self.members.values()],
            "chores": [c.to_dict() for c in self.chores.values()],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> Family:
        data = data or {}
        members = {m["id"]: Member.from_dict(m) for m in data.get("members", [])}
        chores = {c["id"]: Chore.from_dict(c) for c in data.get("chores", [])}
        return cls(members, chores)

    # -- Hilfen --------------------------------------------------------------

    def actor_for_user(self, user_id: str | None, *, is_admin: bool) -> Actor:
        if user_id is None:
            return SYSTEM
        member = next(
            (m for m in self.members.values() if m.user_id == user_id), None
        )
        return Actor(member=member, is_admin=is_admin)

    def member(self, member_id: str) -> Member:
        try:
            return self.members[member_id]
        except KeyError:
            raise FamilyError(f"Unbekanntes Familienmitglied: {member_id}") from None

    def chore(self, chore_id: str) -> Chore:
        try:
            return self.chores[chore_id]
        except KeyError:
            raise FamilyError(f"Unbekannte Aufgabe: {chore_id}") from None

    @staticmethod
    def responsible(chore: Chore) -> list[str]:
        """Wer gerade dran ist. Bei Rotation genau eine Person."""
        if not chore.assignees:
            return []
        if chore.rotation:
            return [chore.assignees[chore.rotation_index % len(chore.assignees)]]
        return list(chore.assignees)

    def chores_for(self, member_id: str) -> list[Chore]:
        return [c for c in self.chores.values() if member_id in self.responsible(c)]

    @staticmethod
    def _require_manager(actor: Actor) -> None:
        if not actor.is_manager:
            raise PermissionDenied("Nur Eltern dürfen das.")

    # -- Familienmitglieder --------------------------------------------------

    def add_member(
        self,
        actor: Actor,
        name: str,
        role: Role,
        user_id: str | None = None,
        notify_service: str | None = None,
    ) -> Member:
        self._require_manager(actor)
        name = name.strip()
        if not name:
            raise FamilyError("Name fehlt.")
        if user_id and any(m.user_id == user_id for m in self.members.values()):
            raise FamilyError("Dieses HA-Konto gehört schon zu einem Mitglied.")
        member = Member(uuid.uuid4().hex, name, role, user_id, notify_service)
        self.members[member.id] = member
        return member

    def remove_member(self, actor: Actor, member_id: str) -> None:
        self._require_manager(actor)
        self.member(member_id)
        del self.members[member_id]
        for chore in self.chores.values():
            if member_id in chore.assignees:
                chore.assignees.remove(member_id)
                if chore.assignees:
                    chore.rotation_index %= len(chore.assignees)
                else:
                    chore.rotation_index = 0
            if chore.claimed_by == member_id:
                chore.claimed_by = None
                chore.state = ChoreState.OPEN

    # -- Aufgaben verwalten --------------------------------------------------

    def create_chore(
        self,
        actor: Actor,
        name: str,
        assignees: list[str],
        *,
        points: int = 1,
        recurrence: Recurrence = Recurrence.NONE,
        due: datetime | None = None,
        rotation: bool = False,
        requires_approval: bool = False,
    ) -> Chore:
        self._require_manager(actor)
        name = name.strip()
        if not name:
            raise FamilyError("Name fehlt.")
        if not assignees:
            raise FamilyError("Mindestens eine Person muss zugeordnet sein.")
        for member_id in assignees:
            self.member(member_id)
        if points < 0:
            raise FamilyError("Punkte dürfen nicht negativ sein.")
        if recurrence is not Recurrence.NONE and due is None:
            raise FamilyError("Wiederkehrende Aufgaben brauchen eine erste Frist.")
        chore = Chore(
            id=uuid.uuid4().hex,
            name=name,
            assignees=list(dict.fromkeys(assignees)),
            points=points,
            recurrence=recurrence,
            due=due,
            rotation=rotation,
            requires_approval=requires_approval,
        )
        self.chores[chore.id] = chore
        return chore

    def delete_chore(self, actor: Actor, chore_id: str) -> None:
        self._require_manager(actor)
        self.chore(chore_id)
        del self.chores[chore_id]

    # -- Ablauf --------------------------------------------------------------

    def claim(
        self, actor: Actor, chore_id: str, member_id: str, now: datetime
    ) -> Chore:
        """Kind meldet erledigt. Eltern dürfen für jedes Kind melden."""
        chore = self.chore(chore_id)
        self.member(member_id)
        if not actor.is_manager:
            if actor.member is None or actor.member.id != member_id:
                raise PermissionDenied("Du kannst nur für dich selbst melden.")
            if member_id not in self.responsible(chore):
                raise PermissionDenied("Diese Aufgabe ist gerade nicht deine.")
        if chore.state is ChoreState.DONE:
            raise FamilyError("Die Aufgabe ist schon erledigt.")
        if chore.state is ChoreState.CLAIMED:
            raise FamilyError("Die Aufgabe wartet schon auf Freigabe.")

        if chore.requires_approval and not actor.is_manager:
            chore.state = ChoreState.CLAIMED
            chore.claimed_by = member_id
            self._log(chore, "claimed", member_id, now)
            return chore
        self._complete(chore, member_id, now)
        return chore

    def undo_claim(self, actor: Actor, chore_id: str) -> Chore:
        chore = self.chore(chore_id)
        if chore.state is not ChoreState.CLAIMED:
            raise FamilyError("Es gibt keine offene Meldung.")
        if not actor.is_manager and (
            actor.member is None or actor.member.id != chore.claimed_by
        ):
            raise PermissionDenied("Nur die eigene Meldung lässt sich zurücknehmen.")
        chore.state = ChoreState.OPEN
        chore.claimed_by = None
        return chore

    def approve(self, actor: Actor, chore_id: str, now: datetime) -> Chore:
        self._require_manager(actor)
        chore = self.chore(chore_id)
        if chore.state is not ChoreState.CLAIMED or chore.claimed_by is None:
            raise FamilyError("Es gibt nichts freizugeben.")
        self._complete(chore, chore.claimed_by, now)
        return chore

    def reject(self, actor: Actor, chore_id: str, now: datetime) -> Chore:
        self._require_manager(actor)
        chore = self.chore(chore_id)
        if chore.state is not ChoreState.CLAIMED:
            raise FamilyError("Es gibt nichts abzulehnen.")
        self._log(chore, "rejected", chore.claimed_by, now)
        chore.claimed_by = None
        chore.state = (
            ChoreState.OVERDUE if chore.due and chore.due < now else ChoreState.OPEN
        )
        return chore

    def refresh(self, now: datetime) -> list[Chore]:
        """Markiert offene Aufgaben mit abgelaufener Frist als überfällig."""
        changed = []
        for chore in self.chores.values():
            if chore.state is ChoreState.OPEN and chore.due and chore.due < now:
                chore.state = ChoreState.OVERDUE
                changed.append(chore)
        return changed

    # -- intern --------------------------------------------------------------

    def _complete(self, chore: Chore, member_id: str, now: datetime) -> None:
        self.member(member_id).points += chore.points
        chore.last_completed_by = member_id
        chore.last_completed_at = now
        chore.claimed_by = None
        self._log(chore, "completed", member_id, now)

        if chore.recurrence is Recurrence.NONE:
            chore.state = ChoreState.DONE
            return
        chore.due = _next_due(chore.due, chore.recurrence, now)
        if chore.rotation and chore.assignees:
            chore.rotation_index = (chore.rotation_index + 1) % len(chore.assignees)
        chore.state = ChoreState.OPEN

    @staticmethod
    def _log(chore: Chore, event: str, member_id: str | None, now: datetime) -> None:
        chore.history.append(
            {"event": event, "member": member_id, "at": now.isoformat()}
        )
        del chore.history[:-HISTORY_LIMIT]


def _next_due(due: datetime | None, recurrence: Recurrence, now: datetime) -> datetime:
    """Nächste Frist nach `now`, im festen Takt der ersten Frist.

    Wer eine Aufgabe zu spät erledigt, bekommt keine Frist in der
    Vergangenheit, und der Wochentag bzw. die Uhrzeit bleiben gleich.
    """
    step = _INTERVALS[recurrence]
    base = due or now
    nxt = base + step
    while nxt <= now:
        nxt += step
    return nxt
