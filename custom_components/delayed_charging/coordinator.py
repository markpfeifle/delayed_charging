import datetime
import logging
from datetime import timedelta
from typing import cast

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from custom_components.delayed_charging.const import CONF_COUNTRY_ID, DEFAULT_COUNTRY_ID
from custom_components.delayed_charging.smard import get_pricing_info

_LOGGER = logging.getLogger(__name__)


class ElectricityPriceCoordinator(DataUpdateCoordinator[list[tuple[datetime.datetime, float]]]):
    """Coordinator to fetch electricity prices from a REST API."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            config_entry=config_entry,
            name="Electricity Price Coordinator",
            update_interval=timedelta(minutes=2),
            always_update=True,
        )

    async def _async_update_data(self):
        """Fetch data from API."""
        try:
            # Check options first, fall back to data if not in options
            config_entry = cast(ConfigEntry, self.config_entry)
            country_id = config_entry.options.get(CONF_COUNTRY_ID, DEFAULT_COUNTRY_ID)
            return await get_pricing_info(country_id)
        except Exception as err:
            raise UpdateFailed(f"API error: {err}") from err
