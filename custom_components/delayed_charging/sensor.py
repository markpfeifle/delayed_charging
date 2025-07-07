import logging
from datetime import timedelta

from coordinator import ElectricityPriceCoordinator
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
)

from custom_components.delayed_charging_start.service import get_delayed_charging_start

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "Delayed Charging Start"

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    coordinator = ElectricityPriceCoordinator(hass)
    await coordinator.async_config_entry_first_refresh()
    """Set up the sensor platform asynchronously."""
    async_add_entities([DelayedChargingStart()])


class DelayedChargingStart(SensorEntity):

    def __init__(self):
        """Initialize the sensor."""
        self._state = None
        self._name = DEFAULT_NAME

    @property
    def name(self):
        return self._name

    @property
    def native_value(self):
        return self._state

    @property
    def device_class(self):
        return SensorDeviceClass.TIMESTAMP

    @property
    def state_class(self):
        return None

    async def async_update(self):
        try:
            self._state = await get_delayed_charging_start()
        except Exception as e:
            _LOGGER.error("Error fetching delayed charging start: %s", e)
            self._state = None
