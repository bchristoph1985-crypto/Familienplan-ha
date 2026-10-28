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
    ATTR_ASSIGNEES,
    ATTR_CHORE_ID,
    ATTR_DUE,
    ATTR_MEMBER,
    ATTR_NAME,
    ATTR_POINTS,
    ATTR_RECURRENCE,
    ATTR_REQUIRES_APPROVAL,
    ATTR_ROTATION,
    DOMAIN,
    SERVICE_APPROVE_CHORE,
    SERVICE_CLAIM_CHORE,
    SERVICE_CREATE_CHORE,
    SERVICE_DELETE_CHORE,
    SERVICE_REJECT_CHORE,
    SERVICE_UNDO_CLAIM,
)
from .core import Actor, FamilyError, Recurrence

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
    }
)

CLAIM_SCHEMA = CHORE_SCHEMA.extend({vol.Optional(ATTR_MEMBER): cv.string})


def _runtime(hass: HomeAssistant) -> FamilienplanData:
    entries = hass.config_entries.async_loaded_entries(DOMAIN)
    if not entries:
        raise ServiceValidationError("Familienplan ist nicht eingerichtet.")
    return entries[0].runtime_data


async def _actor(hass: HomeAssistant, call: ServiceCall, data: FamilienplanData) -> Actor:
    user_id = call.context.user_id
    user = await hass.auth.async_get_user(user_id) if user_id else None
    return data.family.actor_for_user(user_id, is_admin=bool(user and user.is_admin))


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


async def _create(hass, call, data, actor) -> None:
    due = call.data.get(ATTR_DUE)
    if due is not None:
        due = dt_util.as_utc(due if due.tzinfo else due.replace(tzinfo=dt_util.get_default_time_zone()))
    data.family.create_chore(
        actor,
        call.data[ATTR_NAME],
        [_member_id(data, a) for a in call.data[ATTR_ASSIGNEES]],
        points=call.data[ATTR_POINTS],
        recurrence=Recurrence(call.data[ATTR_RECURRENCE]),
        due=due,
        rotation=call.data[ATTR_ROTATION],
        requires_approval=call.data[ATTR_REQUIRES_APPROVAL],
    )


async def _delete(hass, call, data, actor) -> None:
    data.family.delete_chore(actor, call.data[ATTR_CHORE_ID])


async def _claim(hass, call, data, actor) -> None:
    if ATTR_MEMBER in call.data:
        member_id = _member_id(data, call.data[ATTR_MEMBER])
    elif actor.member is not None:
        member_id = actor.member.id
    else:
        raise ServiceValidationError("Bitte angeben, wer die Aufgabe erledigt hat.")
    data.family.claim(actor, call.data[ATTR_CHORE_ID], member_id, dt_util.utcnow())


async def _undo(hass, call, data, actor) -> None:
    data.family.undo_claim(actor, call.data[ATTR_CHORE_ID])


async def _approve(hass, call, data, actor) -> None:
    data.family.approve(actor, call.data[ATTR_CHORE_ID], dt_util.utcnow())


async def _reject(hass, call, data, actor) -> None:
    data.family.reject(actor, call.data[ATTR_CHORE_ID], dt_util.utcnow())


@callback
def async_register_services(hass: HomeAssistant) -> None:
    for name, handler, schema in (
        (SERVICE_CREATE_CHORE, _create, CREATE_SCHEMA),
        (SERVICE_DELETE_CHORE, _delete, CHORE_SCHEMA),
        (SERVICE_CLAIM_CHORE, _claim, CLAIM_SCHEMA),
        (SERVICE_UNDO_CLAIM, _undo, CHORE_SCHEMA),
        (SERVICE_APPROVE_CHORE, _approve, CHORE_SCHEMA),
        (SERVICE_REJECT_CHORE, _reject, CHORE_SCHEMA),
    ):
        hass.services.async_register(DOMAIN, name, _guarded(handler), schema=schema)
