from functools import cached_property

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


class DelayedChargingStart(  # type: ignore[override]
    CoordinatorEntity[ElectricityPriceCoordinator],
    SensorEntity,
):

    def __init__(
        self,
        coordinator: ElectricityPriceCoordinator,
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
    def native_value(self):  # type: ignore[override]
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


class DelayedChargingActive(  # type: ignore[override]
    CoordinatorEntity[ElectricityPriceCoordinator],
    BinarySensorEntity,
):
    def __init__(
        self,
        coordinator: ElectricityPriceCoordinator,
        name: str = "Delayed Charging Active",
    ):
        super().__init__(coordinator)
        self._name = name
        self._attr_is_on = None

    @cached_property
    def name(self):
        return self._name

    @property
    def is_on(self):  # type: ignore[override]
        return self._attr_is_on

    @cached_property
    def device_class(self):
        return BinarySensorDeviceClass.POWER

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_is_on = delayed_charging_is_active_today(self.coordinator.data)
        self.async_write_ha_state()


class CurrentPriceSensor(  # type: ignore[override]
    CoordinatorEntity[ElectricityPriceCoordinator],
    SensorEntity,
):
    def __init__(
        self,
        coordinator: ElectricityPriceCoordinator,
        name: str = "Current Price",
    ):
        super().__init__(coordinator)
        self._name = name
        self._attr_native_value = None
        self._attr_extra_state_attributes = {}

    @cached_property
    def name(self):
        return self._name

    @cached_property
    def device_class(self):
        return SensorDeviceClass.MONETARY

    @property
    def native_value(self):  # type: ignore[override]
        return self._attr_native_value

    @property
    def extra_state_attributes(self):  # type: ignore[override]
        """Expose the daily price series for ApexCharts Card."""
        return self._attr_extra_state_attributes or {"apexchart_series": []}

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = get_current_price(self.coordinator.data)
        self._attr_extra_state_attributes = {
            "apexchart_series": [
                {
                    "x": dt.isoformat(),
                    "y": price,
                }
                for dt, price in (self.coordinator.data or [])
            ]
        }
        self.async_write_ha_state()
