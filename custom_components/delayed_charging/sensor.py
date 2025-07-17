from functools import cached_property

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from custom_components.delayed_charging.const import DEFAULT_THRESH
from custom_components.delayed_charging.coordinator import ElectricityPriceCoordinator
from custom_components.delayed_charging.service import (
    get_charging_start,
    get_current_price,
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    coordinator = ElectricityPriceCoordinator(hass, config_entry)
    async_add_entities(
        [
            DelayedChargingStart(coordinator),
            CurrentPriceSensor(coordinator),
        ]
    )
    await coordinator.async_config_entry_first_refresh()


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
        self._config_entry = coordinator.config_entry

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
        threshold = self._config_entry.data.get("threshold", DEFAULT_THRESH)
        self._attr_native_value = get_charging_start(self.coordinator.data, threshold)
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
        self._config_entry = coordinator.config_entry

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
