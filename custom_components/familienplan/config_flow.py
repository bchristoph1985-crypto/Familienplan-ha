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
    CONF_CONSEQUENCES,
    CONF_LOCK_TIME,
    CONF_PHOTO_RETENTION,
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
    DOMAIN,
)
from .core import SYSTEM, FamilyError, Role
from .reminders import parse_times

CONF_FAMILY_NAME = "family_name"
CONF_MEMBER_NAME = "name"
CONF_ROLE = "role"
CONF_USER = "user"
CONF_MEMBER = "member"
CONF_NOTIFY = "notify_service"
CONF_DEVICES = "devices"
NO_USER = "__none__"


class FamilienplanConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(
                title=user_input[CONF_FAMILY_NAME].strip() or "Familie", data={}
            )
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {vol.Required(CONF_FAMILY_NAME, default="Familie"): str}
            ),
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
        menu.append("reminders")
        menu.append("consequences")
        menu.append("rules")
        if any(
            m.role is Role.CHILD
            for m in self.config_entry.runtime_data.family.members.values()
        ):
            menu.append("devices")
        return self.async_show_menu(step_id="init", menu_options=menu)

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
            data.family.remove_member(SYSTEM, user_input[CONF_MEMBER])
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
