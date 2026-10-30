"""Einrichtung und Familienmitglieder über die HA-Oberfläche."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    BooleanSelector,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    EntitySelector,
    EntitySelectorConfig,
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import (
    CONF_ANNOUNCE_NOTIFY,
    CONF_ANNOUNCE_TIMES,
    CONF_SPEAKERS,
    CONF_TTS_ENGINE,
    DEFAULT_ANNOUNCE_TIMES,
    CONF_CONSEQUENCES,
    CONF_LOCK_TIME,
    CONF_PHOTO_DELETE_AFTER_REVIEW,
    CONF_PHOTO_RETENTION,
    DEFAULT_PHOTO_DELETE_AFTER_REVIEW,
    CONF_TAKEOVER_DOUBLE,
    CONF_TAKEOVER_FROM,
    CONF_TAKEOVER_MAX,
    DEFAULT_PHOTO_RETENTION,
    DEFAULT_TAKEOVER_DOUBLE,
    DEFAULT_TAKEOVER_FROM,
    DEFAULT_TAKEOVER_MAX,
    CONF_PARENT_SUMMARY_TIME,
    CONF_RELEASE_TIME,
    DEFAULT_LOCK_TIME,
    DEFAULT_RELEASE_TIME,
    CONF_REMINDER_TIMES,
    DEFAULT_PARENT_SUMMARY_TIME,
    DEFAULT_REMINDER_TIMES,
    DATA_INITIAL_FAMILY,
    DOMAIN,
)
from homeassistant.util import dt as dt_util

from .core import SYSTEM, FamilyError, Role
from .reminders import parse_times
from .setup_helpers import (
    Person,
    build_family,
    find_people,
    split_names,
)


def _age_selector() -> NumberSelector:
    return NumberSelector(
        NumberSelectorConfig(
            min=0, max=18, step=1, mode=NumberSelectorMode.BOX
        )
    )

CONF_FAMILY_NAME = "family_name"
CONF_MEMBER_NAME = "name"
CONF_ROLE = "role"
CONF_USER = "user"
CONF_MEMBER = "member"
CONF_NOTIFY = "notify_service"
CONF_DEVICES = "devices"
CONF_PEOPLE = "people"
CONF_EXTRA_CHILDREN = "extra_children"
CONF_PARENTS = "parents"
CONF_STARTERS = "starters"
CONF_REWARDS = "rewards"
CONF_PHOTO_PRIVACY = "photo_privacy"
CONF_TABLET = "tablet"
CONF_TABLET_APPROVAL = "tablet_approval"
PHOTO_DELETE = "delete"
PHOTO_KEEP = "keep"
NO_USER = "__none__"


class SternchenplanConfigFlow(ConfigFlow, domain=DOMAIN):
    """Einrichtung in wenigen kurzen Schritten.

    1. Familienname  2. Wer gehört dazu (aus den HA-Personen, plus Kinder ohne
    Konto)  3. Wer davon sind Eltern  4. Familientablet (nur wenn möglich).
    Handys für Push-Nachrichten werden automatisch zugeordnet. Den Rest
    (Alter, Aufgaben, Belohnungen, Fotos) erledigt der Willkommens-Assistent.
    """

    VERSION = 1

    def __init__(self) -> None:
        self._title = "Familie"
        self._people: list[Person] = []
        self._selected: list[str] = []
        self._extra: list[str] = []
        self._parents: list[str] = []
        self._tablet: list[str] = []
        self._tablet_approval = False

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            self._title = user_input[CONF_FAMILY_NAME].strip() or "Familie"
            self._people = find_people(self.hass)
            return await self.async_step_members()
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {vol.Required(CONF_FAMILY_NAME, default="Familie"): str}
            ),
        )

    async def async_step_members(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            self._selected = user_input.get(CONF_PEOPLE, [])
            self._extra = split_names(user_input.get(CONF_EXTRA_CHILDREN, ""))
            if not self._selected and not self._extra:
                errors["base"] = "no_members"
            elif self._selected:
                return await self.async_step_parents()
            else:
                return await self.async_step_tablet()

        schema: dict = {}
        if self._people:
            schema[vol.Optional(CONF_PEOPLE, default=[p.entity_id for p in self._people])] = (
                SelectSelector(
                    SelectSelectorConfig(
                        options=[
                            SelectOptionDict(value=p.entity_id, label=p.name) for p in self._people
                        ],
                        multiple=True,
                        mode=SelectSelectorMode.LIST,
                    )
                )
            )
        schema[vol.Optional(CONF_EXTRA_CHILDREN, default="")] = str
        return self.async_show_form(
            step_id="members", errors=errors, data_schema=vol.Schema(schema)
        )

    async def async_step_parents(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            self._parents = user_input.get(CONF_PARENTS, [])
            return await self.async_step_tablet()

        chosen = [p for p in self._people if p.entity_id in self._selected]
        # Vorschlag: wer in HA Administrator ist, ist Elternteil.
        suggested = []
        for person in chosen:
            user = await self.hass.auth.async_get_user(person.user_id) if person.user_id else None
            if user and user.is_admin:
                suggested.append(person.entity_id)
        return self.async_show_form(
            step_id="parents",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_PARENTS, default=suggested): SelectSelector(
                        SelectSelectorConfig(
                            options=[SelectOptionDict(value=p.entity_id, label=p.name) for p in chosen],
                            multiple=True,
                            mode=SelectSelectorMode.LIST,
                        )
                    )
                }
            ),
        )

    async def async_step_tablet(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Familientablet für Kinder ohne eigenes Handy. Freiwillig.

        Zur Auswahl stehen HA-Konten, die nicht Eltern sind. War ein solches
        Konto als Kind angehakt, ist es danach kein Familienmitglied mehr.
        """
        candidates = [
            p for p in self._people if p.user_id and p.entity_id not in self._parents
        ]
        if not candidates:
            return self._create()
        if user_input is not None:
            chosen = [p for p in candidates if p.entity_id in user_input.get(CONF_TABLET, [])]
            self._tablet = [p.user_id for p in chosen]
            self._tablet_approval = user_input.get(CONF_TABLET_APPROVAL, False)
            self._selected = [
                e for e in self._selected if e not in {p.entity_id for p in chosen}
            ]
            return self._create()
        return self.async_show_form(
            step_id="tablet",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_TABLET, default=[]): SelectSelector(
                        SelectSelectorConfig(
                            options=[
                                SelectOptionDict(value=p.entity_id, label=p.name)
                                for p in candidates
                            ],
                            multiple=True,
                            mode=SelectSelectorMode.LIST,
                        )
                    ),
                    vol.Optional(CONF_TABLET_APPROVAL, default=False): BooleanSelector(),
                }
            ),
        )

    def _create(self) -> ConfigFlowResult:
        """Familie anlegen. Alter, Aufgaben, Belohnungen und Fotos fragt danach
        der Willkommens-Assistent im Menüpunkt „Sternchenplan“ ab."""
        english = not (self.hass.config.language or "").startswith("de")
        people = [p for p in self._people if p.entity_id in self._selected]
        family = build_family(
            people,
            self._parents,
            self._extra,
            [],
            dt_util.utcnow(),
            english=english,
            currency=self.hass.config.currency,
            tablet_users=self._tablet,
            tablet_approval=self._tablet_approval,
        )
        return self.async_create_entry(
            title=self._title,
            data={DATA_INITIAL_FAMILY: family.to_dict()},
            options={CONF_PHOTO_DELETE_AFTER_REVIEW: DEFAULT_PHOTO_DELETE_AFTER_REVIEW},
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return MembersOptionsFlow()


class MembersOptionsFlow(OptionsFlow):
    """Mitglieder hinzufügen oder entfernen.

    Nur Admins kommen in HA überhaupt in diesen Dialog. Die Änderung läuft
    trotzdem über den Kern, damit die Regeln an einer Stelle bleiben.
    """

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        menu = ["add_member"]
        if self.config_entry.runtime_data.family.members:
            menu.append("remove_member")
        if any(
            m.role is Role.CHILD
            for m in self.config_entry.runtime_data.family.members.values()
        ):
            menu.append("ages")
        menu.append("tablet")
        menu.append("reminders")
        menu.append("announcements")
        menu.append("consequences")
        menu.append("rules")
        if any(
            m.role is Role.CHILD
            for m in self.config_entry.runtime_data.family.members.values()
        ):
            menu.append("devices")
        return self.async_show_menu(step_id="init", menu_options=menu)

    async def async_step_tablet(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Familientablet: HA-Konto, an dem Kinder ohne Handy abhaken."""
        family = self.config_entry.runtime_data.family
        if user_input is not None:
            family.set_tablet(
                SYSTEM,
                user_input.get(CONF_TABLET, []),
                approval=user_input.get(CONF_TABLET_APPROVAL, False),
            )
            return await self._async_finish()
        taken = {m.user_id for m in family.members.values() if m.user_id}
        users = [
            u
            for u in await self.hass.auth.async_get_users()
            if not u.system_generated and u.is_active and u.id not in taken
        ]
        return self.async_show_form(
            step_id="tablet",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_TABLET,
                        default=[u for u in family.tablet_users if u in {x.id for x in users}],
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=[
                                SelectOptionDict(value=u.id, label=u.name or u.id)
                                for u in sorted(users, key=lambda u: (u.name or "").casefold())
                            ],
                            multiple=True,
                            mode=SelectSelectorMode.LIST,
                        )
                    ),
                    vol.Optional(
                        CONF_TABLET_APPROVAL, default=family.tablet_approval
                    ): BooleanSelector(),
                }
            ),
        )

    async def async_step_add_member(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        data = self.config_entry.runtime_data
        errors: dict[str, str] = {}
        if user_input is not None:
            user_id = user_input.get(CONF_USER)
            notify = user_input.get(CONF_NOTIFY)
            try:
                data.family.add_member(
                    SYSTEM,
                    user_input[CONF_MEMBER_NAME],
                    Role(user_input[CONF_ROLE]),
                    user_id=None if user_id in (None, NO_USER) else user_id,
                    notify_service=None if notify in (None, NO_USER) else notify,
                )
            except FamilyError:
                errors["base"] = "invalid_member"
            else:
                return await self._async_finish()

        taken = {m.user_id for m in data.family.members.values() if m.user_id}
        users = [
            SelectOptionDict(value=u.id, label=u.name or u.id)
            for u in await self.hass.auth.async_get_users()
            if not u.system_generated and u.is_active and u.id not in taken
        ]
        notify_services = [
            SelectOptionDict(value=name, label=f"notify.{name}")
            for name in sorted(self.hass.services.async_services_for_domain("notify"))
            if name not in ("send_message", "persistent_notification")
        ]
        return self.async_show_form(
            step_id="add_member",
            errors=errors,
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_MEMBER_NAME): str,
                    vol.Required(CONF_ROLE, default=Role.CHILD.value): SelectSelector(
                        SelectSelectorConfig(
                            options=[r.value for r in Role],
                            translation_key="role",
                            mode=SelectSelectorMode.LIST,
                        )
                    ),
                    vol.Optional(CONF_USER, default=NO_USER): SelectSelector(
                        SelectSelectorConfig(
                            options=[SelectOptionDict(value=NO_USER, label="—"), *users],
                            mode=SelectSelectorMode.DROPDOWN,
                        )
                    ),
                    vol.Optional(CONF_NOTIFY, default=NO_USER): SelectSelector(
                        SelectSelectorConfig(
                            options=[
                                SelectOptionDict(value=NO_USER, label="—"),
                                *notify_services,
                            ],
                            mode=SelectSelectorMode.DROPDOWN,
                        )
                    ),
                }
            ),
        )

    async def async_step_remove_member(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        data = self.config_entry.runtime_data
        if user_input is not None:
            from .photos import async_discard  # noqa: PLC0415

            for photo in data.family.remove_member(SYSTEM, user_input[CONF_MEMBER]):
                await async_discard(self.hass, photo)
            return await self._async_finish()
        return self.async_show_form(
            step_id="remove_member",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_MEMBER): SelectSelector(
                        SelectSelectorConfig(
                            options=[
                                SelectOptionDict(value=m.id, label=m.name)
                                for m in data.family.members.values()
                            ]
                        )
                    )
                }
            ),
        )

    async def async_step_ages(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Alter der Kinder ändern. Leer lassen heißt: unbekannt."""
        family = self.config_entry.runtime_data.family
        now = dt_util.utcnow()
        children = [m for m in family.members.values() if m.role is Role.CHILD]
        if user_input is not None:
            for child in children:
                value = user_input.get(child.name)
                family.set_age(SYSTEM, child.id, None if value in (None, "") else int(value), now)
            return await self._async_finish()
        schema = {}
        for child in children:
            age = child.age(now)
            key = (
                vol.Optional(child.name, description={"suggested_value": age})
                if age is not None
                else vol.Optional(child.name)
            )
            schema[key] = _age_selector()
        return self.async_show_form(step_id="ages", data_schema=vol.Schema(schema))

    async def async_step_reminders(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        options = self.config_entry.options
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                parse_times(user_input[CONF_REMINDER_TIMES])
                parse_times(user_input.get(CONF_PARENT_SUMMARY_TIME, ""))
            except ValueError:
                errors["base"] = "invalid_time"
            else:
                return await self._async_finish(
                    {**options, **user_input, CONF_PARENT_SUMMARY_TIME: user_input.get(CONF_PARENT_SUMMARY_TIME, "")}
                )
        return self.async_show_form(
            step_id="reminders",
            errors=errors,
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_REMINDER_TIMES,
                        default=options.get(CONF_REMINDER_TIMES, DEFAULT_REMINDER_TIMES),
                    ): str,
                    vol.Optional(
                        CONF_PARENT_SUMMARY_TIME,
                        default=options.get(
                            CONF_PARENT_SUMMARY_TIME, DEFAULT_PARENT_SUMMARY_TIME
                        ),
                    ): str,
                }
            ),
        )

    async def async_step_announcements(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Ansagen über Lautsprecher."""
        options = self.config_entry.options
        errors: dict[str, str] = {}
        if user_input is not None:
            # Geleerte Felder schickt HA nicht mit, darum hier zurücksetzen.
            user_input = {
                CONF_SPEAKERS: [],
                CONF_TTS_ENGINE: "",
                CONF_ANNOUNCE_NOTIFY: [],
                CONF_ANNOUNCE_TIMES: "",
                **user_input,
            }
            try:
                parse_times(user_input[CONF_ANNOUNCE_TIMES])
            except ValueError:
                errors["base"] = "invalid_time"
            else:
                if user_input[CONF_SPEAKERS] and not user_input[CONF_TTS_ENGINE]:
                    errors["base"] = "tts_missing"
                else:
                    return await self._async_finish({**options, **user_input})

        notify_services = [
            SelectOptionDict(value=name, label=f"notify.{name}")
            for name in sorted(self.hass.services.async_services_for_domain("notify"))
            if name not in ("send_message", "persistent_notification")
        ]
        engine = options.get(CONF_TTS_ENGINE)
        return self.async_show_form(
            step_id="announcements",
            errors=errors,
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_ANNOUNCE_TIMES,
                        default=options.get(CONF_ANNOUNCE_TIMES, DEFAULT_ANNOUNCE_TIMES),
                    ): str,
                    vol.Optional(
                        CONF_SPEAKERS, default=options.get(CONF_SPEAKERS, [])
                    ): EntitySelector(EntitySelectorConfig(domain="media_player", multiple=True)),
                    vol.Optional(
                        CONF_TTS_ENGINE,
                        **({"description": {"suggested_value": engine}} if engine else {}),
                    ): EntitySelector(EntitySelectorConfig(domain="tts")),
                    vol.Optional(
                        CONF_ANNOUNCE_NOTIFY, default=options.get(CONF_ANNOUNCE_NOTIFY, [])
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=notify_services,
                            multiple=True,
                            mode=SelectSelectorMode.DROPDOWN,
                        )
                    ),
                }
            ),
        )

    async def async_step_consequences(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        options = self.config_entry.options
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                parse_times(user_input[CONF_LOCK_TIME])
                parse_times(user_input[CONF_RELEASE_TIME])
            except ValueError:
                errors["base"] = "invalid_time"
            else:
                return await self._async_finish({**options, **user_input})
        return self.async_show_form(
            step_id="consequences",
            errors=errors,
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_CONSEQUENCES, default=options.get(CONF_CONSEQUENCES, False)
                    ): BooleanSelector(),
                    vol.Required(
                        CONF_LOCK_TIME, default=options.get(CONF_LOCK_TIME, DEFAULT_LOCK_TIME)
                    ): str,
                    vol.Required(
                        CONF_RELEASE_TIME,
                        default=options.get(CONF_RELEASE_TIME, DEFAULT_RELEASE_TIME),
                    ): str,
                }
            ),
        )

    async def async_step_rules(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Wegmopsen und Fotos."""
        options = self.config_entry.options
        errors: dict[str, str] = {}
        if user_input is not None:
            user_input = {
                CONF_TAKEOVER_FROM: "",
                CONF_TAKEOVER_DOUBLE: "",
                **user_input,
            }
            try:
                parse_times(user_input[CONF_TAKEOVER_FROM])
                parse_times(user_input[CONF_TAKEOVER_DOUBLE])
            except ValueError:
                errors["base"] = "invalid_time"
            else:
                user_input[CONF_TAKEOVER_MAX] = int(user_input[CONF_TAKEOVER_MAX])
                user_input[CONF_PHOTO_RETENTION] = int(user_input[CONF_PHOTO_RETENTION])
                return await self._async_finish({**options, **user_input})

        def number(maximum: int) -> NumberSelector:
            return NumberSelector(
                NumberSelectorConfig(min=1, max=maximum, step=1, mode=NumberSelectorMode.BOX)
            )

        return self.async_show_form(
            step_id="rules",
            errors=errors,
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_TAKEOVER_FROM,
                        default=options.get(CONF_TAKEOVER_FROM, DEFAULT_TAKEOVER_FROM),
                    ): str,
                    vol.Optional(
                        CONF_TAKEOVER_DOUBLE,
                        default=options.get(CONF_TAKEOVER_DOUBLE, DEFAULT_TAKEOVER_DOUBLE),
                    ): str,
                    vol.Required(
                        CONF_TAKEOVER_MAX,
                        default=options.get(CONF_TAKEOVER_MAX, DEFAULT_TAKEOVER_MAX),
                    ): number(10),
                    vol.Required(
                        CONF_PHOTO_DELETE_AFTER_REVIEW,
                        default=options.get(
                            CONF_PHOTO_DELETE_AFTER_REVIEW, DEFAULT_PHOTO_DELETE_AFTER_REVIEW
                        ),
                    ): BooleanSelector(),
                    vol.Required(
                        CONF_PHOTO_RETENTION,
                        default=options.get(CONF_PHOTO_RETENTION, DEFAULT_PHOTO_RETENTION),
                    ): number(90),
                }
            ),
        )

    async def async_step_devices(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        family = self.config_entry.runtime_data.family
        if user_input is not None:
            self._member_id = user_input[CONF_MEMBER]
            return await self.async_step_devices_select()
        children = [m for m in family.members.values() if m.role is Role.CHILD]
        return self.async_show_form(
            step_id="devices",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_MEMBER): SelectSelector(
                        SelectSelectorConfig(
                            options=[SelectOptionDict(value=m.id, label=m.name) for m in children]
                        )
                    )
                }
            ),
        )

    async def async_step_devices_select(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        family = self.config_entry.runtime_data.family
        member = family.members[self._member_id]
        if user_input is not None:
            family.set_devices(SYSTEM, member.id, user_input.get(CONF_DEVICES, []))
            return await self._async_finish()
        return self.async_show_form(
            step_id="devices_select",
            description_placeholders={"member": member.name},
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_DEVICES, default=member.devices): EntitySelector(
                        EntitySelectorConfig(domain="switch", multiple=True)
                    )
                }
            ),
        )

    async def _async_finish(
        self, options: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        await self.config_entry.runtime_data.async_save()
        # Neu laden, damit Sensoren und Zeitpläne zum neuen Stand passen.
        self.hass.config_entries.async_schedule_reload(self.config_entry.entry_id)
        return self.async_create_entry(
            data=options if options is not None else dict(self.config_entry.options)
        )
