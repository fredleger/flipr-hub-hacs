from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN
from .flipr_api_client import FliprAPIClient

async def async_setup(hass: HomeAssistant, config: dict):
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    api_client = FliprAPIClient(hass)
    token = await api_client.get_token(entry.data['username'], entry.data['password'])
    
    if token is None:
        _LOGGER.error("Failed to setup FliprHubs integration due to token error")
        return False

    place_ids = await api_client.get_place_ids(token)
    
    if not place_ids:
        _LOGGER.error("Failed to find any places for FliprHubs integration")
        return False

    hass.data[DOMAIN] = {
        'api_client': api_client,
        'token': token,
        'place_ids': place_ids
    }

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "switch")
    )
    return True