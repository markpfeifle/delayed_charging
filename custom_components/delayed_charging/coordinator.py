from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.core import HomeAssistant

import aiohttp
import logging

_LOGGER = logging.getLogger(__name__)


class ElectricityPriceCoordinator(DataUpdateCoordinator):
    def __init__(
        self, hass: HomeAssistant, session: aiohttp.ClientSession, api_url: str
    ):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Electricity Price Coordinator",
            update_interval=timedelta(minutes=30),
        )
        self.session = session
        self.api_url = api_url

    async def _async_update_data(self):
        try:
            # Call API fetching code
            return {"status": "test"}
        except Exception as err:
            raise UpdateFailed(f"API error: {err}") from err
