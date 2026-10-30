"""Dienste von Sternchenplan. Jeder Aufruf wird über den Aufrufer geprüft."""

from __future__ import annotations

from datetime import time
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING

import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.util import dt as dt_util

from .const import (
    CONF_PHOTO_DELETE_AFTER_REVIEW,
    CONF_CONSEQUENCES,
    CONF_LOCK_TIME,
    CONF_RELEASE_TIME,
    SERVICE_SET_LOCK,
    ATTR_ASSIGNEES,
    ATTR_CHORE_ID,
    ATTR_DEVICES,
    ATTR_DUE,
    ATTR_AGE,
    ATTR_MEMBER,
    ATTR_MIN_AGE,
    ATTR_NAME,
    ATTR_POINTS,
    ATTR_RECURRENCE,
    ATTR_REQUIRES_APPROVAL,
    ATTR_REQUIRES_PHOTO,
    ATTR_ROTATION,
    ATTR_START,
    ATTR_SUBSTITUTE,
    ATTR_UNTIL,
    DOMAIN,
    ATTR_COST,
    ATTR_MEMBERS,
    ATTR_MESSAGE,
    ATTR_REDEMPTION_ID,
    ATTR_REWARD_ID,
    SERVICE_APPROVE_REDEMPTION,
    SERVICE_CREATE_REWARD,
    SERVICE_DELETE_REWARD,
    SERVICE_REDEEM_REWARD,
    SERVICE_REJECT_REDEMPTION,
    SERVICE_UPDATE_REWARD,
    SERVICE_ANNOUNCE,
    SERVICE_APPROVE_CHORE,
    SERVICE_CLAIM_CHORE,
    SERVICE_CREATE_CHORE,
    SERVICE_DELETE_CHORE,
    SERVICE_END_ABSENCE,
    SERVICE_GRANT_PASS,
    SERVICE_REVOKE_PASS,
    SERVICE_SET_DEVICES,
    SERVICE_TAKE_OVER,
    SERVICE_REJECT_CHORE,
    SERVICE_SET_ABSENCE,
    SERVICE_SET_AGE,
    SERVICE_UNDO_CLAIM,
    SERVICE_UPDATE_CHORE,
    SERVICE_CLEAR_FAMILY_GOAL,
    SERVICE_SET_FAMILY_GOAL,
    SERVICE_SET_GOAL,
    ATTR_TARGET,
    ATTR_AMOUNT,
    ATTR_EUROS,
    ATTR_NOTE,
    ATTR_PAYDAY,
    ATTR_RATE,
    ATTR_DONE,
    ATTR_INDEX,
    ATTR_STEPS,
    SERVICE_CHECK_STEP,
    SERVICE_END_PAUSE,
    SERVICE_SET_PAUSE,
    SERVICE_SET_PICTURE_MODE,
    SERVICE_SET_THEME,
    SERVICE_SET_PHOTO_PRIVACY,
    ATTR_ENABLED,
    ATTR_THEME,
    ATTR_DELETE,
    ATTR_ICON,
    ATTR_OUTDOOR,
    ATTR_ENTITY,
    ATTR_DAY,
    ATTR_HOUR,
    SERVICE_SET_WEATHER,
    SERVICE_SET_REPORT,
    SERVICE_SEND_REPORT,
    SERVICE_GIVE_STARS,
    SERVICE_ADD_PRESET,
    SERVICE_DELETE_PRESET,
    SERVICE_LEARN_TAG,
    SERVICE_CLEAR_TAG,
    HOUSE_FIELDS,
    ATTR_STARS,
    ATTR_REASON,
    ATTR_PRESET_ID,
    ATTR_WEEKDAYS,
    SERVICE_ADJUST_MONEY,
    SERVICE_EXCHANGE_STARS,
    SERVICE_PAYOUT,
    SERVICE_SET_ALLOWANCE,
    SERVICE_SET_MONEY,
)
from .const import (
    ATTR_FEATURES,
    ATTR_HOURS,
    ATTR_MAX_MINUTES,
    ATTR_MINUTES,
    ATTR_OPTION,
    ATTR_OPTIONS,
    ATTR_PET,
    ATTR_QUESTION,
    SERVICE_BUY_SCREEN_TIME,
    SERVICE_CAST_VOTE,
    SERVICE_END_VOTE,
    SERVICE_SET_FEATURES,
    SERVICE_SET_LAMP,
    SERVICE_SET_PET,
    SERVICE_SET_SCREEN,
    SERVICE_SET_SCREEN_DEVICES,
    SERVICE_START_VOTE,
    SERVICE_STOP_SCREEN_TIME,
    SERVICE_TRIGGER_CHORE,
    SERVICE_FORGET_MEMBER,
    SERVICE_DELETE_PHOTO,
    ATTR_FILE,
    SERVICE_SET_PRIVATE_PUSH,
)
from .consequences import next_release
from .reminders import async_send_week_report, weather_is_bad
from .takeover import takeover_terms
from .core import FEATURES, PETS, THEMES, Actor, FamilyError, PermissionDenied, Recurrence

if TYPE_CHECKING:
    from . import SternchenplanData

