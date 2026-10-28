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
        # Welche Geräte wir je Mitglied gesperrt haben. Nur diese geben wir
        # später wieder frei, nie etwas, das jemand anders ausgeschaltet hat.
        self.locked: dict[str, list[str]] = {}

    # -- Speichern -----------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        return {
            "members": [m.to_dict() for m in self.members.values()],
            "chores": [c.to_dict() for c in self.chores.values()],
            "locked": {k: list(v) for k, v in self.locked.items()},
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> Family:
        data = data or {}
        members = {m["id"]: Member.from_dict(m) for m in data.get("members", [])}
        chores = {c["id"]: Chore.from_dict(c) for c in data.get("chores", [])}
        family = cls(members, chores)
        family.locked = {k: list(v) for k, v in data.get("locked", {}).items()}
        return family

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

    def _available(self, member_id: str, now: datetime, min_age: int = 0) -> bool:
        member = self.members.get(member_id)
        return (
            member is not None
            and not member.is_away(now)
            and member.old_enough(min_age, now)
        )

    def _substitute(self, member_id: str, now: datetime, min_age: int = 0) -> str | None:
        member = self.members.get(member_id)
        if member is None or member.substitute_id is None:
            return None
        return (
            member.substitute_id
            if self._available(member.substitute_id, now, min_age)
            else None
        )

    def responsible(self, chore: Chore, now: datetime) -> list[str]:
        """Wer gerade dran ist, mit Abwesenheit und Vertretung.

        Rotation: Wer abwesend ist, wird übersprungen. Sind alle weg, übernimmt
        die Vertretung der Person, die eigentlich dran wäre.
        Ohne Rotation: Abwesende werden durch ihre Vertretung ersetzt.
        Kinder unter dem Mindestalter der Aufgabe sind nie dran.
        Leere Liste heißt: niemand da, die Aufgabe ruht.
        """
        if not chore.assignees:
            return []
        age = chore.min_age
        if chore.rotation:
            count = len(chore.assignees)
            for step in range(count):
                member_id = chore.assignees[(chore.rotation_index + step) % count]
                if self._available(member_id, now, age):
                    return [member_id]
            sub = self._substitute(chore.assignees[chore.rotation_index % count], now, age)
            return [sub] if sub else []
        result = []
        for member_id in chore.assignees:
            member = self.members.get(member_id)
            if member is None or not member.old_enough(age, now):
                continue  # zu jung: die Aufgabe ist (noch) nicht für dieses Kind
            if self._available(member_id, now, age):
                result.append(member_id)
            elif sub := self._substitute(member_id, now, age):
                result.append(sub)
        return list(dict.fromkeys(result))

    def chores_for(self, member_id: str, now: datetime) -> list[Chore]:
        return [
            c for c in self.chores.values() if member_id in self.responsible(c, now)
        ]

    def open_until(self, member_id: str, now: datetime, until: datetime) -> list[Chore]:
        """Offene oder überfällige Aufgaben, die bis `until` fällig sind (für Erinnerungen)."""
        return [
            c
            for c in self.chores_for(member_id, now)
            if c.state in (ChoreState.OPEN, ChoreState.OVERDUE)
            and (c.due is None or c.due <= until)
        ]

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

    def set_age(self, actor: Actor, member_id: str, age: int | None, now: datetime) -> Member:
        """Alter in Jahren setzen (gespeichert als Geburtsjahr). None löscht es."""
        self._require_manager(actor)
        member = self.member(member_id)
        if age is not None and not 0 <= age <= 120:
            raise FamilyError("Bitte ein Alter zwischen 0 und 120 angeben.")
        member.birth_year = None if age is None else now.year - age
        return member

    def remove_member(self, actor: Actor, member_id: str) -> None:
        self._require_manager(actor)
        self.member(member_id)
        del self.members[member_id]
        self.locked.pop(member_id, None)
        for other in self.members.values():
            if other.substitute_id == member_id:
                other.substitute_id = None
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

    def set_absence(
        self,
        actor: Actor,
        member_id: str,
        until: datetime,
        *,
        start: datetime | None = None,
        substitute_id: str | None = None,
    ) -> Member:
        """Abwesenheit eintragen, z. B. Klassenfahrt oder krank."""
        self._require_manager(actor)
        member = self.member(member_id)
        if start is not None and until <= start:
            raise FamilyError("Das Ende muss nach dem Beginn liegen.")
        if substitute_id is not None:
            self.member(substitute_id)
            if substitute_id == member_id:
                raise FamilyError("Niemand kann sich selbst vertreten.")
        member.away_from = start
        member.away_until = until
        member.substitute_id = substitute_id
        return member

    def end_absence(self, actor: Actor, member_id: str) -> Member:
        self._require_manager(actor)
        member = self.member(member_id)
        member.away_from = member.away_until = member.substitute_id = None
        return member

    # -- Konsequenzen ---------------------------------------------------------

    def set_devices(self, actor: Actor, member_id: str, devices: list[str]) -> Member:
        """Freizeitgeräte, deren Internet bei offenen Aufgaben gesperrt wird."""
        self._require_manager(actor)
        member = self.member(member_id)
        if member.role is not Role.CHILD and devices:
            raise FamilyError("Sperren gibt es nur für Kinder.")
        member.devices = list(dict.fromkeys(devices))
        return member

    def grant_pass(self, actor: Actor, member_id: str, until: datetime) -> Member:
        """Freikarte: bis `until` keine Sperre, egal was offen ist."""
        self._require_manager(actor)
        member = self.member(member_id)
        member.pass_until = until
        return member

    def revoke_pass(self, actor: Actor, member_id: str) -> Member:
        self._require_manager(actor)
        member = self.member(member_id)
        member.pass_until = None
        return member

    def should_lock(self, member_id: str, now: datetime) -> bool:
        """Ob die Geräte dieses Kindes gerade gesperrt sein sollen.

        Gesperrt wird nur bei überfälligen Aufgaben. Gemeldete Aufgaben, die
        auf Freigabe warten, zählen nicht: Das Kind hat seinen Teil getan.
        Abwesende und Kinder mit Freikarte werden nie gesperrt.
        """
        member = self.members.get(member_id)
        if (
            member is None
            or member.role is not Role.CHILD
            or not member.devices
            or member.is_away(now)
            or member.has_pass(now)
        ):
            return False
        return any(
            c.state is ChoreState.OVERDUE and member_id in self.responsible(c, now)
            for c in self.chores.values()
        )

    def lock_reasons(self, member_id: str, now: datetime) -> list[Chore]:
        return [
            c
            for c in self.chores.values()
            if c.state is ChoreState.OVERDUE and member_id in self.responsible(c, now)
        ]

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
        requires_photo: bool = False,
        min_age: int = 0,
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
            requires_photo=requires_photo,
            min_age=max(0, min_age),
        )
        self.chores[chore.id] = chore
        return chore

    def update_chore(
        self,
        actor: Actor,
        chore_id: str,
        now: datetime,
        *,
        name: str | None = None,
        assignees: list[str] | None = None,
        points: int | None = None,
        recurrence: Recurrence | None = None,
        due: datetime | None = None,
        clear_due: bool = False,
        rotation: bool | None = None,
        requires_approval: bool | None = None,
        requires_photo: bool | None = None,
        min_age: int | None = None,
    ) -> Chore:
        """Nur übergebene Felder ändern. Punkte und Verlauf bleiben erhalten."""
        self._require_manager(actor)
        chore = self.chore(chore_id)
        if name is not None:
            name = name.strip()
            if not name:
                raise FamilyError("Name fehlt.")
        if assignees is not None:
            if not assignees:
                raise FamilyError("Mindestens eine Person muss zugeordnet sein.")
            for member_id in assignees:
                self.member(member_id)
        if points is not None and points < 0:
            raise FamilyError("Punkte dürfen nicht negativ sein.")
        new_due = None if clear_due else (due if due is not None else chore.due)
        new_recurrence = recurrence if recurrence is not None else chore.recurrence
        if new_recurrence is not Recurrence.NONE and new_due is None:
            raise FamilyError("Wiederkehrende Aufgaben brauchen eine Frist.")

        if name is not None:
            chore.name = name
        if assignees is not None:
            chore.assignees = list(dict.fromkeys(assignees))
            chore.rotation_index %= len(chore.assignees)
        if points is not None:
            chore.points = points
        if rotation is not None:
            chore.rotation = rotation
        if requires_approval is not None:
            chore.requires_approval = requires_approval
        if requires_photo is not None:
            chore.requires_photo = requires_photo
        if min_age is not None:
            chore.min_age = max(0, min_age)
        chore.recurrence = new_recurrence
        chore.due = new_due
        if chore.state is ChoreState.OVERDUE and (chore.due is None or chore.due > now):
            chore.state = ChoreState.OPEN
        if chore.state is ChoreState.DONE and chore.recurrence is not Recurrence.NONE:
            chore.state = ChoreState.OPEN
        if (
            not chore.requires_approval
            and chore.state is ChoreState.CLAIMED
            and chore.claimed_by is not None
        ):
            # Wer schon gemeldet hat, soll durch die Änderung nichts verlieren.
            self._complete(chore, chore.claimed_by, now)
        return chore

    def delete_chore(self, actor: Actor, chore_id: str) -> None:
        self._require_manager(actor)
        self.chore(chore_id)
        del self.chores[chore_id]

    # -- Ablauf --------------------------------------------------------------

    def claim(
        self,
        actor: Actor,
        chore_id: str,
        member_id: str,
        now: datetime,
        *,
        photo: str | None = None,
    ) -> Chore:
        """Kind meldet erledigt. Eltern dürfen für jedes Kind melden.

        Bei Aufgaben mit Fotopflicht brauchen Kinder ein Foto. Eltern und
        Automationen dürfen auch ohne Foto abhaken.
        """
        chore = self.chore(chore_id)
        self.member(member_id)
        if not actor.is_manager:
            if actor.member is None or actor.member.id != member_id:
                raise PermissionDenied("Du kannst nur für dich selbst melden.")
            if member_id not in self.responsible(chore, now):
                raise PermissionDenied("Diese Aufgabe ist gerade nicht deine.")
            if chore.requires_photo and not photo:
                raise FamilyError("Für diese Aufgabe brauchst du ein Foto.")
        self._check_claimable(chore)
        chore.photo = photo  # altes Foto gehört zur letzten Runde
        self._submit(chore, member_id, now, needs_check=not actor.is_manager)
        return chore

    def take_over(
        self,
        actor: Actor,
        chore_id: str,
        member_id: str,
        now: datetime,
        *,
        multiplier: int = 1,
        max_per_day: int = 2,
        day_start: datetime,
        photo: str | None = None,
    ) -> Chore:
        """Geschwister übernimmt eine fremde, offene Aufgabe („wegmopsen“).

        Die Punkte bekommt, wer übernimmt, je nach Uhrzeit mit Faktor. Bei
        Rotation geht es danach so weiter, als hätte der eigentlich
        Zuständige erledigt. Ob das Zeitfenster offen ist, prüft der Aufrufer.
        """
        chore = self.chore(chore_id)
        taker = self.member(member_id)
        if not actor.is_manager and (actor.member is None or actor.member.id != member_id):
            raise PermissionDenied("Du kannst nur für dich selbst übernehmen.")
        if taker.role is not Role.CHILD:
            raise FamilyError("Nur Kinder können Aufgaben übernehmen.")
        if not taker.old_enough(chore.min_age, now):
            raise FamilyError(f"Diese Aufgabe ist erst ab {chore.min_age} Jahren.")
        responsible = self.responsible(chore, now)
        if not responsible or member_id in responsible:
            raise FamilyError("Diese Aufgabe kannst du nicht übernehmen.")
        if chore.requires_photo and not photo and not actor.is_manager:
            raise FamilyError("Für diese Aufgabe brauchst du ein Foto.")
        self._check_claimable(chore)
        taken_today = sum(
            1
            for c in self.chores.values()
            for h in c.history
            if h.get("event") == "taken_over"
            and h.get("member") == member_id
            and datetime.fromisoformat(h["at"]) >= day_start
        )
        if taken_today >= max_per_day:
            raise FamilyError(f"Du hast heute schon {max_per_day} Aufgaben übernommen.")

        chore.claim_multiplier = max(1, multiplier)
        chore.claim_taken_from = responsible[0]
        chore.photo = photo  # altes Foto gehört zur letzten Runde
        self._log(chore, "taken_over", member_id, now)
        self._submit(chore, member_id, now, needs_check=not actor.is_manager)
        return chore

    @staticmethod
    def _check_claimable(chore: Chore) -> None:
        if chore.state is ChoreState.DONE:
            raise FamilyError("Die Aufgabe ist schon erledigt.")
        if chore.state is ChoreState.CLAIMED:
            raise FamilyError("Die Aufgabe wartet schon auf Freigabe.")

    def _submit(self, chore: Chore, member_id: str, now: datetime, *, needs_check: bool) -> None:
        if chore.requires_approval and needs_check:
            chore.state = ChoreState.CLAIMED
            chore.claimed_by = member_id
            self._log(chore, "claimed", member_id, now)
        else:
            self._complete(chore, member_id, now)

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
        self._reset_claim(chore)
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
        self._reset_claim(chore)
        chore.state = (
            ChoreState.OVERDUE if chore.due and chore.due < now else ChoreState.OPEN
        )
        return chore

    def refresh(self, now: datetime) -> bool:
        """Fristen und Abwesenheiten nachführen. True, wenn sich etwas geändert hat.

        Offene Aufgaben mit abgelaufener Frist werden überfällig, außer niemand
        ist da (alle abwesend ohne Vertretung). Abgelaufene Abwesenheiten
        werden gelöscht.
        """
        changed = False
        for member in self.members.values():
            if member.away_until is not None and now >= member.away_until:
                member.away_from = member.away_until = member.substitute_id = None
                changed = True
            if member.pass_until is not None and now >= member.pass_until:
                member.pass_until = None
                changed = True
        for chore in self.chores.values():
            if (
                chore.state is ChoreState.OPEN
                and chore.due
                and chore.due < now
                and self.responsible(chore, now)
            ):
                chore.state = ChoreState.OVERDUE
                changed = True
        return changed

    # -- intern --------------------------------------------------------------

    def _complete(self, chore: Chore, member_id: str, now: datetime) -> None:
        self.member(member_id).points += chore.points * chore.claim_multiplier
        chore.last_completed_by = member_id
        chore.last_completed_at = now
        chore.claimed_by = None
        # Bei Übernahme rotiert es weiter, als hätte der Zuständige erledigt.
        rotate_from = chore.claim_taken_from or member_id
        self._reset_claim(chore)
        self._log(chore, "completed", member_id, now)

        if chore.recurrence is Recurrence.NONE:
            chore.state = ChoreState.DONE
            return
        chore.due = _next_due(chore.due, chore.recurrence, now)
        if chore.rotation and chore.assignees:
            # Nach der Person weiter, die dran war bzw. erledigt hat. So zählt
            # auch ein Einspringen bei Abwesenheit als Runde.
            start = (
                chore.assignees.index(rotate_from)
                if rotate_from in chore.assignees
                else chore.rotation_index
            )
            chore.rotation_index = (start + 1) % len(chore.assignees)
        chore.state = ChoreState.OPEN

    @staticmethod
    def _reset_claim(chore: Chore) -> None:
        chore.claim_multiplier = 1
        chore.claim_taken_from = None

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
