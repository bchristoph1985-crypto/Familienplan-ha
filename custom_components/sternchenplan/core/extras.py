"""Zusatzfunktionen, die Familien bei der Einrichtung an- oder abwählen.

Haustier, Zimmerlampe, Bildschirmzeit, Aufgaben bei Bedarf, Familienrat,
Monatsurkunde und „Eltern machen mit“. Die Regeln stehen hier, damit
family.py übersichtlich bleibt. `Family` erbt davon.
"""

from __future__ import annotations

import math
import uuid
from collections import Counter
from datetime import date, datetime, timedelta
from typing import TYPE_CHECKING, Any

from .models import ChoreState, Member, Recurrence, Role

if TYPE_CHECKING:
    from .family import Actor

# Was eine Familie nutzen kann. Reihenfolge = Anzeige im Assistenten.
FEATURES = ("pet", "lamp", "screen", "demand", "vote", "certificate", "parents", "money", "goal")
# Ohne Auswahl ist alles an, nur „Eltern machen mit“ nicht: das ändert die Wertung.
DEFAULT_FEATURES = frozenset(FEATURES) - {"parents"}

PETS = ("dragon", "cat", "dog", "unicorn", "dino", "panda", "fox", "owl")

SCREEN_STEP = 5  # Bildschirmzeit gibt es in 5-Minuten-Schritten
SCREEN_WARN = timedelta(minutes=5)
MAX_VOTE_OPTIONS = 6
DEMAND_HOURS = 2  # so lange hat man Zeit, wenn ein Gerät eine Aufgabe fällig macht