CHORE_SCHEMA = vol.Schema({vol.Required(ATTR_CHORE_ID): cv.string})

CREATE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_NAME): cv.string,
        vol.Required(ATTR_ASSIGNEES): vol.All(cv.ensure_list, [cv.string]),
        vol.Optional(ATTR_POINTS, default=1): vol.All(vol.Coerce(int), vol.Range(min=0)),
        vol.Optional(ATTR_RECURRENCE, default=Recurrence.NONE.value): vol.In(
            [r.value for r in Recurrence]
        ),
        vol.Optional(ATTR_DUE): cv.datetime,
        vol.Optional(ATTR_ROTATION, default=False): cv.boolean,
        vol.Optional(ATTR_REQUIRES_APPROVAL, default=False): cv.boolean,
        vol.Optional(ATTR_REQUIRES_PHOTO, default=False): cv.boolean,
        vol.Optional(ATTR_MIN_AGE, default=0): vol.All(vol.Coerce(int), vol.Range(min=0, max=18)),
        vol.Optional(ATTR_STEPS, default=[]): vol.All(cv.ensure_list, [cv.string]),
        vol.Optional(ATTR_WEEKDAYS, default=[]): vol.All(cv.ensure_list, [vol.All(vol.Coerce(int), vol.Range(min=0, max=6))]),
        vol.Optional(ATTR_ICON, default=""): cv.string,
        vol.Optional(ATTR_OUTDOOR, default=False): cv.boolean,
        **{vol.Optional(k): cv.string for k in HOUSE_FIELDS},
    }
)

UPDATE_SCHEMA = CHORE_SCHEMA.extend(
    {
        vol.Optional(ATTR_NAME): cv.string,
        vol.Optional(ATTR_ASSIGNEES): vol.All(cv.ensure_list, [cv.string]),
        vol.Optional(ATTR_POINTS): vol.All(vol.Coerce(int), vol.Range(min=0)),
        vol.Optional(ATTR_RECURRENCE): vol.In([r.value for r in Recurrence]),
        # Leerer Text oder null löscht die Frist.
        vol.Optional(ATTR_DUE): vol.Any(None, vol.All(cv.string, vol.Length(max=0)), cv.datetime),
        vol.Optional(ATTR_ROTATION): cv.boolean,
        vol.Optional(ATTR_REQUIRES_APPROVAL): cv.boolean,
        vol.Optional(ATTR_REQUIRES_PHOTO): cv.boolean,
        vol.Optional(ATTR_MIN_AGE): vol.All(vol.Coerce(int), vol.Range(min=0, max=18)),
        vol.Optional(ATTR_STEPS): vol.All(cv.ensure_list, [cv.string]),
        vol.Optional(ATTR_WEEKDAYS): vol.All(cv.ensure_list, [vol.All(vol.Coerce(int), vol.Range(min=0, max=6))]),
        vol.Optional(ATTR_ICON): cv.string,
        vol.Optional(ATTR_OUTDOOR): cv.boolean,
        **{vol.Optional(k): cv.string for k in HOUSE_FIELDS},
    }
)

CLAIM_SCHEMA = CHORE_SCHEMA.extend({vol.Optional(ATTR_MEMBER): cv.string})
STEP_SCHEMA = CLAIM_SCHEMA.extend(
    {vol.Required(ATTR_INDEX): vol.All(vol.Coerce(int), vol.Range(min=0)),
     vol.Optional(ATTR_DONE, default=True): cv.boolean}
)

ABSENCE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_MEMBER): cv.string,
        vol.Required(ATTR_UNTIL): cv.datetime,
        vol.Optional(ATTR_START): cv.datetime,
        vol.Optional(ATTR_SUBSTITUTE): cv.string,
    }
)

END_ABSENCE_SCHEMA = vol.Schema({vol.Required(ATTR_MEMBER): cv.string})

DEVICES_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_MEMBER): cv.string,
        vol.Required(ATTR_DEVICES): vol.All(cv.ensure_list, [cv.entity_domain("switch")]),
    }
)

PASS_SCHEMA = vol.Schema(
    {vol.Required(ATTR_MEMBER): cv.string, vol.Optional(ATTR_UNTIL): cv.datetime}
)


AGE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_MEMBER): cv.string,
        vol.Required(ATTR_AGE): vol.Any(None, vol.All(vol.Coerce(int), vol.Range(min=0, max=120))),
    }
)

ANNOUNCE_SCHEMA = vol.Schema({vol.Optional(ATTR_MESSAGE): cv.string})

