from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import (
    CONF_COUNTRY_ID,
    CONF_THRESH,
    DEFAULT_COUNTRY_ID,
    DEFAULT_THRESH,
    DOMAIN,
)
from .smard import SMARD_COUNTRIES

SCHEMA = vol.Schema(
    {
        vol.Required(
            CONF_COUNTRY_ID,
            default=DEFAULT_COUNTRY_ID,
            description={"translation_key": CONF_COUNTRY_ID},
        ): vol.In(SMARD_COUNTRIES),
        vol.Required(
            CONF_THRESH,
            default=DEFAULT_THRESH,
            description={"translation_key": CONF_THRESH},
        ): vol.Coerce(float),
    }
)


class DelayedChargingConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Delayed Charging."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial step."""

        if user_input is not None:
            return self.async_create_entry(
                title="Delayed Charging", data=user_input, options=user_input
            )

        return self.async_show_form(
            step_id="user",
            data_schema=SCHEMA,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return DelayedChargingOptionsFlow()


class DelayedChargingOptionsFlow(config_entries.OptionsFlowWithReload):
    """Handle options flow for Delayed Charging."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(
                SCHEMA, self.config_entry.options
            ),
        )
