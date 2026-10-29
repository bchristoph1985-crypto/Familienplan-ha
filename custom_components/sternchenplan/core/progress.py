"""Fortschritt der Kinder: Level, Serien und Abzeichen.

Alles hier ergibt sich aus Zählern am Mitglied. Die Zähler wachsen nur, auch
wenn Sterne für Belohnungen ausgegeben werden. So fällt niemand im Level
zurück, nur weil er sich etwas gegönnt hat.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Any

# Sterne, die man insgesamt für ein Level braucht: 0, 5, 15, 30, 50, 75, ...
LEVEL_STEP = 5
EARLY_HOUR = 9  # „Frühaufsteher“: erledigt vor 9 Uhr Ortszeit


def level_floor(level: int) -> int:
    """Sterne insgesamt, ab denen dieses Level erreicht ist."""
    return LEVEL_STEP * (level - 1) * level // 2


def level_for(earned: int) -> int:
    level = 1
    while level_floor(level + 1) <= earned:
        level += 1
    return level


@dataclass
class Progress:
    earned: int = 0  # Sterne insgesamt, Ausgeben zieht nichts ab
    done: int = 0
    taken_over: int = 0
    photos: int = 0
    early: int = 0
    redeemed: int = 0
    streak: int = 0
    best_streak: int = 0
    streak_day: date | None = None  # letzter Tag, der zur Serie zählt
    badges: dict[str, str] = field(default_factory=dict)  # Abzeichen -> erreicht am

    @property
    def level(self) -> int:
        return level_for(self.earned)

    def current_streak(self, today: date) -> int:
        """Die Serie reißt erst, wenn gestern nichts erledigt wurde."""
        if self.streak_day is None or self.streak_day < today - timedelta(days=1):
            return 0
        return self.streak

    def count_day(self, today: date) -> None:
        if self.streak_day == today:
            return
        if self.streak_day == today - timedelta(days=1):
            self.streak += 1
        else:
            self.streak = 1
        self.streak_day = today
        self.best_streak = max(self.best_streak, self.streak)

    def to_dict(self) -> dict[str, Any]:
        return {
            "earned": self.earned,
            "done": self.done,
            "taken_over": self.taken_over,
            "photos": self.photos,
            "early": self.early,
            "redeemed": self.redeemed,
            "streak": self.streak,
            "best_streak": self.best_streak,
            "streak_day": self.streak_day.isoformat() if self.streak_day else None,
            "badges": dict(self.badges),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Progress:
        day = data.get("streak_day")
        return cls(
            earned=int(data.get("earned", 0)),
            done=int(data.get("done", 0)),
            taken_over=int(data.get("taken_over", 0)),
            photos=int(data.get("photos", 0)),
            early=int(data.get("early", 0)),
            redeemed=int(data.get("redeemed", 0)),
            streak=int(data.get("streak", 0)),
            best_streak=int(data.get("best_streak", 0)),
            streak_day=date.fromisoformat(day) if day else None,
            badges=dict(data.get("badges", {})),
        )


@dataclass(frozen=True)
class Badge:
    id: str
    emoji: str
    counter: str  # Feld von Progress, best_streak für Serien
    target: int


# Reihenfolge = Anzeige. Namen und Texte stehen in der Karte (Deutsch/Englisch).
BADGES: tuple[Badge, ...] = (
    Badge("first", "🌟", "done", 1),
    Badge("done10", "🐝", "done", 10),
    Badge("done50", "🏅", "done", 50),
    Badge("done100", "🦸", "done", 100),
    Badge("done250", "👑", "done", 250),
    Badge("streak3", "🔥", "best_streak", 3),
    Badge("streak7", "🚀", "best_streak", 7),
    Badge("streak30", "☄️", "best_streak", 30),
    Badge("helper1", "🛟", "taken_over", 1),
    Badge("helper10", "🦾", "taken_over", 10),
    Badge("early5", "🌅", "early", 5),
    Badge("photo10", "📸", "photos", 10),
    Badge("reward1", "🎁", "redeemed", 1),
    Badge("stars100", "💯", "earned", 100),
    Badge("stars500", "💎", "earned", 500),
)


def new_badges(progress: Progress, now: datetime) -> list[Badge]:
    """Neu verdiente Abzeichen eintragen und zurückgeben."""
    earned = []
    for badge in BADGES:
        if badge.id not in progress.badges and getattr(progress, badge.counter) >= badge.target:
            progress.badges[badge.id] = now.isoformat()
            earned.append(badge)
    return earned


def badge_status(progress: Progress) -> list[dict[str, Any]]:
    """Alle Abzeichen mit Stand, für Karte und Sensor."""
    return [
        {
            "id": b.id,
            "emoji": b.emoji,
            "target": b.target,
            "value": min(getattr(progress, b.counter), b.target),
            "counter": b.counter,
            "earned_at": progress.badges.get(b.id),
        }
        for b in BADGES
    ]
