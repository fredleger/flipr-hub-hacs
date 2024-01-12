import aiohttp
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from ._logger import _LOGGER
from .const import API_URI

class FliprAPIClient:
    def __init__(self, hass):
        self.session = async_get_clientsession(hass)

    async def get_token(self, username, password):
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {'grant_type': 'password', 'username': username, 'password': password}
    
        _LOGGER.info("Calling get_token")
        response_json = await self._make_request('post', f'{API_URI}/OAuth2/token', data, headers)

        return response_json['access_token']

    async def get_place_ids(self, token):
        _LOGGER.info(f"Calling get_place_ids with token={token}")
        headers = {'Authorization': f'Bearer {token}'}
        response_json = await self._make_request('get', f'{API_URI}/place', None, headers)

        return [place['PlaceId'] for place in response_json] if response_json else []

    async def get_hubs_for_all_places(self, token, place_ids):
        all_hubs = []
        for place_id in place_ids:
            hubs = await self.get_hubs(token, place_id)
            all_hubs.extend(hubs)
        return all_hubs

    async def get_hubs(self, token, place_id):
        _LOGGER.info(f"Calling get_hubs with token={token} and place_id={place_id}")
        headers = {'Authorization': f'Bearer {token}'}
        return await self._make_request('get', f'{API_URI}/hub/Place/{place_id}/AllHubs', None, headers)

    async def change_hub_state(self, serial, state, token):
        _LOGGER.info(f"Calling change_hub_state with serial={serial}, state={state}, token={token}")
        headers = {'Authorization': f'Bearer {token}'}
        return await self._make_request('post', f'{API_URI}/hub/{serial}/Manual/{str(state).lower()}', None, headers)

    async def update_hub_state(self, serial, token):
        _LOGGER.info(f"Calling update_hub_state with serial={serial}, token={token}")
        headers = {'Authorization': f'Bearer {token}'}
        return await self._make_request('get', f'{API_URI}/hub/{serial}/state', None, headers)

    async def _make_request(self, method, url, data=None, headers=None):
        async with self.session.request(method, url, data=data, headers=headers) as response:
            
            if response.status == 200:
                _LOGGER.info(f"Response from {url}: {response_json}")
                return True
            else:
                _LOGGER.error(f"Request to {url} failed with status {response.status}: {response_json}")
                return False