class ExtrasMixin:
    """Wird in `Family` gemischt. Nutzt deren Hilfen (_require_manager, member, ...)."""

    features: set[str]
    vote: dict[str, Any] | None
    screen_rate: int
    screen_max: int
    screen_on: dict[str, list[str]]

    def _init_extras(self) -> None:
        self.features = set(DEFAULT_FEATURES)
        self.vote = None
        # Bildschirmzeit: Minuten pro Stern (0 = aus) und höchstens so viele Minuten am Tag
        self.screen_rate = 0
        self.screen_max = 60
        # Welche Geräte wir für die Bildschirmzeit eingeschaltet haben
        self.screen_on = {}
        # Sparsame Push-Nachrichten: keine Namen und Aufgaben im Text (laufen über Google/Apple)
        self.private_push = False

    def _extras_to_dict(self) -> dict[str, Any]:
        return {
            "features": sorted(self.features),
            "vote": dict(self.vote) if self.vote else None,
            "screen_rate": self.screen_rate,
            "screen_max": self.screen_max,
            "screen_on": {k: list(v) for k, v in self.screen_on.items()},
            "private_push": self.private_push,
        }

    def _extras_from_dict(self, data: dict[str, Any]) -> None:
        if "features" in data:
            self.features = {f for f in data["features"] if f in FEATURES}
        self.vote = data.get("vote")
        self.screen_rate = int(data.get("screen_rate", 0))
        self.screen_max = int(data.get("screen_max", 60))
        self.screen_on = {k: list(v) for k, v in data.get("screen_on", {}).items()}
        self.private_push = bool(data.get("private_push", False))

    def has(self, feature: str) -> bool:
        return feature in self.features

    def set_features(self, actor: Actor, features: list[str]) -> None:
        self._require_manager(actor)
        unknown = set(features) - set(FEATURES)
        if unknown:
            raise self._error(f"Unbekannte Funktion: {', '.join(sorted(unknown))}")
        self.features = set(features)

    def _need(self, feature: str) -> None:
        if not self.has(feature):
            raise self._error("Diese Funktion ist ausgeschaltet.")

    # -- Datenschutz -----------------------------------------------------------

    def set_private_push(self, actor: Actor, enabled: bool) -> None:
        self._require_manager(actor)
        self.private_push = enabled

    def export_member(self, actor: Actor, member_id: str) -> dict[str, Any]:
        """Alles, was Sternchenplan über eine Person speichert (Auskunft, Umzug)."""
        self._require_manager(actor)
        member = self.member(member_id)
        return {
            "member": member.to_dict(),
            "chores": [
                {"id": c.id, "name": c.name, "assigned": member_id in c.assignees,
                 "history": [h for h in c.history if h.get("member") == member_id]}
                for c in self.chores.values()
                if member_id in c.assignees or any(h.get("member") == member_id for h in c.history)
            ],
            "redemptions": [r.to_dict() for r in self.redemptions if r.member_id == member_id],
            "star_log": [e for e in self.star_log if e["member"] == member_id],
            "money_log": [e for e in self.money_log if e["member"] == member_id],
            "vote": (
                {"question": self.vote["question"],
                 "choice": self.vote["options"][self.vote["votes"][member_id]]}
                if self.vote and member_id in self.vote["votes"] else None
            ),
        }

    def _purge(self, member_id: str) -> list[str]:
        """Spuren einer Person löschen. Gibt die Fotos zurück, die weg müssen."""
        photos = []
        for chore in self.chores.values():
            mine = chore.claimed_by == member_id or chore.last_completed_by == member_id
            if chore.photo and mine:
                photos.append(chore.photo)
                chore.photo = None
            chore.history = [h for h in chore.history if h.get("member") != member_id]
            if chore.last_completed_by == member_id:
                chore.last_completed_by = chore.last_completed_at = None
            if chore.claim_taken_from == member_id:
                chore.claim_taken_from = None
        self.redemptions = [r for r in self.redemptions if r.member_id != member_id]
        self.star_log = [e for e in self.star_log if e["member"] != member_id]
        self.money_log = [e for e in self.money_log if e["member"] != member_id]
        if self.vote:
            self.vote["votes"].pop(member_id, None)
        self.screen_on.pop(member_id, None)
        return photos

    # -- Haustier -------------------------------------------------------------

    def set_pet(self, actor: Actor, member_id: str, pet: str, name: str) -> Member:
        """Kind sucht sein Haustier aus und gibt ihm einen Namen."""
        self._need("pet")
        member = self.member(member_id)
        actor = self._as_child(actor, member_id)
        if not actor.is_manager and (actor.member is None or actor.member.id != member_id):
            raise self._denied("Du kannst nur dein eigenes Haustier aussuchen.")
        if pet and pet not in PETS:
            raise self._error("Dieses Tier gibt es nicht.")
        member.pet = pet
        member.pet_name = name.strip()[:20]
        return member

    # -- Zimmerlampe -----------------------------------------------------------

    def set_lamp(self, actor: Actor, member_id: str, entity_id: str) -> Member:
        self._require_manager(actor)
        member = self.member(member_id)
        entity_id = entity_id.strip()
        if entity_id and not entity_id.startswith("light."):
            raise self._error("Bitte eine Lampe (light.…) auswählen.")
        member.lamp = entity_id
        return member

    def all_done_today(self, member_id: str, now: datetime) -> bool:
        return not self.open_for(member_id, now) and not any(
            c.state is ChoreState.CLAIMED and c.claimed_by == member_id for c in self.chores.values()
        )

    def _check_all_done(self, member: Member, now: datetime) -> None:
        """Nach dem Abhaken: Ist heute alles geschafft, gibt es ein Ereignis (grüne Lampe)."""
        if self.all_done_today(member.id, now):
            self.events.append({"type": "all_done", "member": member.id})

    # -- Bildschirmzeit --------------------------------------------------------

    def set_screen(self, actor: Actor, rate: int, max_minutes: int) -> None:
        """Minuten pro Stern (0 = aus) und Tageshöchstwert."""
        self._require_manager(actor)
        if not 0 <= rate <= 60 or not 5 <= max_minutes <= 600:
            raise self._error("Ungültige Einstellung.")
        self.screen_rate = rate
        self.screen_max = max_minutes

    def set_screen_devices(self, actor: Actor, member_id: str, devices: list[str]) -> Member:
        self._require_manager(actor)
        member = self._child(member_id)
        member.screen_devices = list(dict.fromkeys(d.strip() for d in devices if d.strip()))
        return member

    def screen_cost(self, minutes: int) -> int:
        return math.ceil(minutes / self.screen_rate) if self.screen_rate else 0

    def screen_left_today(self, member: Member, now: datetime) -> int:
        today = now.astimezone(self.tz).date()
        used = member.screen_used if member.screen_day == today else 0
        return max(0, self.screen_max - used)

    def buy_screen_time(self, actor: Actor, member_id: str, minutes: int, now: datetime) -> Member:
        """Kind tauscht Sterne gegen Bildschirmzeit. Die Geräte gehen sofort an."""
        self._need("screen")
        member = self._child(member_id)
        actor = self._as_child(actor, member_id)
        if not actor.is_manager and (actor.member is None or actor.member.id != member_id):
            raise self._denied("Du kannst nur deine eigenen Sterne tauschen.")
        if not self.screen_rate:
            raise self._error("Bildschirmzeit gegen Sterne ist nicht eingeschaltet.")
        if not member.screen_devices:
            raise self._error("Für dich sind keine Geräte eingestellt.")
        if minutes < SCREEN_STEP or minutes % SCREEN_STEP:
            raise self._error(f"Bitte in {SCREEN_STEP}-Minuten-Schritten.")
        if self.should_lock(member_id, now):
            raise self._error("Erst die überfälligen Aufgaben erledigen.")
        left = self.screen_left_today(member, now)
        if minutes > left:
            raise self._error(f"Heute gehen noch {left} Minuten.")
        cost = self.screen_cost(minutes)
        if member.points < cost:
            raise self._error(f"Dafür brauchst du {cost} Sterne, du hast {member.points}.")
        member.points -= cost
        today = now.astimezone(self.tz).date()
        member.screen_used = (member.screen_used if member.screen_day == today else 0) + minutes
        member.screen_day = today
        start = member.screen_until if member.screen_until and member.screen_until > now else now
        member.screen_until = start + timedelta(minutes=minutes)
        member.screen_warned = member.screen_until - now <= SCREEN_WARN
        self.events.append({"type": "screen_start", "member": member.id, "minutes": minutes})
        return member

    def stop_screen_time(self, actor: Actor, member_id: str, now: datetime) -> Member:
        """Vorzeitig beenden (Kind selbst oder Eltern). Sterne gibt es nicht zurück."""
        member = self._child(member_id)
        actor = self._as_child(actor, member_id)
        if not actor.is_manager and (actor.member is None or actor.member.id != member_id):
            raise self._denied("Nur Eltern dürfen das.")
        if member.screen_until is None or member.screen_until <= now:
            raise self._error("Gerade läuft keine Bildschirmzeit.")
        member.screen_until = now
        return member

    def screen_active(self, member: Member, now: datetime) -> bool:
        return (
            self.has("screen")
            and member.screen_until is not None
            and now < member.screen_until
            and not self.should_lock(member.id, now)
        )

    def _refresh_screen(self, now: datetime) -> bool:
        changed = False
        for member in self.members.values():
            until = member.screen_until
            if until is None:
                continue
            if now >= until:
                member.screen_until = None
                member.screen_warned = False
                self.events.append({"type": "screen_over", "member": member.id})
                changed = True
            elif not member.screen_warned and until - now <= SCREEN_WARN:
                member.screen_warned = True
                self.events.append({"type": "screen_ending", "member": member.id})
                changed = True
        return changed

    # -- Aufgaben bei Bedarf ---------------------------------------------------

    def trigger_chore(
        self, actor: Actor, chore_id: str, now: datetime, hours: int = DEMAND_HOURS
    ) -> bool:
        """Bedarfs-Aufgabe fällig machen. False, wenn sie schon offen ist."""
        self._require_manager(actor)
        chore = self.chore(chore_id)
        if chore.recurrence is not Recurrence.ON_DEMAND:
            raise self._error("Das geht nur bei Aufgaben „bei Bedarf“.")
        if chore.state is not ChoreState.DONE:
            return False
        chore.state = ChoreState.OPEN
        chore.due = now + timedelta(hours=hours)
        self._log(chore, "triggered", None, now)
        self.events.append(
            {"type": "demand", "chore": chore.id, "name": chore.name,
             "members": self.responsible(chore, now)}
        )
        return True

    # -- Familienrat -----------------------------------------------------------

    def start_vote(
        self, actor: Actor, question: str, options: list[str], hours: int, now: datetime
    ) -> dict[str, Any]:
        self._need("vote")
        self._require_manager(actor)
        question = question.strip()[:100]
        options = [o.strip()[:40] for o in options if o and o.strip()]
        if not question:
            raise self._error("Frage fehlt.")
        if not 2 <= len(options) <= MAX_VOTE_OPTIONS:
            raise self._error(f"2 bis {MAX_VOTE_OPTIONS} Möglichkeiten.")
        if not 1 <= hours <= 24 * 7:
            raise self._error("Zwischen 1 Stunde und 7 Tagen.")
        self.vote = {
            "id": uuid.uuid4().hex[:8],
            "question": question,
            "options": options,
            "votes": {},
            "created_at": now.isoformat(),
            "closes_at": (now + timedelta(hours=hours)).isoformat(),
            "closed_at": None,
            "winner": None,
        }
        self.events.append({"type": "vote_started", "question": question})
        return self.vote

    def cast_vote(self, actor: Actor, member_id: str, index: int, now: datetime) -> dict[str, Any]:
        """Jedes Familienmitglied hat eine Stimme und kann sie ändern, bis abgestimmt ist."""
        self._need("vote")
        vote = self.vote
        if not vote or vote["closed_at"]:
            raise self._error("Gerade gibt es keine Abstimmung.")
        self.member(member_id)
        actor = self._as_child(actor, member_id)
        if actor.member is None or actor.member.id != member_id:
            raise self._denied("Du kannst nur für dich selbst abstimmen.")
        if not 0 <= index < len(vote["options"]):
            raise self._error("Diese Möglichkeit gibt es nicht.")
        vote["votes"][member_id] = index
        voters = {m.id for m in self.members.values() if not m.is_away(now)}
        if voters <= set(vote["votes"]):
            self._close_vote(now)
        return vote

    def end_vote(self, actor: Actor, now: datetime) -> None:
        self._require_manager(actor)
        if not self.vote:
            raise self._error("Es gibt keine Abstimmung.")
        if self.vote["closed_at"]:
            self.vote = None  # Ergebnis ausblenden
        else:
            self._close_vote(now)

    def _close_vote(self, now: datetime) -> None:
        vote = self.vote
        counts = Counter(vote["votes"].values())
        best = max(counts.values(), default=0)
        winners = [i for i in range(len(vote["options"])) if counts.get(i, 0) == best and best]
        vote["closed_at"] = now.isoformat()
        vote["winner"] = winners[0] if len(winners) == 1 else None
        self.events.append(
            {"type": "vote_result", "question": vote["question"],
             "winner": vote["options"][winners[0]] if len(winners) == 1 else None,
             "tie": [vote["options"][i] for i in winners] if len(winners) > 1 else []}
        )

    def _refresh_vote(self, now: datetime) -> bool:
        vote = self.vote
        if vote and not vote["closed_at"] and now >= datetime.fromisoformat(vote["closes_at"]):
            self._close_vote(now)
            return True
        if vote and vote["closed_at"] and now - datetime.fromisoformat(vote["closed_at"]) > timedelta(days=3):
            self.vote = None  # altes Ergebnis nach drei Tagen ausblenden
            return True
        return False

    # -- Monatsurkunde ---------------------------------------------------------

    def ranked_members(self) -> list[Member]:
        """Wer in Wertung, Urkunde und Familienziel zählt: Kinder, mit Feature auch Eltern."""
        return [
            m for m in self.members.values()
            if m.role is Role.CHILD or (self.has("parents") and m.role is Role.PARENT)
        ]

    def month_report(self, year: int, month: int) -> list[dict[str, Any]]:
        """Pro Person: erledigt, verpasst, Sterne, neue Abzeichen und Lieblingsaufgabe im Monat."""
        start = date(year, month, 1)
        end = date(year + (month == 12), month % 12 + 1, 1)

        def in_month(iso: str) -> bool:
            return start <= datetime.fromisoformat(iso).astimezone(self.tz).date() < end

        rows: dict[str, dict[str, Any]] = {}
        favourites: dict[str, Counter] = {}
        for m in self.ranked_members():
            rows[m.id] = {
                "member": m.id, "name": m.name, "done": 0, "missed": 0, "stars": 0,
                "bonus": 0, "best_streak": m.progress.best_streak,
                "badges": [b for b, at in m.progress.badges.items() if in_month(at)],
                "favourite": None,
            }
            favourites[m.id] = Counter()
        for chore in self.chores.values():
            for entry in chore.history:
                row = rows.get(entry.get("member"))
                if row is None or not in_month(entry["at"]):
                    continue
                if entry["event"] == "completed":
                    row["done"] += 1
                    row["stars"] += int(entry.get("points", chore.points))
                    favourites[row["member"]][chore.name] += 1
                elif entry["event"] == "missed":
                    row["missed"] += 1
        for entry in self.star_log:
            row = rows.get(entry["member"])
            if row is not None and entry["stars"] > 0 and in_month(entry["at"]):
                row["bonus"] += entry["stars"]
        for member_id, counter in favourites.items():
            if counter:
                rows[member_id]["favourite"] = counter.most_common(1)[0][0]
        return list(rows.values())

    @staticmethod
    def previous_month(today: date) -> tuple[int, int]:
        first = today.replace(day=1) - timedelta(days=1)
        return first.year, first.month
