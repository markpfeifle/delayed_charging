from functools import cached_property
from typing import cast

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from custom_components.delayed_charging.const import DEFAULT_THRESH
from custom_components.delayed_charging.coordinator import ElectricityPriceCoordinator
from custom_components.delayed_charging.service import delayed_charging_is_active_today


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    coordinator = ElectricityPriceCoordinator(hass, config_entry)
    async_add_entities(
        [
            DelayedChargingActive(coordinator),
        ]
    )
    await coordinator.async_config_entry_first_refresh()


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
        self._config_entry = cast(ConfigEntry, coordinator.config_entry)

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
        threshold = self._config_entry.options.get("threshold", DEFAULT_THRESH)
        self._attr_is_on = delayed_charging_is_active_today(self.coordinator.data, threshold)
        self.async_write_ha_state()