_COST = vol.All(vol.Coerce(int), vol.Range(min=1, max=100000))
CREATE_REWARD_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_NAME): cv.string,
        vol.Required(ATTR_COST): _COST,
        vol.Optional(ATTR_MEMBERS, default=[]): vol.All(cv.ensure_list, [cv.string]),
    }
)
UPDATE_REWARD_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_REWARD_ID): cv.string,
        vol.Optional(ATTR_NAME): cv.string,
        vol.Optional(ATTR_COST): _COST,
        vol.Optional(ATTR_MEMBERS): vol.All(cv.ensure_list, [cv.string]),
    }
)
REWARD_SCHEMA = vol.Schema({vol.Required(ATTR_REWARD_ID): cv.string})
REDEEM_SCHEMA = REWARD_SCHEMA.extend({vol.Optional(ATTR_MEMBER): cv.string})
REDEMPTION_SCHEMA = vol.Schema({vol.Required(ATTR_REDEMPTION_ID): cv.string})
# Ohne reward_id (oder leer) wird das Sparziel gelöscht.
GOAL_SCHEMA = vol.Schema(
    {vol.Optional(ATTR_REWARD_ID): vol.Any(None, cv.string), vol.Optional(ATTR_MEMBER): cv.string}
)
FAMILY_GOAL_SCHEMA = vol.Schema(
    {vol.Required(ATTR_NAME): cv.string, vol.Required(ATTR_TARGET): _COST}
)
EMPTY_SCHEMA = vol.Schema({})
PAUSE_SCHEMA = vol.Schema({vol.Optional(ATTR_START): cv.datetime, vol.Required(ATTR_UNTIL): cv.datetime})
WEATHER_SCHEMA = vol.Schema({vol.Optional(ATTR_ENTITY, default=""): vol.Any("", cv.entity_domain("weather"))})
REPORT_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_DAY): vol.All(vol.Coerce(int), vol.Range(min=-1, max=6)),
        vol.Optional(ATTR_HOUR, default=18): vol.All(vol.Coerce(int), vol.Range(min=0, max=23)),
    }
)
_STARS = vol.All(vol.Coerce(int), vol.Range(min=-100, max=100))
GIVE_STARS_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_MEMBER): cv.string,
        vol.Required(ATTR_STARS): _STARS,
        vol.Optional(ATTR_REASON, default=""): cv.string,
    }
)
ADD_PRESET_SCHEMA = vol.Schema({vol.Required(ATTR_NAME): cv.string, vol.Required(ATTR_STARS): _STARS})
DELETE_PRESET_SCHEMA = vol.Schema({vol.Required(ATTR_PRESET_ID): cv.string})
PICTURE_SCHEMA = vol.Schema({vol.Required(ATTR_MEMBER): cv.string, vol.Required(ATTR_ENABLED): cv.boolean})
PHOTO_PRIVACY_SCHEMA = vol.Schema({vol.Required(ATTR_DELETE): cv.boolean})


def _clock(value) -> str:
    """Uhrzeit als HH:MM, auch aus "20:00:00"."""
    try:
        return time.fromisoformat(str(value).strip()).strftime("%H:%M")
    except ValueError as err:
        raise vol.Invalid(f"Keine Uhrzeit: {value}") from err


LOCK_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_ENABLED): cv.boolean,
        vol.Optional(CONF_LOCK_TIME): _clock,
        vol.Optional(CONF_RELEASE_TIME): _clock,
    }
)
THEME_SCHEMA = vol.Schema({vol.Required(ATTR_MEMBER): cv.string, vol.Optional(ATTR_THEME, default=""): vol.In(THEMES)})
_EURO = vol.All(vol.Coerce(float), vol.Range(min=-10000, max=10000))
MONEY_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_RATE): vol.All(vol.Coerce(int), vol.Range(min=0, max=10000)),
        vol.Optional(ATTR_PAYDAY, default=6): vol.All(vol.Coerce(int), vol.Range(min=0, max=6)),
    }
)
ALLOWANCE_SCHEMA = vol.Schema(
    {vol.Required(ATTR_MEMBER): cv.string, vol.Required(ATTR_AMOUNT): vol.All(_EURO, vol.Range(min=0))}
)
EXCHANGE_SCHEMA = vol.Schema(
    {vol.Required(ATTR_EUROS): vol.All(vol.Coerce(int), vol.Range(min=1, max=1000)),
     vol.Optional(ATTR_MEMBER): cv.string}
)
PAYOUT_SCHEMA = vol.Schema(
    {vol.Required(ATTR_MEMBER): cv.string, vol.Optional(ATTR_AMOUNT): vol.All(_EURO, vol.Range(min=0.01))}
)
ADJUST_SCHEMA = vol.Schema(
    {vol.Required(ATTR_MEMBER): cv.string, vol.Required(ATTR_AMOUNT): _EURO,
     vol.Optional(ATTR_NOTE, default=""): cv.string}
)


