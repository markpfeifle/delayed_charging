from datetime import timedelta
import datetime
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.core import HomeAssistant

import logging

from custom_components.delayed_charging.service import get_pricing_info

_LOGGER = logging.getLogger(__name__)


class ElectricityPriceCoordinator(
    DataUpdateCoordinator[list[tuple[datetime.datetime, float]]]
):
    def __init__(self, hass: HomeAssistant):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Electricity Price Coordinator",
            update_interval=timedelta(minutes=5),
            always_update=False,
        )

    async def _async_update_data(self):
        try:
            return await get_pricing_info()
        except Exception as err:
            raise UpdateFailed(f"API error: {err}") from err
