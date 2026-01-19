"""Config flow for DigitalSTROM VDC."""
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries

from .const import DOMAIN


class DigitalstromConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            data = {"host": "127.0.0.1", "port": user_input["port"]}
            return self.async_create_entry(title="DigitalSTROM VDC", data=data)

        data_schema = vol.Schema(
            {
                vol.Required("port", default=4000): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=65535)
                ),
            }
        )
        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)