FEATURES_SCHEMA = vol.Schema(
    {vol.Required(ATTR_FEATURES): vol.All(cv.ensure_list, [vol.In(FEATURES)])}
)
PET_SCHEMA = vol.Schema(
    {vol.Required(ATTR_MEMBER): cv.string, vol.Optional(ATTR_PET, default=""): vol.In(("", *PETS)),
     vol.Optional(ATTR_NAME, default=""): cv.string}
)
LAMP_SCHEMA = vol.Schema({vol.Required(ATTR_MEMBER): cv.string, vol.Optional(ATTR_ENTITY, default=""): cv.string})
SCREEN_SCHEMA = vol.Schema(
    {vol.Required(ATTR_RATE): vol.All(vol.Coerce(int), vol.Range(min=0, max=60)),
     vol.Optional(ATTR_MAX_MINUTES, default=60): vol.All(vol.Coerce(int), vol.Range(min=5, max=600))}
)
SCREEN_DEVICES_SCHEMA = vol.Schema(
    {vol.Required(ATTR_MEMBER): cv.string, vol.Optional(ATTR_DEVICES, default=[]): cv.entity_ids}
)
BUY_SCREEN_SCHEMA = vol.Schema(
    {vol.Required(ATTR_MINUTES): vol.All(vol.Coerce(int), vol.Range(min=5, max=600)),
     vol.Optional(ATTR_MEMBER): cv.string}
)
MEMBER_OPTIONAL_SCHEMA = vol.Schema({vol.Optional(ATTR_MEMBER): cv.string})
VOTE_SCHEMA = vol.Schema(
    {vol.Required(ATTR_QUESTION): cv.string,
     vol.Required(ATTR_OPTIONS): vol.All(cv.ensure_list, [cv.string]),
     vol.Optional(ATTR_HOURS, default=24): vol.All(vol.Coerce(int), vol.Range(min=1, max=168))}
)
CAST_VOTE_SCHEMA = vol.Schema(
    {vol.Required(ATTR_OPTION): vol.All(vol.Coerce(int), vol.Range(min=0, max=9)),
     vol.Optional(ATTR_MEMBER): cv.string}
)


def _cents(euros: float) -> int:
    return round(euros * 100)


def _runtime(hass: HomeAssistant) -> SternchenplanData:
    entries = hass.config_entries.async_loaded_entries(DOMAIN)
    if not entries:
        raise ServiceValidationError("Sternchenplan ist nicht eingerichtet.")
    return entries[0].runtime_data


async def _actor(hass: HomeAssistant, call: ServiceCall, data: SternchenplanData) -> Actor:
    user_id = call.context.user_id
    user = await hass.auth.async_get_user(user_id) if user_id else None
    return actor_for_user(data, user_id, bool(user and user.is_admin))


def actor_for_user(data: SternchenplanData, user_id: str | None, is_admin: bool) -> Actor:
    return data.family.actor_for_user(user_id, is_admin=is_admin)


def _member_id(data: SternchenplanData, value: str) -> str:
    """Mitglied per ID oder Name (Groß-/Kleinschreibung egal)."""
    family = data.family
    if value in family.members:
        return value
    wanted = value.strip().casefold()
    for member in family.members.values():
        if member.name.casefold() == wanted:
            return member.id
    raise ServiceValidationError(f"Unbekanntes Familienmitglied: {value}")


def _guarded(
    handler: Callable[[HomeAssistant, ServiceCall, SternchenplanData, Actor], Awaitable[None]],
) -> Callable[[ServiceCall], Awaitable[None]]:
    async def wrapper(call: ServiceCall) -> None:
        hass = call.hass
        data = _runtime(hass)
        actor = await _actor(hass, call, data)
        try:
            await handler(hass, call, data, actor)
        except FamilyError as err:
            # Regeln verletzt oder keine Berechtigung: nichts wurde geändert.
            raise ServiceValidationError(str(err)) from err
        await data.async_save()

    return wrapper


def _utc(value):
    """Zeit aus dem Dienstaufruf. Ohne Zeitzone gilt die HA-Zeitzone."""
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=dt_util.get_default_time_zone())
    return dt_util.as_utc(value)


async def _create(hass, call, data, actor) -> None:
    due = _utc(call.data.get(ATTR_DUE))
    data.family.create_chore(
        actor,
        call.data[ATTR_NAME],
        [_member_id(data, a) for a in call.data[ATTR_ASSIGNEES]],
        points=call.data[ATTR_POINTS],
        recurrence=Recurrence(call.data[ATTR_RECURRENCE]),
        due=due,
        rotation=call.data[ATTR_ROTATION],
        requires_approval=call.data[ATTR_REQUIRES_APPROVAL],
        requires_photo=call.data[ATTR_REQUIRES_PHOTO],
        min_age=call.data[ATTR_MIN_AGE],
        steps=call.data[ATTR_STEPS],
        weekdays=call.data[ATTR_WEEKDAYS],
        icon=call.data[ATTR_ICON],
        outdoor=call.data[ATTR_OUTDOOR],
        house={k: call.data[k] for k in HOUSE_FIELDS if k in call.data},
    )


async def _update(hass, call, data, actor) -> None:
    d = call.data
    due = d.get(ATTR_DUE)
    data.family.update_chore(
        actor,
        d[ATTR_CHORE_ID],
        dt_util.utcnow(),
        name=d.get(ATTR_NAME),
        assignees=(
            [_member_id(data, a) for a in d[ATTR_ASSIGNEES]] if ATTR_ASSIGNEES in d else None
        ),
        points=d.get(ATTR_POINTS),
        recurrence=Recurrence(d[ATTR_RECURRENCE]) if ATTR_RECURRENCE in d else None,
        due=_utc(due) if due else None,
        clear_due=ATTR_DUE in d and not due,
        rotation=d.get(ATTR_ROTATION),
        requires_approval=d.get(ATTR_REQUIRES_APPROVAL),
        requires_photo=d.get(ATTR_REQUIRES_PHOTO),
        min_age=d.get(ATTR_MIN_AGE),
        steps=d.get(ATTR_STEPS),
        weekdays=d.get(ATTR_WEEKDAYS),
        icon=d.get(ATTR_ICON),
        outdoor=d.get(ATTR_OUTDOOR),
        house={k: d[k] for k in HOUSE_FIELDS if k in d},
    )


