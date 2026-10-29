"""Dienste von Familienplan. Jeder Aufruf wird über den Aufrufer geprüft."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING

import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.util import dt as dt_util

from .const import (
    PRO_ONLY,
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
)
from .consequences import next_release
from .takeover import takeover_terms
from .core import Actor, FamilyError, PermissionDenied, Recurrence

if TYPE_CHECKING:
    from . import FamilienplanData

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
    }
)

CLAIM_SCHEMA = CHORE_SCHEMA.extend({vol.Optional(ATTR_MEMBER): cv.string})

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


def _runtime(hass: HomeAssistant) -> FamilienplanData:
    entries = hass.config_entries.async_loaded_entries(DOMAIN)
    if not entries:
        raise ServiceValidationError("Familienplan ist nicht eingerichtet.")
    return entries[0].runtime_data


async def _actor(hass: HomeAssistant, call: ServiceCall, data: FamilienplanData) -> Actor:
    user_id = call.context.user_id
    user = await hass.auth.async_get_user(user_id) if user_id else None
    return actor_for_user(data, user_id, bool(user and user.is_admin))


def actor_for_user(data: FamilienplanData, user_id: str | None, is_admin: bool) -> Actor:
    return data.family.actor_for_user(user_id, is_admin=is_admin)


def _member_id(data: FamilienplanData, value: str) -> str:
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
    handler: Callable[[HomeAssistant, ServiceCall, FamilienplanData, Actor], Awaitable[None]],
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


def _require_pro(data: FamilienplanData) -> None:
    if not data.pro:
        raise FamilyError(PRO_ONLY)


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
    _require_pro(data)
    now = dt_util.utcnow()
    allowed, multiplier, max_per_day, day_start = takeover_terms(data.entry, now)
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
    _require_pro(data)
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
    from .reminders import notify_parents  # noqa: PLC0415

    redemption = data.family.redeem(
        actor, call.data[ATTR_REWARD_ID], _who(data, call, actor), dt_util.utcnow()
    )
    member = data.family.members[redemption.member_id]
    await notify_parents(hass, data.family, "redeemed", name=member.name, reward=redemption.reward_name)


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
    chore = data.family.chores.get(chore_id)
    if chore is not None and chore.photo == photo:
        chore.photo = None
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
    _require_pro(data)
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
    ):
        hass.services.async_register(DOMAIN, name, _guarded(handler), schema=schema)
