from functools import cached_property
import datetime

from coordinator import ElectricityPriceCoordinator
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
)
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from custom_components.delayed_charging.service import (
    delayed_charging_is_active_today,
    get_charging_start,
    get_current_price,
)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
):
    coordinator = ElectricityPriceCoordinator(hass)
    await coordinator.async_config_entry_first_refresh()
    """Set up the sensor platform asynchronously."""
    async_add_entities(
        [
            DelayedChargingStart(coordinator),
            DelayedChargingActive(coordinator),
            CurrentPriceSensor(coordinator),
        ]
    )


class DelayedChargingStart(
    CoordinatorEntity[DataUpdateCoordinator[list[tuple[datetime.datetime, float]]]],
    SensorEntity,
):

    def __init__(
        self,
        coordinator: DataUpdateCoordinator[list[tuple[datetime.datetime, float]]],
        name: str = "Delayed Charging Start",
    ):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator)
        self._name = name
        self._attr_native_value = None

    @cached_property
    def name(self):
        return self._name

    @property
    def native_value(self):
        return self._attr_native_value

    @cached_property
    def device_class(self):
        return SensorDeviceClass.TIMESTAMP

    @cached_property
    def state_class(self):
        return None

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = get_charging_start(self.coordinator.data)
        self.async_write_ha_state()


class DelayedChargingActive(
    CoordinatorEntity[DataUpdateCoordinator[list[tuple[datetime.datetime, float]]]],
    BinarySensorEntity,
):
    def __init__(
        self,
        coordinator: DataUpdateCoordinator[list[tuple[datetime.datetime, float]]],
        name: str = "Delayed Charging Active",
    ):
        super().__init__(coordinator)
        self._name = name
        self._attr_is_on = None

    @cached_property
    def name(self):
        return self._name

    @property
    def is_on(self):
        return self._attr_is_on

    @cached_property
    def device_class(self):
        return BinarySensorDeviceClass.POWER

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_is_on = delayed_charging_is_active_today(self.coordinator.data)
        self.async_write_ha_state()


class CurrentPriceSensor(
    CoordinatorEntity[DataUpdateCoordinator[list[tuple[datetime.datetime, float]]]],
    SensorEntity,
):
    def __init__(
        self,
        coordinator: DataUpdateCoordinator[list[tuple[datetime.datetime, float]]],
        name: str = "Current Price",
    ):
        super().__init__(coordinator)
        self._name = name
        self._attr_native_value = None

    @cached_property
    def name(self):
        return self._name

    @property
    def native_value(self):
        return self._attr_native_value

    @cached_property
    def device_class(self):
        return SensorDeviceClass.MONETARY

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = get_current_price(self.coordinator.data)
        self.async_write_ha_state()