async def _delete(hass, call, data, actor) -> None:
    data.family.delete_chore(actor, call.data[ATTR_CHORE_ID])


def _who(data, call, actor) -> str:
    if ATTR_MEMBER in call.data:
        return _member_id(data, call.data[ATTR_MEMBER])
    if actor.member is not None:
        return actor.member.id
    raise ServiceValidationError("Bitte angeben, wer die Aufgabe erledigt hat.")


async def _claim(hass, call, data, actor) -> None:
    data.family.claim(actor, call.data[ATTR_CHORE_ID], _who(data, call, actor), dt_util.utcnow())


def take_over(data, actor, chore_id: str, member_id: str, photo: str | None = None) -> None:
    """Gemeinsam für Dienst und Foto-Upload."""
    now = dt_util.utcnow()
    allowed, multiplier, max_per_day, day_start = takeover_terms(data.entry, now)
    if not data.family.has("helping"):
        raise FamilyError("Geschwistern helfen ist ausgeschaltet.")
    if not allowed and not actor.is_manager:
        raise FamilyError("Übernehmen geht erst später am Tag.")
    data.family.take_over(
        actor, chore_id, member_id, now,
        multiplier=multiplier, max_per_day=max_per_day, day_start=day_start, photo=photo,
    )


async def _take_over(hass, call, data, actor) -> None:
    take_over(data, actor, call.data[ATTR_CHORE_ID], _who(data, call, actor))


async def _announce(hass, call, data, actor) -> None:
    """Jetzt ansagen: eigener Text oder, ohne Text, was heute noch offen ist."""
    from .reminders import _text, announce_configured, announcement, async_announce  # noqa: PLC0415

    if not actor.is_manager:
        raise PermissionDenied("Nur Eltern können Ansagen machen.")
    if not announce_configured(data.entry):
        raise FamilyError("Es sind keine Lautsprecher eingestellt.")
    message = call.data.get(ATTR_MESSAGE) or announcement(
        hass, data.family, dt_util.utcnow()
    ) or _text(hass)["say_done"]
    await async_announce(hass, data.entry, message)


async def _create_reward(hass, call, data, actor) -> None:
    data.family.create_reward(
        actor,
        call.data[ATTR_NAME],
        call.data[ATTR_COST],
        [_member_id(data, m) for m in call.data[ATTR_MEMBERS]],
    )


async def _update_reward(hass, call, data, actor) -> None:
    d = call.data
    data.family.update_reward(
        actor,
        d[ATTR_REWARD_ID],
        name=d.get(ATTR_NAME),
        cost=d.get(ATTR_COST),
        members=[_member_id(data, m) for m in d[ATTR_MEMBERS]] if ATTR_MEMBERS in d else None,
    )


async def _delete_reward(hass, call, data, actor) -> None:
    data.family.delete_reward(actor, call.data[ATTR_REWARD_ID])


async def _redeem(hass, call, data, actor) -> None:
    # Die Eltern fragt async_celebrate per Push mit Knöpfen.
    data.family.redeem(actor, call.data[ATTR_REWARD_ID], _who(data, call, actor), dt_util.utcnow())


async def _approve_redemption(hass, call, data, actor) -> None:
    data.family.approve_redemption(actor, call.data[ATTR_REDEMPTION_ID], dt_util.utcnow())


async def _reject_redemption(hass, call, data, actor) -> None:
    data.family.reject_redemption(actor, call.data[ATTR_REDEMPTION_ID], dt_util.utcnow())


async def _set_age(hass, call, data, actor) -> None:
    data.family.set_age(
        actor, _member_id(data, call.data[ATTR_MEMBER]), call.data[ATTR_AGE], dt_util.utcnow()
    )


async def _drop_photo(hass, data, chore_id: str, photo: str | None, always: bool) -> None:
    """Foto nach der Entscheidung löschen, wenn die Familie das so eingestellt hat.

    Zurückgenommene Meldungen verlieren ihr Foto immer, es gehört zu nichts mehr.
    """
    from .photos import async_discard, delete_after_review  # noqa: PLC0415

    if photo is None or not (always or delete_after_review(data.entry)):
        return
    data.family.forget_photos([photo])
    await async_discard(hass, photo)


async def _undo(hass, call, data, actor) -> None:
    chore = data.family.chore(call.data[ATTR_CHORE_ID])
    photo = chore.photo
    data.family.undo_claim(actor, chore.id)
    await _drop_photo(hass, data, chore.id, photo, always=True)


async def _approve(hass, call, data, actor) -> None:
    chore = data.family.chore(call.data[ATTR_CHORE_ID])
    photo = chore.photo
    data.family.approve(actor, chore.id, dt_util.utcnow())
    await _drop_photo(hass, data, chore.id, photo, always=False)


