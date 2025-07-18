from typing import Any

import voluptuous as vol
from homeassistant import config_entries

from .const import CONF_THRESH, DEFAULT_THRESH, DOMAIN


class DelayedChargingConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Delayed Charging."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            return self.async_create_entry(
                title="Delayed Charging",
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_THRESH, default=DEFAULT_THRESH): vol.Coerce(
                        float
                    ),
                }
            ),
            errors=errors,
        )
