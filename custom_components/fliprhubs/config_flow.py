import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN
from .flipr_api_client import FliprAPIClient

class FliprHubsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 3
    CONNECTION_CLASS = config_entries.CONN_CLASS_UNKNOWN

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            api_client = FliprAPIClient(self.hass)
            token = await api_client.get_token(user_input['username'], user_input['password'])

            if token is not None:
                place_ids = await api_client.get_place_ids(token)
                if place_ids:
                    return self.async_create_entry(
                        title="Flipr Hubs",
                        data={
                            'username': user_input['username'],
                            'password': user_input['password'],
                            'place_ids': place_ids
                        }
                    )
                else:
                    errors["base"] = "no_place_ids"
            else:
                errors["base"] = "invalid_auth"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("username"): str,
                vol.Required("password"): str,
            }),
            errors=errors
        )
