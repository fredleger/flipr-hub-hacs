from homeassistant.components.switch import SwitchEntity
from .const import DOMAIN
from .flipr_api_client import FliprAPIClient

async def async_setup_entry(hass, config_entry, async_add_entities):
    api_client = hass.data[DOMAIN]['api_client']
    token = hass.data[DOMAIN]['token']
    place_ids = hass.data[DOMAIN]['place_ids']
    hubs = await api_client.get_hubs_for_all_places(token, place_ids)

    async_add_entities(FliprHubSwitch(hub, api_client, token) for hub in hubs)

class FliprHubSwitch(SwitchEntity):
    def __init__(self, hub, api_client, token):
        self.api_client = api_client
        self._serial = hub['Serial']
        self._name = hub['NameEquipment']
        self._state = hub['StateEquipment']
        self._token = token

    @property
    def name(self):
        return self._name

    @property
    def is_on(self):
        return self._state

    async def async_turn_on(self, **kwargs):
        success = await self.api_client.change_hub_state(self._serial, True, self._token)
        if success:
            self._state = True
            self.async_schedule_update_ha_state()

    async def async_turn_off(self, **kwargs):
        success = await self.api_client.change_hub_state(self._serial, False, self._token)
        if success:
            self._state = False
            self.async_schedule_update_ha_state()

    async def async_update(self):
        state_info = await self.api_client.update_hub_state(self._serial, self._token)
        if state_info is not None:
            self._state = state_info['stateEquipment']
