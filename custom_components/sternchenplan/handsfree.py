"""Abhaken ohne Bildschirm: NFC-Aufkleber und Sprachbefehle über Home Assistant Assist.

Aufkleber: Die Home-Assistant-App meldet `tag_scanned` mit dem Konto des Handys.
Gehört das Handy einem Kind, meldet es seine Aufgaben mit diesem Aufkleber.
Ein Lesegerät ohne Konto (z. B. an der Haustür) meldet für das Kind, das gerade
dran ist, wenn es genau eins ist.

Sprache: Sätze wie „Ich habe den Müll rausgebracht“ oder „Lucas hat den Tisch
gedeckt“. Rechte wie beim Abhaken am Handy, Fotos gehen nur in der App.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import timedelta
from typing import TYPE_CHECKING

from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.util import dt as dt_util

from .privacy import scrub
from .core import Chore, ChoreState, FamilyError, Member, Role

if TYPE_CHECKING:
    from . import SternchenplanConfigEntry

_LOGGER = logging.getLogger(__name__)

LEARN_TIME = timedelta(minutes=2)
DATA_LEARN = "sternchenplan_learn_tag"

_VERBS_DE = (
    "erledigt|gemacht|geschafft|rausgebracht|rausgetragen|weggebracht|ausgeräumt|eingeräumt|"
    "aufgeräumt|geputzt|gefüttert|gesaugt|gedeckt|abgeräumt|gemäht|gegossen|gemacht|"
    "gepackt|gewechselt|aufgehängt|zusammengelegt|gespült|abgetrocknet|geleert|gekehrt|gerecht"
)
SENTENCES = {
    "de": {
        "done": [
            f"ich (habe|hab) {{aufgabe}} ({_VERBS_DE})",
            "ich bin mit {aufgabe} fertig",
            f"{{name}} hat {{aufgabe}} ({_VERBS_DE})",
            "{name} ist mit {aufgabe} fertig",
        ],
        "open": [
            "was muss ich [heute] [noch] (machen|tun|erledigen)",
            "was (muss|soll) {name} [heute] [noch] (machen|tun|erledigen)",
            "welche aufgaben (habe|hab) ich [heute] [noch]",
            "welche aufgaben hat {name} [heute] [noch]",
        ],
        "stars": [
            "wie viele sterne (habe|hab) ich",
            "wie viele sterne hat {name}",
        ],
    },
    "en": {
        "done": [
            "i (did|finished|have done) {aufgabe}",
            "i am done with {aufgabe}",
            "{name} (did|finished|has done) {aufgabe}",
        ],
        "open": [
            "what (do|should) i [still] (have to do|do) [today]",
            "what (does|should) {name} [still] (have to do|do) [today]",
            "which chores (do|does) {name} have [today]",
        ],
        "stars": [
            "how many stars do i have",
            "how many stars does {name} have",
        ],
    },
}

TEXT = {
    "de": {
        "done": "Super, {name}! „{chore}“ ist erledigt. ⭐ +{points}",
        "waiting": "Danke, {name}! „{chore}“ wartet jetzt auf die Freigabe.",
        "unknown_chore": "Ich habe keine offene Aufgabe „{spoken}“ für {name} gefunden.",
        "who": "Wer bist du? Sag zum Beispiel: Lucas hat den Müll rausgebracht.",
        "unknown_name": "Ich kenne kein Kind namens {spoken}.",
        "open": "{name}, bei dir ist noch offen: {list}.",
        "nothing": "{name}, für heute ist alles erledigt. Super!",
        "and": "und",
        "stars": "{name} hat {points} Sterne.",
        "tag_learned": "Aufkleber für „{chore}“ gespeichert.",
        "tag_nothing": "Für dich ist hier gerade nichts offen.",
        "only_self": "Du kannst nur für dich selbst melden.",
    },
    "en": {
        "done": "Great, {name}! “{chore}” is done. ⭐ +{points}",
        "waiting": "Thanks, {name}! “{chore}” is waiting for approval.",
        "unknown_chore": "I couldn't find an open chore “{spoken}” for {name}.",
        "who": "Who are you? Say for example: Lucas did the dishes.",
        "unknown_name": "I don't know a child called {spoken}.",
        "open": "{name}, still to do: {list}.",
        "nothing": "{name}, everything is done for today. Great!",
        "and": "and",
        "stars": "{name} has {points} stars.",
        "tag_learned": "Tag saved for “{chore}”.",
        "tag_nothing": "There's nothing open for you here right now.",
        "only_self": "You can only report for yourself.",
    },
}


def _lang(hass: HomeAssistant) -> str:
    return "de" if (hass.config.language or "").startswith("de") else "en"


def _text(hass: HomeAssistant) -> dict[str, str]:
    return TEXT[_lang(hass)]


def _spoken_list(items: list[str], word_and: str) -> str:
    if len(items) <= 1:
        return "".join(items)
    return f"{', '.join(items[:-1])} {word_and} {items[-1]}"


def start_learning(hass: HomeAssistant, chore_id: str) -> None:
    """Der nächste gescannte Aufkleber gehört zu dieser Aufgabe."""
    hass.data[DATA_LEARN] = (chore_id, dt_util.utcnow() + LEARN_TIME)


def learning(hass: HomeAssistant) -> str | None:
    pending = hass.data.get(DATA_LEARN)
    if pending and pending[1] > dt_util.utcnow():
        return pending[0]
    return None


async def _notify(hass: HomeAssistant, member: Member | None, message: str) -> None:
    if member is None or not member.notify_service:
        return
    service = member.notify_service.removeprefix("notify.")
    if hass.services.has_service("notify", service):
        await hass.services.async_call(
            "notify", service, scrub(hass, {"title": "Sternchenplan", "message": message}), blocking=False
        )


def _result(hass: HomeAssistant, member: Member, chore: Chore) -> str:
    text = _text(hass)
    if chore.state is ChoreState.CLAIMED:
        return text["waiting"].format(name=member.name, chore=chore.name)
    return text["done"].format(name=member.name, chore=chore.name, points=chore.points)


@callback
def async_setup_handsfree(
    hass: HomeAssistant, entry: SternchenplanConfigEntry
) -> list[Callable[[], None]]:
    data = entry.runtime_data
    family = data.family

    async def on_tag(event: Event) -> None:
        tag_id = str(event.data.get("tag_id", ""))
        if not tag_id:
            return
        if chore_id := learning(hass):
            hass.data.pop(DATA_LEARN, None)
            try:
                chore = family.chore(chore_id)
            except FamilyError:
                return
            # Ein Aufkleber gehört zu genau einer Stelle: von anderen Aufgaben lösen
            # wäre zu streng, mehrere Aufgaben an der Mülltonne sind gewollt.
            chore.tag_id = tag_id
            await data.async_save()
            user = await hass.auth.async_get_user(event.context.user_id) if event.context.user_id else None
            parent = family.actor_for_user(user.id if user else None, is_admin=bool(user and user.is_admin))
            await _notify(hass, parent.member, _text(hass)["tag_learned"].format(chore=chore.name))
            return
        chores = family.chores_with_tag(tag_id)
        if not chores:
            return
        now = dt_util.utcnow()
        user_id = event.context.user_id
        member = next((m for m in family.members.values() if user_id and m.user_id == user_id), None)
        if member is None or member.role is not Role.CHILD:
            # Lesegerät ohne Kinderkonto: nur eindeutig zuordnen
            who = {m for c in chores for m in family.responsible(c, now)
                   if c in family.open_for(m, now)}
            if len(who) != 1:
                return
            member = family.members[who.pop()]
        done: list[Chore] = []
        # Nur was heute dran ist: nach dem Abhaken liegt die nächste Frist morgen.
        due_now = {c.id for c in family.open_for(member.id, now)}
        for chore in chores:
            if chore.id not in due_now:
                continue
            try:
                done.append(family.claim_hands_free(member.id, chore, now))
            except FamilyError as err:
                await _notify(hass, member, str(err))
        if not done:
            await _notify(hass, member, _text(hass)["tag_nothing"])
            return
        await data.async_save()
        for chore in done:
            await _notify(hass, member, _result(hass, member, chore))

    unsubs = [hass.bus.async_listen("tag_scanned", on_tag)]
    unsubs += _setup_voice(hass, entry)
    return unsubs


def _setup_voice(hass: HomeAssistant, entry: SternchenplanConfigEntry) -> list[Callable[[], None]]:
    try:
        from homeassistant.components.conversation.agent_manager import (  # noqa: PLC0415
            get_agent_manager,
        )
        from homeassistant.components.conversation.trigger import (  # noqa: PLC0415
            TriggerDetails,
        )
    except ImportError:  # Assist nicht installiert
        return []
    if "conversation" not in hass.config.components:
        return []

    data = entry.runtime_data
    family = data.family
    sentences = SENTENCES[_lang(hass)]

    def who(user_input, result) -> tuple[Member | None, str | None]:
        """Kind aus dem Satz („Lucas hat …“) oder aus dem HA-Konto des Geräts."""
        text = _text(hass)
        speaker = next(
            (m for m in family.members.values()
             if user_input.context.user_id and m.user_id == user_input.context.user_id),
            None,
        )
        if "name" in result.entities:
            spoken = str(result.entities["name"].value).strip()
            member = family.child_by_name(spoken)
            if member is None:
                return None, text["unknown_name"].format(spoken=spoken)
            if speaker and speaker.role is Role.CHILD and speaker.id != member.id:
                return None, text["only_self"]
            return member, None
        if speaker is None or speaker.role is not Role.CHILD:
            return None, text["who"]
        return speaker, None

    async def on_done(user_input, result) -> str | None:
        text = _text(hass)
        member, error = who(user_input, result)
        if member is None:
            return error
        spoken = str(result.entities["aufgabe"].value).strip()
        now = dt_util.utcnow()
        # Das Verb hilft beim Zuordnen: „Müll rausgebracht“ ↔ „Müll rausbringen“
        chore = family.match_chore(member.id, f"{spoken} {user_input.text.split()[-1]}", now)
        if chore is None:
            chore = family.match_chore(member.id, spoken, now)
        if chore is None:
            return text["unknown_chore"].format(spoken=spoken, name=member.name)
        try:
            family.claim_hands_free(member.id, chore, now)
        except FamilyError as err:
            return str(err)
        await data.async_save()
        return _result(hass, member, chore)

    async def on_open(user_input, result) -> str | None:
        text = _text(hass)
        member, error = who(user_input, result)
        if member is None:
            return error
        chores = family.open_for(member.id, dt_util.utcnow())
        if not chores:
            return text["nothing"].format(name=member.name)
        return text["open"].format(
            name=member.name, list=_spoken_list([c.name for c in chores], text["and"])
        )

    async def on_stars(user_input, result) -> str | None:
        member, error = who(user_input, result)
        if member is None:
            return error
        return _text(hass)["stars"].format(name=member.name, points=member.points)

    manager = get_agent_manager(hass)
    return [
        manager.register_trigger(TriggerDetails(sentences["done"], on_done)),
        manager.register_trigger(TriggerDetails(sentences["open"], on_open)),
        manager.register_trigger(TriggerDetails(sentences["stars"], on_stars)),
    ]