async def _reject(hass, call, data, actor) -> None:
    chore = data.family.chore(call.data[ATTR_CHORE_ID])
    photo = chore.photo
    data.family.reject(actor, chore.id, dt_util.utcnow())
    await _drop_photo(hass, data, chore.id, photo, always=False)


async def _set_absence(hass, call, data, actor) -> None:
    substitute = call.data.get(ATTR_SUBSTITUTE)
    data.family.set_absence(
        actor,
        _member_id(data, call.data[ATTR_MEMBER]),
        _utc(call.data[ATTR_UNTIL]),
        start=_utc(call.data.get(ATTR_START)),
        substitute_id=_member_id(data, substitute) if substitute else None,
    )


async def _end_absence(hass, call, data, actor) -> None:
    data.family.end_absence(actor, _member_id(data, call.data[ATTR_MEMBER]))


async def _set_devices(hass, call, data, actor) -> None:
    data.family.set_devices(
        actor, _member_id(data, call.data[ATTR_MEMBER]), call.data[ATTR_DEVICES]
    )


async def _grant_pass(hass, call, data, actor) -> None:
    until = _utc(call.data.get(ATTR_UNTIL)) or next_release(data.entry, dt_util.utcnow())
    data.family.grant_pass(actor, _member_id(data, call.data[ATTR_MEMBER]), until)


async def _revoke_pass(hass, call, data, actor) -> None:
    data.family.revoke_pass(actor, _member_id(data, call.data[ATTR_MEMBER]))


@callback
async def _set_goal(hass, call, data, actor) -> None:
    data.family.set_goal(actor, _who(data, call, actor), call.data.get(ATTR_REWARD_ID) or None)


async def _set_family_goal(hass, call, data, actor) -> None:
    data.family.set_family_goal(actor, call.data[ATTR_NAME], call.data[ATTR_TARGET], dt_util.utcnow())


async def _clear_family_goal(hass, call, data, actor) -> None:
    data.family.clear_family_goal(actor)


async def _set_money(hass, call, data, actor) -> None:
    data.family.set_money(actor, call.data[ATTR_RATE], call.data[ATTR_PAYDAY])


async def _set_allowance(hass, call, data, actor) -> None:
    data.family.set_allowance(
        actor, _member_id(data, call.data[ATTR_MEMBER]), _cents(call.data[ATTR_AMOUNT]), dt_util.utcnow()
    )


async def _exchange(hass, call, data, actor) -> None:
    data.family.exchange(actor, _who(data, call, actor), call.data[ATTR_EUROS], dt_util.utcnow())


async def _payout(hass, call, data, actor) -> None:
    amount = call.data.get(ATTR_AMOUNT)
    data.family.payout(
        actor, _member_id(data, call.data[ATTR_MEMBER]),
        None if amount is None else _cents(amount), dt_util.utcnow(),
    )


async def _adjust_money(hass, call, data, actor) -> None:
    data.family.adjust_money(
        actor, _member_id(data, call.data[ATTR_MEMBER]), _cents(call.data[ATTR_AMOUNT]),
        call.data[ATTR_NOTE], dt_util.utcnow(),
    )


async def _check_step(hass, call, data, actor) -> None:
    d = call.data
    data.family.check_step(
        actor, d[ATTR_CHORE_ID], _who(data, call, actor), d[ATTR_INDEX], d[ATTR_DONE], dt_util.utcnow()
    )


async def _set_pause(hass, call, data, actor) -> None:
    start = _utc(call.data.get(ATTR_START)) or dt_util.utcnow()
    data.family.set_pause(actor, start, _utc(call.data[ATTR_UNTIL]))


async def _end_pause(hass, call, data, actor) -> None:
    data.family.end_pause(actor, dt_util.utcnow())


async def _set_picture_mode(hass, call, data, actor) -> None:
    data.family.set_picture_mode(actor, _member_id(data, call.data[ATTR_MEMBER]), call.data[ATTR_ENABLED])


async def _set_theme(hass, call, data, actor) -> None:
    data.family.set_theme(actor, _member_id(data, call.data[ATTR_MEMBER]), call.data[ATTR_THEME])


async def _set_photo_privacy(hass, call, data, actor) -> None:
    """Fotos nach der Entscheidung löschen oder behalten (Willkommens-Assistent)."""
    if not actor.is_manager:
        raise PermissionDenied("Nur Eltern.")
    hass.config_entries.async_update_entry(
        data.entry,
        options={**data.entry.options, CONF_PHOTO_DELETE_AFTER_REVIEW: call.data[ATTR_DELETE]},
    )


async def _set_lock(hass, call, data, actor) -> None:
    """Internetsperre an/aus und Sperrzeiten (Karte: Einstellungen, Assistent)."""
    if not actor.is_manager:
        raise PermissionDenied("Nur Eltern.")
    options = dict(data.entry.options)
    if ATTR_ENABLED in call.data:
        options[CONF_CONSEQUENCES] = call.data[ATTR_ENABLED]
    for key in (CONF_LOCK_TIME, CONF_RELEASE_TIME):
        if key in call.data:
            options[key] = call.data[key]
    hass.config_entries.async_update_entry(data.entry, options=options)


