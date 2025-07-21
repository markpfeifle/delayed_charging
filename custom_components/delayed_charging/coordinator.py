import datetime
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from custom_components.delayed_charging.service import get_pricing_info

_LOGGER = logging.getLogger(__name__)


class ElectricityPriceCoordinator(
    DataUpdateCoordinator[list[tuple[datetime.datetime, float]]]
):
    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry):
        """Initialize the coordinator."""
        self.config_entry = config_entry
        super().__init__(
            hass,
            _LOGGER,
            name="Electricity Price Coordinator",
            update_interval=timedelta(minutes=2),
            always_update=True,
        )

    async def _async_update_data(self):
        try:
            return await get_pricing_info()
        except Exception as err:
            raise UpdateFailed(f"API error: {err}") from err
