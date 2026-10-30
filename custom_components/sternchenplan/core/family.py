"""Regeln des Aufgaben-Kerns: Melden, Freigeben, Wiederholen, Rotieren, Rechte.

Jede Änderung läuft über eine Methode von `Family` und bekommt einen `Actor`.
Die Rechte werden hier geprüft, also serverseitig, bevor sich etwas ändert.
Es gibt keinen Wächter, der hinterher zurücksetzt.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta, tzinfo
from difflib import SequenceMatcher
from typing import Any

from .extras import ExtrasMixin
from .models import (
    Chore,
    ChoreState,
    FamilyGoal,
    Member,
    Recurrence,
    Redemption,
    RedemptionState,
    Reward,
    Role,
)
from .progress import EARLY_HOUR, level_for, new_badges

HISTORY_LIMIT = 50
MONEY_LOG_LIMIT = 200
MAX_STEPS = 12
REDEMPTION_LIMIT = 100
STAR_LOG_LIMIT = 200
MAX_PRESETS = 12
# Vorschläge für Bonus und Abzug, Eltern können sie ändern
# Designs zum Aussuchen; „“ ist das klare Standard-Design.
THEMES = ("", "space", "jungle", "ocean", "candy", "elegant")

DEFAULT_PRESETS = (
    ("Extra geholfen", 3),
    ("Besonders lieb", 2),
    ("Nicht gehört", -1),
    ("Streit", -2),
)

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
    # Gemeinsames Familientablet: Kinder ohne eigenes Handy tippen dort ihren
    # Namen an. Das Tablet darf für jedes Kind handeln, aber nur so viel wie
    # das Kind selbst.
    tablet: bool = False

    @property
    def is_manager(self) -> bool:
        return (
            self.system
            or self.is_admin
            or (self.member is not None and self.member.role is Role.PARENT)
        )


SYSTEM = Actor(system=True)


class Family(ExtrasMixin):
    _error = staticmethod(FamilyError)
    _denied = staticmethod(PermissionDenied)

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
        self.rewards: dict[str, Reward] = {}
        self.redemptions: list[Redemption] = []
        # Schaltet den Fotonachweis familienweit ab. Ohne gilt jede Aufgabe als
        # ohne Fotopflicht, die Einstellung an der Aufgabe bleibt aber erhalten.
        self.photo_proof = True
        # HA-Konten der Familientablets und ob dort Abgehaktes von Eltern
        # bestätigt werden muss.
        self.tablet_users: list[str] = []
        self.tablet_approval = False
        # Zeitzone für Serien und „Frühaufsteher“. Home Assistant setzt sie.
        self.tz: tzinfo = UTC
        # Level und Abzeichen, die seit dem letzten Abholen neu sind. Wird nicht
        # gespeichert. Home Assistant feiert damit (Push, Ereignis).
        self.events: list[dict[str, Any]] = []
        self.goal: FamilyGoal | None = None
        # Taschengeld: Sterne pro Euro (0 = kein Tausch), Zahltag (0 = Montag)
        self.money_rate = 0
        self.payday = 6
        self.money_log: list[dict[str, Any]] = []
        # Ferien-Pause für alle: nichts ist fällig, nichts wird gesperrt
        self.pause_from: datetime | None = None
        self.pause_until: datetime | None = None
        # Wetter: welche HA-Wetter-Entität zählt und ob es gerade nass ist.
        # bad_weather setzt Home Assistant laufend, es wird nicht gespeichert.
        self.weather_entity: str | None = None
        self.bad_weather = False
        # Wochenbericht an die Eltern: Wochentag (0 = Montag, -1 = aus) und Stunde
        self.report_day = 6
        self.report_hour = 18
        # Bonus und Abzug: Verlauf und Vorschläge
        self.star_log: list[dict[str, Any]] = []
        self.presets: list[dict[str, Any]] = [
            {"id": uuid.uuid4().hex[:8], "name": n, "stars": s} for n, s in DEFAULT_PRESETS
        ]
        self._init_extras()

    # -- Speichern -----------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        return {
            "members": [m.to_dict() for m in self.members.values()],
            "chores": [c.to_dict() for c in self.chores.values()],
            "locked": {k: list(v) for k, v in self.locked.items()},
            "rewards": [r.to_dict() for r in self.rewards.values()],
            "redemptions": [r.to_dict() for r in self.redemptions],
            "tablet_users": list(self.tablet_users),
            "tablet_approval": self.tablet_approval,
            "goal": self.goal.to_dict() if self.goal else None,
            "money_rate": self.money_rate,
            "payday": self.payday,
            "money_log": list(self.money_log),
            "pause_from": self.pause_from.isoformat() if self.pause_from else None,
            "pause_until": self.pause_until.isoformat() if self.pause_until else None,
            "weather_entity": self.weather_entity,
            "report_day": self.report_day,
            "report_hour": self.report_hour,
            "star_log": list(self.star_log),
            "presets": [dict(p) for p in self.presets],
            **self._extras_to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> Family:
        data = data or {}
        members = {m["id"]: Member.from_dict(m) for m in data.get("members", [])}
        chores = {c["id"]: Chore.from_dict(c) for c in data.get("chores", [])}
        family = cls(members, chores)
        family.locked = {k: list(v) for k, v in data.get("locked", {}).items()}
        family.rewards = {r["id"]: Reward.from_dict(r) for r in data.get("rewards", [])}
        family.redemptions = [Redemption.from_dict(r) for r in data.get("redemptions", [])]
        family.tablet_users = list(data.get("tablet_users", []))
        family.tablet_approval = bool(data.get("tablet_approval", False))
        if data.get("goal"):
            family.goal = FamilyGoal.from_dict(data["goal"])
        family.money_rate = int(data.get("money_rate", 0))
        family.payday = int(data.get("payday", 6))
        family.money_log = list(data.get("money_log", []))
        if data.get("pause_until"):
            family.pause_until = datetime.fromisoformat(data["pause_until"])
            family.pause_from = datetime.fromisoformat(data["pause_from"])
        family.weather_entity = data.get("weather_entity")
        family.report_day = int(data.get("report_day", 6))
        family.report_hour = int(data.get("report_hour", 18))
        family.star_log = list(data.get("star_log", []))
        if "presets" in data:
            family.presets = [dict(p) for p in data["presets"]]
        family._extras_from_dict(data)
        for raw in data.get("members", []):
            if "progress" not in raw:
                family._estimate_progress(family.members[raw["id"]])
        return family

    def _estimate_progress(self, member: Member) -> None:
        """Stand vor 0.16: Fortschritt aus Punkten und Verlauf schätzen.

        Abzeichen gibt es dabei still, ohne Feier, damit nach dem Update nicht
        alle auf einmal aufpoppen.
        """
        progress = member.progress
        spent = sum(
            r.cost for r in self.redemptions
            if r.member_id == member.id and r.state is not RedemptionState.REJECTED
        )
        progress.earned = max(0, member.points) + spent
        progress.redeemed = sum(1 for r in self.redemptions if r.member_id == member.id)
        for chore in self.chores.values():
            for entry in chore.history:
                if entry.get("member") != member.id:
                    continue
                if entry.get("event") == "completed":
                    progress.done += 1
                elif entry.get("event") == "taken_over":
                    progress.taken_over += 1
        new_badges(progress, datetime.now(UTC))

    def pop_events(self) -> list[dict[str, Any]]:
        events, self.events = self.events, []
        return events

    # -- Hilfen --------------------------------------------------------------

    def actor_for_user(self, user_id: str | None, *, is_admin: bool) -> Actor:
        if user_id is None:
            return SYSTEM
        member = next(
            (m for m in self.members.values() if m.user_id == user_id), None
        )
        if member is None and user_id in self.tablet_users:
            return Actor(is_admin=is_admin, tablet=True)
        return Actor(member=member, is_admin=is_admin)

    def _as_child(self, actor: Actor, member_id: str | None) -> Actor:
        """Am Familientablet handelt das Tablet als das gewählte Kind."""
        if not actor.tablet or actor.is_manager:
            return actor
        member = self.member(member_id) if member_id else None
        if member is None or member.role is not Role.CHILD:
            raise PermissionDenied("Am Familientablet bitte ein Kind auswählen.")
        return Actor(member=member, tablet=True)

    def set_tablet(self, actor: Actor, user_ids: list[str], *, approval: bool) -> None:
        """Familientablets festlegen. Konten von Familienmitgliedern gehen nicht."""
        self._require_manager(actor)
        taken = {m.user_id for m in self.members.values() if m.user_id}
        if taken & set(user_ids):
            raise FamilyError("Ein Familienmitglied kann nicht das Familientablet sein.")
        self.tablet_users = list(dict.fromkeys(user_ids))
        self.tablet_approval = approval

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
        if not chore.assignees or self.is_paused(now):
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
        if user_id in self.tablet_users:
            # Wer Mitglied wird, ist nicht mehr das Familientablet.
            self.tablet_users.remove(user_id)
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

    def remove_member(self, actor: Actor, member_id: str) -> list[str]:
        """Person und alle ihre Spuren löschen. Gibt Fotos zurück, die weg müssen."""
        self._require_manager(actor)
        self.member(member_id)
        photos = self._purge(member_id)
        del self.members[member_id]
        self.locked.pop(member_id, None)
        for reward in list(self.rewards.values()):
            if member_id in reward.members:
                reward.members.remove(member_id)
                if not reward.members:
                    # War nur für dieses Kind gedacht, nicht plötzlich für alle.
                    del self.rewards[reward.id]
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
        return photos

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
        steps: list[str] | None = None,
        weekdays: list[int] | None = None,
        icon: str = "",
        outdoor: bool = False,
        house: dict[str, str] | None = None,
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
        if recurrence not in (Recurrence.NONE, Recurrence.ON_DEMAND) and due is None:
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
            steps=_clean_steps(steps),
            weekdays=_clean_weekdays(weekdays),
            icon=icon.strip()[:8],
            outdoor=outdoor,
        )
        _set_house(chore, house or {})
        chore.due = self._allowed_day(chore, chore.due)
        if recurrence is Recurrence.ON_DEMAND:
            # Ruht, bis ein Gerät oder die Eltern sie fällig machen
            chore.state, chore.due = ChoreState.DONE, None
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
        steps: list[str] | None = None,
        weekdays: list[int] | None = None,
        icon: str | None = None,
        outdoor: bool | None = None,
        house: dict[str, str] | None = None,
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
        if new_recurrence not in (Recurrence.NONE, Recurrence.ON_DEMAND) and new_due is None:
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
        if steps is not None:
            new_steps = _clean_steps(steps)
            if new_steps != chore.steps:
                chore.steps = new_steps
                chore.steps_done = []
        if weekdays is not None:
            chore.weekdays = _clean_weekdays(weekdays)
        if icon is not None:
            chore.icon = icon.strip()[:8]
        if house:
            _set_house(chore, house)
        if outdoor is not None:
            chore.outdoor = outdoor
            if not outdoor:
                chore.weather_shift = 0
        chore.recurrence = new_recurrence
        chore.due = self._allowed_day(chore, new_due)
        if chore.state is ChoreState.OVERDUE and (chore.due is None or chore.due > now):
            chore.state = ChoreState.OPEN
        if chore.state is ChoreState.DONE and chore.recurrence not in (
            Recurrence.NONE, Recurrence.ON_DEMAND
        ):
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
        actor = self._as_child(actor, member_id)
        if not actor.is_manager:
            if actor.member is None or actor.member.id != member_id:
                raise PermissionDenied("Du kannst nur für dich selbst melden.")
            if member_id not in self.responsible(chore, now):
                raise PermissionDenied("Diese Aufgabe ist gerade nicht deine.")
            if self.needs_photo(chore) and not photo:
                raise FamilyError("Für diese Aufgabe brauchst du ein Foto.")
        self._check_claimable(chore)
        chore.photo = photo  # altes Foto gehört zur letzten Runde
        if photo:
            self._keep_photo(chore, member_id, now, photo)
        self._submit(chore, member_id, now, needs_check=self._needs_check(actor, chore))
        return chore

    def check_step(
        self, actor: Actor, chore_id: str, member_id: str, index: int, done: bool, now: datetime
    ) -> Chore:
        """Einen Schritt einer Routine abhaken. Sind alle erledigt, gilt die Aufgabe
        als gemeldet, außer sie braucht ein Foto: dann tippt das Kind selbst."""
        chore = self.chore(chore_id)
        self.member(member_id)
        actor = self._as_child(actor, member_id)
        if not actor.is_manager:
            if actor.member is None or actor.member.id != member_id:
                raise PermissionDenied("Du kannst nur für dich selbst abhaken.")
            if member_id not in self.responsible(chore, now):
                raise PermissionDenied("Diese Aufgabe ist gerade nicht deine.")
        if not 0 <= index < len(chore.steps):
            raise FamilyError("Diesen Schritt gibt es nicht.")
        self._check_claimable(chore)
        marked = set(chore.steps_done)
        marked.add(index) if done else marked.discard(index)
        chore.steps_done = sorted(marked)
        if len(chore.steps_done) == len(chore.steps) and not (
            self.needs_photo(chore) and not actor.is_manager
        ):
            self.claim(actor, chore_id, member_id, now)
        return chore

    def needs_photo(self, chore: Chore) -> bool:
        return chore.requires_photo and self.photo_proof

    def _needs_check(self, actor: Actor, chore: Chore) -> bool:
        """Eltern prüfen, wenn die Aufgabe Freigabe braucht oder ein Foto dabei ist.

        Ein Fotonachweis, den niemand ansieht, wäre sinnlos. Darum gehen
        Fotos von Kindern immer zur Bestätigung an die Eltern.
        """
        if actor.is_manager:
            return False
        if actor.tablet and self.tablet_approval:
            return True
        return chore.requires_approval or (chore.requires_photo and chore.photo is not None)

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
        actor = self._as_child(actor, member_id)
        if not actor.is_manager and (actor.member is None or actor.member.id != member_id):
            raise PermissionDenied("Du kannst nur für dich selbst übernehmen.")
        if taker.role is not Role.CHILD:
            raise FamilyError("Nur Kinder können Aufgaben übernehmen.")
        if not taker.old_enough(chore.min_age, now):
            raise FamilyError(f"Diese Aufgabe ist erst ab {chore.min_age} Jahren.")
        responsible = self.responsible(chore, now)
        if not responsible or member_id in responsible:
            raise FamilyError("Diese Aufgabe kannst du nicht übernehmen.")
        if self.needs_photo(chore) and not photo and not actor.is_manager:
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
        if photo:
            self._keep_photo(chore, member_id, now, photo)
        self._log(chore, "taken_over", member_id, now)
        self._submit(chore, member_id, now, needs_check=self._needs_check(actor, chore))
        return chore

    @staticmethod
    def _check_claimable(chore: Chore) -> None:
        if chore.state is ChoreState.DONE:
            raise FamilyError("Die Aufgabe ist schon erledigt.")
        if chore.state is ChoreState.CLAIMED:
            raise FamilyError("Die Aufgabe wartet schon auf Freigabe.")

    def _submit(self, chore: Chore, member_id: str, now: datetime, *, needs_check: bool) -> None:
        if needs_check:
            chore.state = ChoreState.CLAIMED
            chore.claimed_by = member_id
            self._log(chore, "claimed", member_id, now)
            self.events.append(
                {"type": "needs_approval", "member": member_id, "chore": chore.id,
                 "name": chore.name}
            )
        else:
            self._complete(chore, member_id, now)

    def undo_claim(self, actor: Actor, chore_id: str) -> Chore:
        chore = self.chore(chore_id)
        if chore.state is not ChoreState.CLAIMED:
            raise FamilyError("Es gibt keine offene Meldung.")
        actor = self._as_child(actor, chore.claimed_by)
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
        chore.steps_done = []
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
        changed = self._end_pause_if_over(now)
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
                if chore.outdoor and self.bad_weather:
                    self._postpone(chore, now)
                else:
                    chore.state = ChoreState.OVERDUE
                    for member_id in self.responsible(chore, now):
                        self._log(chore, "missed", member_id, now)
                        self.events.append({"type": "overdue", "member": member_id, "chore": chore.id})
                changed = True
        if self.pay_allowances(now):
            changed = True
        if self._refresh_screen(now):
            changed = True
        if self._refresh_vote(now):
            changed = True
        return changed

    # -- Belohnungen -----------------------------------------------------------

    def reward(self, reward_id: str) -> Reward:
        try:
            return self.rewards[reward_id]
        except KeyError:
            raise FamilyError("Unbekannte Belohnung.") from None

    def _check_reward(self, name: str, cost: int, members: list[str]) -> str:
        name = name.strip()
        if not name:
            raise FamilyError("Name fehlt.")
        if cost < 1:
            raise FamilyError("Eine Belohnung kostet mindestens 1 Punkt.")
        for member_id in members:
            if self.member(member_id).role is not Role.CHILD:
                raise FamilyError("Belohnungen gibt es nur für Kinder.")
        return name

    def create_reward(
        self, actor: Actor, name: str, cost: int, members: list[str] | None = None
    ) -> Reward:
        self._require_manager(actor)
        members = list(dict.fromkeys(members or []))
        name = self._check_reward(name, cost, members)
        reward = Reward(uuid.uuid4().hex, name, cost, members)
        self.rewards[reward.id] = reward
        return reward

    def update_reward(
        self,
        actor: Actor,
        reward_id: str,
        *,
        name: str | None = None,
        cost: int | None = None,
        members: list[str] | None = None,
    ) -> Reward:
        self._require_manager(actor)
        reward = self.reward(reward_id)
        new_members = list(dict.fromkeys(members)) if members is not None else reward.members
        new_name = self._check_reward(
            name if name is not None else reward.name,
            cost if cost is not None else reward.cost,
            new_members,
        )
        reward.name = new_name
        if cost is not None:
            reward.cost = cost
        reward.members = new_members
        return reward

    def delete_reward(self, actor: Actor, reward_id: str) -> None:
        """Offene Einlösungen bleiben bestehen und können noch entschieden werden."""
        self._require_manager(actor)
        self.reward(reward_id)
        del self.rewards[reward_id]
        for member in self.members.values():
            if member.goal_reward_id == reward_id:
                member.goal_reward_id = None

    def redeem(self, actor: Actor, reward_id: str, member_id: str, now: datetime) -> Redemption:
        """Kind löst ein. Die Punkte werden sofort abgezogen, Eltern bestätigen."""
        reward = self.reward(reward_id)
        member = self.member(member_id)
        actor = self._as_child(actor, member_id)
        if not actor.is_manager and (actor.member is None or actor.member.id != member_id):
            raise PermissionDenied("Du kannst nur für dich selbst einlösen.")
        if member.role is not Role.CHILD or not reward.available_for(member_id):
            raise FamilyError("Diese Belohnung gibt es für dich nicht.")
        if member.points < reward.cost:
            raise FamilyError(
                f"Dafür brauchst du {reward.cost} Punkte, du hast {member.points}."
            )
        member.points -= reward.cost
        member.progress.redeemed += 1
        if member.goal_reward_id == reward.id:
            member.goal_reward_id = None
        self._celebrate(member, now)
        redemption = Redemption(
            uuid.uuid4().hex, reward.id, reward.name, member_id, reward.cost, now
        )
        self.redemptions.append(redemption)
        self._trim_redemptions()
        self.events.append(
            {"type": "redeemed", "member": member_id, "redemption": redemption.id,
             "reward": reward.name}
        )
        return redemption

    def _redemption(self, redemption_id: str) -> Redemption:
        for redemption in self.redemptions:
            if redemption.id == redemption_id:
                if redemption.state is not RedemptionState.PENDING:
                    raise FamilyError("Darüber wurde schon entschieden.")
                return redemption
        raise FamilyError("Unbekannte Einlösung.")

    def approve_redemption(self, actor: Actor, redemption_id: str, now: datetime) -> Redemption:
        self._require_manager(actor)
        redemption = self._redemption(redemption_id)
        redemption.state = RedemptionState.APPROVED
        redemption.decided_at = now
        return redemption

    def reject_redemption(self, actor: Actor, redemption_id: str, now: datetime) -> Redemption:
        """Ablehnen gibt die Punkte zurück. Das Kind kann auch selbst zurücknehmen."""
        redemption = self._redemption(redemption_id)
        actor = self._as_child(actor, redemption.member_id)
        if not actor.is_manager and (
            actor.member is None or actor.member.id != redemption.member_id
        ):
            raise PermissionDenied("Nur Eltern dürfen das.")
        redemption.state = RedemptionState.REJECTED
        redemption.decided_at = now
        if redemption.member_id in self.members:
            self.members[redemption.member_id].points += redemption.cost
        return redemption

    def pending_redemptions(self) -> list[Redemption]:
        return [r for r in self.redemptions if r.state is RedemptionState.PENDING]

    def _trim_redemptions(self) -> None:
        # Offene nie wegwerfen, nur alte entschiedene.
        done = [r for r in self.redemptions if r.state is not RedemptionState.PENDING]
        excess = len(self.redemptions) - REDEMPTION_LIMIT
        for old in done[: max(0, excess)]:
            self.redemptions.remove(old)

    # -- intern --------------------------------------------------------------

    def _complete(self, chore: Chore, member_id: str, now: datetime) -> None:
        member = self.member(member_id)
        earned = chore.points * chore.claim_multiplier
        member.points += earned
        self._count(member, chore, earned, now)
        chore.last_completed_by = member_id
        chore.last_completed_at = now
        chore.claimed_by = None
        chore.steps_done = []
        # Bei Übernahme rotiert es weiter, als hätte der Zuständige erledigt.
        rotate_from = chore.claim_taken_from or member_id
        self._reset_claim(chore)
        self._log(chore, "completed", member_id, now, points=earned)
        self._finish(chore, rotate_from, now)
        self._check_all_done(member, now)

    def _finish(self, chore: Chore, rotate_from: str, now: datetime) -> None:
        """Nächste Runde vorbereiten: Frist, Reihum, Zustand."""
        if chore.recurrence is Recurrence.NONE:
            chore.state = ChoreState.DONE
            chore.weather_shift = 0
            return
        if chore.recurrence is Recurrence.ON_DEMAND:
            chore.state, chore.due, chore.weather_shift = ChoreState.DONE, None, 0
            self._rotate(chore, rotate_from)
            return
        # Wegen Regen verschoben: der Takt richtet sich weiter nach der alten Frist.
        base = chore.due - timedelta(days=chore.weather_shift) if chore.due else None
        chore.weather_shift = 0
        chore.due = self._allowed_day(chore, _next_due(base, chore.recurrence, now))
        self._rotate(chore, rotate_from)
        chore.state = ChoreState.OPEN

    @staticmethod
    def _rotate(chore: Chore, rotate_from: str) -> None:
        if chore.rotation and chore.assignees:
            # Nach der Person weiter, die dran war bzw. erledigt hat. So zählt
            # auch ein Einspringen bei Abwesenheit als Runde.
            start = (
                chore.assignees.index(rotate_from)
                if rotate_from in chore.assignees
                else chore.rotation_index
            )
            chore.rotation_index = (start + 1) % len(chore.assignees)

    def _count(self, member: Member, chore: Chore, earned: int, now: datetime) -> None:
        """Fortschritt nachführen. Läuft vor dem Zurücksetzen der Übernahme."""
        progress = member.progress
        local = now.astimezone(self.tz)
        progress.earned += max(0, earned)
        progress.done += 1
        if chore.claim_taken_from:
            progress.taken_over += 1
        if chore.photo:
            progress.photos += 1
        if local.hour < EARLY_HOUR:
            progress.early += 1
        progress.count_day(local.date())
        self._goal_step(member, earned, now)
        self._celebrate(member, now, level_before=level_for(progress.earned - max(0, earned)))

    def _goal_step(self, member: Member, earned: int, now: datetime) -> None:
        goal = self.goal
        counts = member.role is Role.CHILD or (self.has("parents") and member.role is Role.PARENT)
        if goal and goal.reached_at is None and counts and earned > 0:
            goal.progress = min(goal.target, goal.progress + earned)
            if goal.progress >= goal.target:
                goal.reached_at = now
                self.events.append({"type": "family_goal", "name": goal.name})
        reward = self.rewards.get(member.goal_reward_id or "")
        if reward and member.points < reward.cost:
            member.goal_ready_told = False
        elif reward and not member.goal_ready_told:
            member.goal_ready_told = True
            self.events.append(
                {"type": "goal_ready", "member": member.id, "reward": reward.name}
            )

    # -- Ziele ---------------------------------------------------------------

    def set_goal(self, actor: Actor, member_id: str, reward_id: str | None) -> Member:
        """Sparziel wählen (Kind für sich, Eltern für jedes Kind). None löscht es."""
        member = self.member(member_id)
        actor = self._as_child(actor, member_id)
        if not actor.is_manager and (actor.member is None or actor.member.id != member_id):
            raise PermissionDenied("Du kannst nur dein eigenes Ziel wählen.")
        if reward_id:
            if not self.reward(reward_id).available_for(member_id):
                raise FamilyError("Diese Belohnung gibt es für dich nicht.")
            member.goal_ready_told = member.points >= self.rewards[reward_id].cost
        member.goal_reward_id = reward_id or None
        return member

    def set_family_goal(self, actor: Actor, name: str, target: int, now: datetime) -> FamilyGoal:
        self._require_manager(actor)
        name = name.strip()
        if not name:
            raise FamilyError("Name fehlt.")
        if target < 1:
            raise FamilyError("Das Ziel braucht mindestens einen Stern.")
        self.goal = FamilyGoal(name, target, now)
        return self.goal

    def clear_family_goal(self, actor: Actor) -> None:
        self._require_manager(actor)
        self.goal = None

    # -- Ferien und Wochentage ---------------------------------------------

    def is_paused(self, now: datetime) -> bool:
        return (
            self.pause_until is not None
            and self.pause_from is not None
            and self.pause_from <= now < self.pause_until
        )

    def set_pause(self, actor: Actor, start: datetime, until: datetime) -> None:
        """Ferien: In diesem Zeitraum ist nichts fällig und nichts wird gesperrt."""
        self._require_manager(actor)
        if until <= start:
            raise FamilyError("Das Ende muss nach dem Anfang liegen.")
        self.pause_from, self.pause_until = start, until

    def end_pause(self, actor: Actor, now: datetime) -> None:
        self._require_manager(actor)
        if self.pause_until is None:
            raise FamilyError("Es gibt keine Ferien-Pause.")
        if self.pause_from and self.pause_from <= now:
            self.pause_until = now
            self._end_pause_if_over(now)
        else:
            self.pause_from = self.pause_until = None

    def _end_pause_if_over(self, now: datetime) -> bool:
        """Nach den Ferien: Fristen nach vorn schieben, Serien nicht reißen lassen."""
        if self.pause_until is None or now < self.pause_until or self.pause_from is None:
            return False
        start, end = self.pause_from, self.pause_until
        for chore in self.chores.values():
            if chore.due is None or chore.due >= end:
                continue
            if chore.recurrence in (Recurrence.NONE, Recurrence.ON_DEMAND):
                if chore.due >= start:
                    chore.due += end - start
            else:
                chore.due = self._allowed_day(chore, _next_due(chore.due, chore.recurrence, end))
            if chore.state is ChoreState.OVERDUE and chore.due > now:
                chore.state = ChoreState.OPEN
        start_day = start.astimezone(self.tz).date()
        end_day = end.astimezone(self.tz).date()
        for member in self.members.values():
            p = member.progress
            if p.streak_day and p.streak_day >= start_day - timedelta(days=1):
                p.streak_day = max(p.streak_day, end_day - timedelta(days=1))
        self.pause_from = self.pause_until = None
        return True

    def _allowed_day(self, chore: Chore, due: datetime | None) -> datetime | None:
        """Tägliche Aufgaben mit Wochentagen auf den nächsten erlaubten Tag legen."""
        if due is None or not chore.weekdays or chore.recurrence is not Recurrence.DAILY:
            return due
        for _ in range(7):
            if due.astimezone(self.tz).weekday() in chore.weekdays:
                break
            due += timedelta(days=1)
        return due

    # -- Wetter und Wochenbericht ---------------------------------------------

    def set_weather(self, actor: Actor, entity_id: str | None) -> None:
        self._require_manager(actor)
        self.weather_entity = entity_id or None
        if not self.weather_entity:
            self.bad_weather = False

    def _postpone(self, chore: Chore, now: datetime) -> None:
        """Draußen-Aufgabe bei Regen: gleiche Uhrzeit, nächster passender Tag."""
        while chore.due is not None and chore.due < now:
            chore.due = self._allowed_day(chore, chore.due + timedelta(days=1))
            chore.weather_shift += 1
        self._log(chore, "postponed", None, now)

    def set_report(self, actor: Actor, day: int, hour: int) -> None:
        self._require_manager(actor)
        if not -1 <= day <= 6 or not 0 <= hour <= 23:
            raise FamilyError("Tag -1 bis 6, Stunde 0 bis 23.")
        self.report_day, self.report_hour = day, hour

    def week_report(self, now: datetime, days: int = 7) -> list[dict[str, Any]]:
        """Pro Kind: erledigt, verpasst und verdiente Sterne der letzten Tage."""
        since = now - timedelta(days=days)
        rows = {
            m.id: {"member": m.id, "name": m.name, "done": 0, "missed": 0, "stars": 0,
                   "streak": m.progress.current_streak(now.astimezone(self.tz).date())}
            for m in self.ranked_members()
        }
        for chore in self.chores.values():
            for entry in chore.history:
                row = rows.get(entry.get("member"))
                if row is None or datetime.fromisoformat(entry["at"]) < since:
                    continue
                if entry["event"] == "completed":
                    row["done"] += 1
                    row["stars"] += int(entry.get("points", chore.points))
                elif entry["event"] == "missed":
                    row["missed"] += 1
        return list(rows.values())

    # -- Bonus und Abzug ------------------------------------------------------

    def give_stars(
        self, actor: Actor, member_id: str, stars: int, reason: str, now: datetime
    ) -> int:
        """Eltern geben Bonus-Sterne oder ziehen welche ab. Gibt die echte Änderung zurück.

        Ein Abzug geht nie unter null und senkt kein Level: Erreichtes bleibt.
        """
        self._require_manager(actor)
        member = self._child(member_id)
        if not stars or abs(stars) > 100:
            raise FamilyError("Zwischen 1 und 100 Sterne.")
        reason = reason.strip()[:60]
        if stars > 0:
            member.points += stars
            before = level_for(member.progress.earned)
            member.progress.earned += stars
            self._goal_step(member, stars, now)
            self._celebrate(member, now, level_before=before)
            delta = stars
        else:
            delta = -min(member.points, -stars) if member.points > 0 else 0
            member.points += delta
            self._goal_step(member, 0, now)
        self.star_log.append(
            {"member": member_id, "stars": delta, "asked": stars, "reason": reason,
             "at": now.isoformat()}
        )
        del self.star_log[:-STAR_LOG_LIMIT]
        if delta:
            self.events.append(
                {"type": "stars", "member": member_id, "stars": delta, "reason": reason}
            )
        return delta

    def star_history(self, member_id: str, limit: int = 20) -> list[dict[str, Any]]:
        return [e for e in reversed(self.star_log) if e["member"] == member_id][:limit]

    def add_preset(self, actor: Actor, name: str, stars: int) -> dict[str, Any]:
        self._require_manager(actor)
        name = name.strip()[:40]
        if not name or not stars or abs(stars) > 100:
            raise FamilyError("Name und 1 bis 100 Sterne (mit Minus für Abzug).")
        if len(self.presets) >= MAX_PRESETS:
            raise FamilyError(f"Höchstens {MAX_PRESETS} Vorschläge.")
        preset = {"id": uuid.uuid4().hex[:8], "name": name, "stars": stars}
        self.presets.append(preset)
        return preset

    def delete_preset(self, actor: Actor, preset_id: str) -> None:
        self._require_manager(actor)
        before = len(self.presets)
        self.presets = [p for p in self.presets if p["id"] != preset_id]
        if len(self.presets) == before:
            raise FamilyError("Diesen Vorschlag gibt es nicht.")

    # -- Kalender -------------------------------------------------------------

    def occurrences(
        self, start: datetime, end: datetime, member_id: str | None = None, limit: int = 500
    ) -> list[tuple[datetime, Chore, list[str]]]:
        """Fristen im Zeitraum, mit Wiederholungen vorausberechnet.

        Rotation wird reihum fortgeschrieben, Abwesenheiten in der Zukunft
        kennen wir nicht. Ferien-Pause und erledigte Einmal-Aufgaben fallen weg.
        """
        result: list[tuple[datetime, Chore, list[str]]] = []
        for chore in self.chores.values():
            if chore.due is None or chore.state is ChoreState.DONE or not chore.assignees:
                continue
            due, k = chore.due, 0
            step = _INTERVALS.get(chore.recurrence)
            while due < end and len(result) < limit:
                if due >= start and not self.is_paused(due) and (
                    not chore.weekdays
                    or chore.recurrence is not Recurrence.DAILY
                    or due.astimezone(self.tz).weekday() in chore.weekdays
                ):
                    who = self._who_at(chore, k, due)
                    if who and (member_id is None or member_id in who):
                        result.append((due, chore, who))
                if step is None:
                    break
                due += step
                k += 1
        result.sort(key=lambda r: r[0])
        return result

    def _who_at(self, chore: Chore, k: int, when: datetime) -> list[str]:
        if k == 0:
            return self.responsible(chore, when) or (
                [chore.claimed_by] if chore.claimed_by else []
            )
        age = chore.min_age
        if chore.rotation:
            member_id = chore.assignees[(chore.rotation_index + k) % len(chore.assignees)]
            member = self.members.get(member_id)
            return [member_id] if member and member.old_enough(age, when) else []
        return [
            m for m in chore.assignees
            if (member := self.members.get(m)) and member.old_enough(age, when)
        ]

    # -- Freihändig: NFC-Aufkleber und Sprache ------------------------------

    def set_tag(self, actor: Actor, chore_id: str, tag_id: str) -> Chore:
        self._require_manager(actor)
        chore = self.chore(chore_id)
        chore.tag_id = tag_id.strip()
        return chore

    def chores_with_tag(self, tag_id: str) -> list[Chore]:
        return [c for c in self.chores.values() if tag_id and c.tag_id == tag_id]

    def child_by_name(self, name: str) -> Member | None:
        wanted = _norm(name)
        for m in self.members.values():
            if m.role is Role.CHILD and _norm(m.name) == wanted:
                return m
        return None

    def open_for(self, member_id: str, now: datetime) -> list[Chore]:
        """Was ein Kind jetzt noch tun kann: offen oder überfällig, Frist bis heute."""
        end = now.astimezone(self.tz).replace(hour=23, minute=59, second=59)
        return sorted(
            (
                c for c in self.chores_for(member_id, now)
                if c.state in (ChoreState.OPEN, ChoreState.OVERDUE)
                and (c.due is None or c.due <= end)
            ),
            key=lambda c: (c.state is not ChoreState.OVERDUE, c.due or end),
        )

    def match_chore(self, member_id: str, spoken: str, now: datetime) -> Chore | None:
        """Gesprochenen Text der passendsten offenen Aufgabe zuordnen."""
        words = set(_norm(spoken).split()) - _FILLER
        if not words:
            return None
        best, score = None, 0.0
        for chore in self.open_for(member_id, now):
            name = set(_norm(chore.name).split()) - _FILLER
            overlap = max(
                (SequenceMatcher(None, w, n).ratio() for w in words for n in name),
                default=0.0,
            )
            whole = SequenceMatcher(None, " ".join(sorted(words)), " ".join(sorted(name))).ratio()
            value = max(overlap, whole)
            if value > score:
                best, score = chore, value
        return best if score >= 0.75 else None

    def house_done(self, chore_id: str, now: datetime) -> str | None:
        """Ein Sensor meldet die Aufgabe als erledigt. Gibt zurück, für wen.

        Gutgeschrieben wird nur, wenn genau ein Kind dran ist. Das Haus braucht
        keine Freigabe, es hat ja selbst nachgesehen.
        """
        chore = self.chore(chore_id)
        if chore.state not in (ChoreState.OPEN, ChoreState.OVERDUE, ChoreState.CLAIMED):
            return None
        if chore.state is ChoreState.CLAIMED and chore.claimed_by:
            self._complete(chore, chore.claimed_by, now)
            return chore.last_completed_by
        who = self.responsible(chore, now)
        if len(who) != 1:
            return None
        self.claim(SYSTEM, chore.id, who[0], now)
        return who[0]

    def claim_hands_free(self, member_id: str, chore: Chore, now: datetime) -> Chore:
        """Per Aufkleber oder Sprache melden: zählt wie selbst abgehakt.

        Freigabe gilt wie am Handy. Fotonachweis geht so nicht, dafür braucht
        es die App.
        """
        member = self.member(member_id)
        if self.needs_photo(chore):
            raise FamilyError("Für diese Aufgabe brauchst du ein Foto. Bitte in der App abhaken.")
        return self.claim(Actor(member=member), chore.id, member_id, now)

    def set_picture_mode(self, actor: Actor, member_id: str, enabled: bool) -> Member:
        self._require_manager(actor)
        member = self._child(member_id)
        member.picture_mode = enabled
        return member

    def set_theme(self, actor: Actor, member_id: str, theme: str) -> Member:
        """Design der eigenen Ansicht (Kind für sich, Eltern für alle)."""
        member = self.member(member_id)
        actor = self._as_child(actor, member_id)
        if not actor.is_manager and (actor.member is None or actor.member.id != member_id):
            raise PermissionDenied("Du kannst nur dein eigenes Design wählen.")
        if theme not in THEMES:
            raise FamilyError("Dieses Design gibt es nicht.")
        member.theme = theme
        return member

    # -- Taschengeld -------------------------------------------------------

    def set_money(self, actor: Actor, rate: int, payday: int) -> None:
        """Tauschkurs (Sterne pro Euro, 0 = aus) und Zahltag (0 = Montag)."""
        self._require_manager(actor)
        if rate < 0 or not 0 <= payday <= 6:
            raise FamilyError("Ungültige Einstellung.")
        self.money_rate = rate
        self.payday = payday

    def set_allowance(self, actor: Actor, member_id: str, cents: int, now: datetime) -> Member:
        """Fester Betrag pro Woche. Der erste kommt am nächsten Zahltag."""
        self._require_manager(actor)
        member = self._child(member_id)
        if cents < 0:
            raise FamilyError("Der Betrag darf nicht negativ sein.")
        if not member.allowance:
            # Nicht rückwirkend für diese Woche auszahlen, wenn der Zahltag schon war.
            member.allowance_paid = now.astimezone(self.tz).date()
        member.allowance = cents
        return member

    def exchange(self, actor: Actor, member_id: str, euros: int, now: datetime) -> Member:
        """Kind tauscht Sterne in Taschengeld, sofort und in ganzen Euro."""
        member = self._child(member_id)
        actor = self._as_child(actor, member_id)
        if not actor.is_manager and (actor.member is None or actor.member.id != member_id):
            raise PermissionDenied("Du kannst nur deine eigenen Sterne tauschen.")
        if not self.money_rate:
            raise FamilyError("Sterne tauschen ist nicht eingeschaltet.")
        if euros < 1:
            raise FamilyError("Mindestens 1 Euro.")
        stars = euros * self.money_rate
        if member.points < stars:
            raise FamilyError(f"Dafür brauchst du {stars} Sterne, du hast {member.points}.")
        member.points -= stars
        self._book(member, euros * 100, "exchange", now, stars=stars)
        return member

    def payout(self, actor: Actor, member_id: str, cents: int | None, now: datetime) -> Member:
        """Eltern zahlen aus (bar oder überwiesen). Ohne Betrag alles."""
        self._require_manager(actor)
        member = self._child(member_id)
        cents = member.money if cents is None else cents
        if cents <= 0 or cents > member.money:
            raise FamilyError("So viel ist nicht auf dem Konto.")
        self._book(member, -cents, "payout", now)
        return member

    def adjust_money(
        self, actor: Actor, member_id: str, cents: int, note: str, now: datetime
    ) -> Member:
        """Eltern buchen etwas dazu oder ab, z. B. Bonus oder Ersatz für Kaputtes."""
        self._require_manager(actor)
        member = self._child(member_id)
        if not cents:
            raise FamilyError("Betrag fehlt.")
        if member.money + cents < 0:
            raise FamilyError("Das Konto darf nicht ins Minus.")
        self._book(member, cents, "adjust", now, note=note.strip()[:80])
        return member

    def pay_allowances(self, now: datetime) -> bool:
        """Am Zahltag das Wochengeld gutschreiben, einmal pro Woche."""
        today = now.astimezone(self.tz).date()
        if today.weekday() != self.payday:
            return False
        changed = False
        for member in self.members.values():
            if member.role is not Role.CHILD or not member.allowance:
                continue
            if member.allowance_paid and (today - member.allowance_paid).days < 7:
                continue
            member.allowance_paid = today
            self._book(member, member.allowance, "allowance", now)
            self.events.append(
                {"type": "allowance", "member": member.id, "cents": member.allowance}
            )
            changed = True
        return changed

    def money_history(self, member_id: str, limit: int = 20) -> list[dict[str, Any]]:
        return [e for e in reversed(self.money_log) if e["member"] == member_id][:limit]

    def _child(self, member_id: str) -> Member:
        member = self.member(member_id)
        if member.role is not Role.CHILD:
            raise FamilyError("Taschengeld gibt es nur für Kinder.")
        return member

    def _book(self, member: Member, cents: int, kind: str, now: datetime, **extra: Any) -> None:
        member.money += cents
        self.money_log.append(
            {"member": member.id, "cents": cents, "kind": kind, "at": now.isoformat(),
             "balance": member.money, **extra}
        )
        del self.money_log[:-MONEY_LOG_LIMIT]

    def _celebrate(self, member: Member, now: datetime, *, level_before: int | None = None) -> None:
        progress = member.progress
        if level_before is not None and progress.level > level_before:
            self.events.append(
                {"type": "level", "member": member.id, "level": progress.level}
            )
        for badge in new_badges(progress, now):
            self.events.append(
                {"type": "badge", "member": member.id, "badge": badge.id, "emoji": badge.emoji}
            )

    @staticmethod
    def _reset_claim(chore: Chore) -> None:
        chore.claim_multiplier = 1
        chore.claim_taken_from = None

    @staticmethod
    def _log(
        chore: Chore, event: str, member_id: str | None, now: datetime, **extra: Any
    ) -> None:
        chore.history.append(
            {"event": event, "member": member_id, "at": now.isoformat(), **extra}
        )
        del chore.history[:-HISTORY_LIMIT]


# Füllwörter, die beim Zuordnen gesprochener Aufgaben nichts bedeuten
_FILLER = {
    "den", "die", "das", "der", "dem", "ein", "eine", "einen", "mein", "meine", "meinen",
    "ich", "habe", "hab", "hat", "bin", "fertig", "erledigt", "gemacht", "geschafft",
    "the", "a", "my", "i", "have", "did", "done", "finished", "with", "mit",
}


def _norm(text: str) -> str:
    text = text.lower().replace("ß", "ss")
    return "".join(ch if ch.isalnum() or ch == " " else " " for ch in text).strip()


HOUSE_FIELDS = ("done_entity", "done_state", "start_entity", "start_state")


def _set_house(chore: Chore, house: dict[str, str]) -> None:
    for key in HOUSE_FIELDS:
        if key in house:
            setattr(chore, key, str(house[key] or "").strip()[:100])


def _clean_steps(steps: list[str] | None) -> list[str]:
    cleaned = [s.strip()[:60] for s in steps or [] if s and s.strip()]
    if len(cleaned) > MAX_STEPS:
        raise FamilyError(f"Höchstens {MAX_STEPS} Schritte.")
    return cleaned


def _clean_weekdays(days: list[int] | None) -> list[int]:
    cleaned = sorted({int(d) for d in days or []})
    if any(d < 0 or d > 6 for d in cleaned):
        raise FamilyError("Wochentage gehen von 0 (Montag) bis 6 (Sonntag).")
    return [] if len(cleaned) == 7 else cleaned


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
