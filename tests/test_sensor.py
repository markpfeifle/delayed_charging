"""Test the Delayed Charging binary sensor setup."""

import pytest
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.delayed_charging.const import DOMAIN


@pytest.fixture
def mock_config_entry():
    """Create a mock config entry for the integration."""
    return MockConfigEntry(
        domain=DOMAIN,
        data={"country_id": "DE", "threshold": 0.15},
    )


async def test_binary_sensor_setup(hass: HomeAssistant, coordinator_update_patch: None, mock_config_entry: MockConfigEntry):
    """Test binary sensor platform setup."""

    mock_config_entry.add_to_hass(hass)

    # Set up the binary sensor platform
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    # Verify the integration was loaded
    assert DOMAIN in hass.config.components

    # Verify the binary sensor entity was created
    active_state = hass.states.get("binary_sensor.delayed_charging_active")
    assert active_state is not None
    assert active_state.name == "Delayed Charging Active"

    # Verify the DelayedChargingStart sensor entity was created
    start_state = hass.states.get("sensor.delayed_charging_start")
    assert start_state is not None
    assert start_state.name == "Delayed Charging Start"

    # Verify the CurrentPriceSensor entity was created
    price_state = hass.states.get("sensor.current_price")
    assert price_state is not None
    assert price_state.name == "Current Price"


async def test_binary_sensor_unload(hass: HomeAssistant, coordinator_update_patch: None, mock_config_entry: MockConfigEntry):
    """Test binary sensor platform unload."""

    mock_config_entry.add_to_hass(hass)

    # Set up the platform
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    # Verify the entities exists
    assert hass.states.get("binary_sensor.delayed_charging_active") is not None
    assert hass.states.get("sensor.delayed_charging_start") is not None
    assert hass.states.get("sensor.current_price") is not None

    # Unload the entry
    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    # Verify the entities no longer exists
    assert hass.states.get("binary_sensor.delayed_charging_active") is None
    assert hass.states.get("sensor.delayed_charging_start") is None
    assert hass.states.get("sensor.current_price") is None
