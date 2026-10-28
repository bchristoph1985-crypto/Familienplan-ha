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
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import DOMAIN
from .core import SYSTEM, FamilyError, Role

CONF_FAMILY_NAME = "family_name"
CONF_MEMBER_NAME = "name"
CONF_ROLE = "role"
CONF_USER = "user"
CONF_MEMBER = "member"
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
        return self.async_show_menu(step_id="init", menu_options=menu)

    async def async_step_add_member(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        data = self.config_entry.runtime_data
        errors: dict[str, str] = {}
        if user_input is not None:
            user_id = user_input.get(CONF_USER)
            try:
                data.family.add_member(
                    SYSTEM,
                    user_input[CONF_MEMBER_NAME],
                    Role(user_input[CONF_ROLE]),
                    user_id=None if user_id in (None, NO_USER) else user_id,
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

    async def _async_finish(self) -> ConfigFlowResult:
        await self.config_entry.runtime_data.async_save()
        # Neu laden, damit Sensoren für neue Mitglieder entstehen.
        self.hass.config_entries.async_schedule_reload(self.config_entry.entry_id)
        return self.async_create_entry(data={})