async def _set_weather(hass, call, data, actor) -> None:
    data.family.set_weather(actor, call.data[ATTR_ENTITY])
    data.family.bad_weather = weather_is_bad(hass, data.family.weather_entity)


async def _set_report(hass, call, data, actor) -> None:
    data.family.set_report(actor, call.data[ATTR_DAY], call.data[ATTR_HOUR])


async def _send_report(hass, call, data, actor) -> None:
    if not actor.is_manager:
        raise PermissionDenied("Nur Eltern.")
    await async_send_week_report(hass, data.family, dt_util.utcnow())


async def _give_stars(hass, call, data, actor) -> None:
    d = call.data
    data.family.give_stars(
        actor, _member_id(data, d[ATTR_MEMBER]), d[ATTR_STARS], d[ATTR_REASON], dt_util.utcnow()
    )


async def _add_preset(hass, call, data, actor) -> None:
    data.family.add_preset(actor, call.data[ATTR_NAME], call.data[ATTR_STARS])


async def _delete_preset(hass, call, data, actor) -> None:
    data.family.delete_preset(actor, call.data[ATTR_PRESET_ID])


async def _learn_tag(hass, call, data, actor) -> None:
    from .handsfree import start_learning  # noqa: PLC0415

    if not actor.is_manager:
        raise PermissionDenied("Nur Eltern.")
    data.family.chore(call.data[ATTR_CHORE_ID])
    start_learning(hass, call.data[ATTR_CHORE_ID])


async def _clear_tag(hass, call, data, actor) -> None:
    data.family.set_tag(actor, call.data[ATTR_CHORE_ID], "")


async def _set_private_push(hass, call, data, actor) -> None:
    data.family.set_private_push(actor, call.data[ATTR_ENABLED])


async def _forget_member(hass, call, data, actor) -> None:
    """Person mit allen Spuren löschen, auch ihre Fotos."""
    from .photos import async_discard  # noqa: PLC0415

    for photo in data.family.remove_member(actor, _member_id(data, call.data[ATTR_MEMBER])):
        await async_discard(hass, photo)


async def _delete_photo(hass, call, data, actor) -> None:
    from .photos import async_discard  # noqa: PLC0415

    data.family.delete_photo(actor, call.data[ATTR_FILE])
    await async_discard(hass, call.data[ATTR_FILE])


async def _set_features(hass, call, data, actor) -> None:
    data.family.set_features(actor, call.data[ATTR_FEATURES])


async def _set_pet(hass, call, data, actor) -> None:
    d = call.data
    data.family.set_pet(actor, _member_id(data, d[ATTR_MEMBER]), d[ATTR_PET], d[ATTR_NAME])


async def _set_lamp(hass, call, data, actor) -> None:
    data.family.set_lamp(actor, _member_id(data, call.data[ATTR_MEMBER]), call.data[ATTR_ENTITY])


async def _set_screen(hass, call, data, actor) -> None:
    data.family.set_screen(actor, call.data[ATTR_RATE], call.data[ATTR_MAX_MINUTES])


async def _set_screen_devices(hass, call, data, actor) -> None:
    data.family.set_screen_devices(actor, _member_id(data, call.data[ATTR_MEMBER]), call.data[ATTR_DEVICES])


async def _buy_screen(hass, call, data, actor) -> None:
    data.family.buy_screen_time(actor, _who(data, call, actor), call.data[ATTR_MINUTES], dt_util.utcnow())


async def _stop_screen(hass, call, data, actor) -> None:
    data.family.stop_screen_time(actor, _who(data, call, actor), dt_util.utcnow())


async def _trigger_chore(hass, call, data, actor) -> None:
    data.family.trigger_chore(actor, call.data[ATTR_CHORE_ID], dt_util.utcnow())


async def _start_vote(hass, call, data, actor) -> None:
    d = call.data
    data.family.start_vote(actor, d[ATTR_QUESTION], d[ATTR_OPTIONS], d[ATTR_HOURS], dt_util.utcnow())


async def _cast_vote(hass, call, data, actor) -> None:
    data.family.cast_vote(actor, _who(data, call, actor), call.data[ATTR_OPTION], dt_util.utcnow())


async def _end_vote(hass, call, data, actor) -> None:
    data.family.end_vote(actor, dt_util.utcnow())


