"""Config flow to configure the EcoNet component."""

from typing import Any
import logging

# kludge to allow load of module from current directory when run as a script.
import sys
import os 
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path)

""" _LOGGER = logging.getLogger(__name__)
_LOGGER.error("my name is " + __name__)
_LOGGER.error("My dir_path path is " + dir_path)
_LOGGER.error("Current sys.path after adding dir_path is " + " ".join(sys.path)) """

import voluptuous as vol

from pyeconetmodified import EcoNetApiInterface
from pyeconetmodified.errors import InvalidCredentialsError, PyeconetError

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD

from .const import DOMAIN

class EcoNetFlowHandler(ConfigFlow, domain=DOMAIN):
    """Handle an EcoNet config flow."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self.data_schema = vol.Schema(
            {
                vol.Required(CONF_EMAIL): str,
                vol.Required(CONF_PASSWORD): str,
            }
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the start of the config flow."""

        if not user_input:
            return self.async_show_form(
                step_id="user",
                data_schema=self.data_schema,
            )

        await self.async_set_unique_id(user_input[CONF_EMAIL])
        self._abort_if_unique_id_configured()
        errors = {}

        try:
            await EcoNetApiInterface.login(
                user_input[CONF_EMAIL], user_input[CONF_PASSWORD]
            )
        except InvalidCredentialsError:
            errors["base"] = "invalid_auth"
        except PyeconetError:
            errors["base"] = "cannot_connect"

        if errors:
            return self.async_show_form(
                step_id="user",
                data_schema=self.data_schema,
                errors=errors,
            )

        return self.async_create_entry(
            title=user_input[CONF_EMAIL],
            data={
                CONF_EMAIL: user_input[CONF_EMAIL],
                CONF_PASSWORD: user_input[CONF_PASSWORD],
            },
        )