def async_register_services(hass: HomeAssistant) -> None:
    for name, handler, schema in (
        (SERVICE_CREATE_CHORE, _create, CREATE_SCHEMA),
        (SERVICE_UPDATE_CHORE, _update, UPDATE_SCHEMA),
        (SERVICE_DELETE_CHORE, _delete, CHORE_SCHEMA),
        (SERVICE_CLAIM_CHORE, _claim, CLAIM_SCHEMA),
        (SERVICE_TAKE_OVER, _take_over, CLAIM_SCHEMA),
        (SERVICE_UNDO_CLAIM, _undo, CHORE_SCHEMA),
        (SERVICE_APPROVE_CHORE, _approve, CHORE_SCHEMA),
        (SERVICE_REJECT_CHORE, _reject, CHORE_SCHEMA),
        (SERVICE_SET_ABSENCE, _set_absence, ABSENCE_SCHEMA),
        (SERVICE_END_ABSENCE, _end_absence, END_ABSENCE_SCHEMA),
        (SERVICE_SET_DEVICES, _set_devices, DEVICES_SCHEMA),
        (SERVICE_GRANT_PASS, _grant_pass, PASS_SCHEMA),
        (SERVICE_REVOKE_PASS, _revoke_pass, END_ABSENCE_SCHEMA),
        (SERVICE_ANNOUNCE, _announce, ANNOUNCE_SCHEMA),
        (SERVICE_SET_AGE, _set_age, AGE_SCHEMA),
        (SERVICE_CREATE_REWARD, _create_reward, CREATE_REWARD_SCHEMA),
        (SERVICE_UPDATE_REWARD, _update_reward, UPDATE_REWARD_SCHEMA),
        (SERVICE_DELETE_REWARD, _delete_reward, REWARD_SCHEMA),
        (SERVICE_REDEEM_REWARD, _redeem, REDEEM_SCHEMA),
        (SERVICE_APPROVE_REDEMPTION, _approve_redemption, REDEMPTION_SCHEMA),
        (SERVICE_REJECT_REDEMPTION, _reject_redemption, REDEMPTION_SCHEMA),
        (SERVICE_SET_GOAL, _set_goal, GOAL_SCHEMA),
        (SERVICE_SET_FAMILY_GOAL, _set_family_goal, FAMILY_GOAL_SCHEMA),
        (SERVICE_CLEAR_FAMILY_GOAL, _clear_family_goal, EMPTY_SCHEMA),
        (SERVICE_SET_MONEY, _set_money, MONEY_SCHEMA),
        (SERVICE_CHECK_STEP, _check_step, STEP_SCHEMA),
        (SERVICE_SET_PAUSE, _set_pause, PAUSE_SCHEMA),
        (SERVICE_END_PAUSE, _end_pause, EMPTY_SCHEMA),
        (SERVICE_SET_PICTURE_MODE, _set_picture_mode, PICTURE_SCHEMA),
        (SERVICE_SET_THEME, _set_theme, THEME_SCHEMA),
        (SERVICE_SET_PHOTO_PRIVACY, _set_photo_privacy, PHOTO_PRIVACY_SCHEMA),
        (SERVICE_SET_LOCK, _set_lock, LOCK_SCHEMA),
        (SERVICE_SET_WEATHER, _set_weather, WEATHER_SCHEMA),
        (SERVICE_SET_REPORT, _set_report, REPORT_SCHEMA),
        (SERVICE_SEND_REPORT, _send_report, EMPTY_SCHEMA),
        (SERVICE_GIVE_STARS, _give_stars, GIVE_STARS_SCHEMA),
        (SERVICE_ADD_PRESET, _add_preset, ADD_PRESET_SCHEMA),
        (SERVICE_DELETE_PRESET, _delete_preset, DELETE_PRESET_SCHEMA),
        (SERVICE_LEARN_TAG, _learn_tag, CHORE_SCHEMA),
        (SERVICE_CLEAR_TAG, _clear_tag, CHORE_SCHEMA),
        (SERVICE_SET_ALLOWANCE, _set_allowance, ALLOWANCE_SCHEMA),
        (SERVICE_EXCHANGE_STARS, _exchange, EXCHANGE_SCHEMA),
        (SERVICE_PAYOUT, _payout, PAYOUT_SCHEMA),
        (SERVICE_ADJUST_MONEY, _adjust_money, ADJUST_SCHEMA),
        (SERVICE_SET_FEATURES, _set_features, FEATURES_SCHEMA),
        (SERVICE_SET_PET, _set_pet, PET_SCHEMA),
        (SERVICE_SET_LAMP, _set_lamp, LAMP_SCHEMA),
        (SERVICE_SET_SCREEN, _set_screen, SCREEN_SCHEMA),
        (SERVICE_SET_SCREEN_DEVICES, _set_screen_devices, SCREEN_DEVICES_SCHEMA),
        (SERVICE_BUY_SCREEN_TIME, _buy_screen, BUY_SCREEN_SCHEMA),
        (SERVICE_STOP_SCREEN_TIME, _stop_screen, MEMBER_OPTIONAL_SCHEMA),
        (SERVICE_TRIGGER_CHORE, _trigger_chore, CHORE_SCHEMA),
        (SERVICE_START_VOTE, _start_vote, VOTE_SCHEMA),
        (SERVICE_CAST_VOTE, _cast_vote, CAST_VOTE_SCHEMA),
        (SERVICE_END_VOTE, _end_vote, EMPTY_SCHEMA),
        (SERVICE_SET_PRIVATE_PUSH, _set_private_push, vol.Schema({vol.Required(ATTR_ENABLED): cv.boolean})),
        (SERVICE_FORGET_MEMBER, _forget_member, vol.Schema({vol.Required(ATTR_MEMBER): cv.string})),
        (SERVICE_DELETE_PHOTO, _delete_photo, vol.Schema({vol.Required(ATTR_FILE): cv.string})),
    ):
        hass.services.async_register(DOMAIN, name, _guarded(handler), schema=schema)
