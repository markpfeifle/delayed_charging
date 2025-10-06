"""Test the Delayed Charging binary sensor setup."""

import datetime
from unittest.mock import MagicMock, patch
from zoneinfo import ZoneInfo

import pytest
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.delayed_charging.const import DOMAIN

# We pretend the system tz to be Central European (Summer) Time
CONSTANT_SYSTEM_TZ = ZoneInfo("Europe/Berlin")

TEST_TIME = datetime.datetime(2025, 7, 28, 10, 0, 0, tzinfo=CONSTANT_SYSTEM_TZ)


@pytest.fixture
def mock_config_entry():
    """Create a mock config entry for the integration."""
    return MockConfigEntry(
        domain=DOMAIN,
        data={"country_id": "DE", "threshold": 0.15},
        options={"country_id": "DE", "threshold": 0.15},
    )


@pytest.fixture
def mock_datetime_now():
    fake_now = datetime.datetime(2025, 7, 28, 10, 15, 0, tzinfo=CONSTANT_SYSTEM_TZ)

    def fake_now_staticmethod(*args, **kwargs) -> datetime.datetime:  # type: ignore[no-untyped-def]
        return fake_now

    real_datetime_class = datetime.datetime
    with patch("custom_components.delayed_charging.service.datetime.datetime") as mock_datetime:
        mock_datetime.now = staticmethod(fake_now_staticmethod)  # type: ignore[assignment]
        # Ensure other datetime methods work normally
        mock_datetime.side_effect = real_datetime_class
        yield fake_now


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


async def test_sensor_states_with_empty_data(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry, mock_datetime_now: MagicMock
):
    """Test sensor states when coordinator returns empty data."""
    empty_data: list[tuple[datetime.datetime, float]] = []

    async def mock_update():
        return empty_data

    with patch(
        "custom_components.delayed_charging.coordinator.ElectricityPriceCoordinator._async_update_data",
        side_effect=mock_update,
    ):
        mock_config_entry.add_to_hass(hass)
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

        current_price = hass.states.get("sensor.current_price")
        charging_start = hass.states.get("sensor.delayed_charging_start")
        charging_active = hass.states.get("binary_sensor.delayed_charging_active")

        assert current_price is not None
        assert charging_start is not None
        assert charging_active is not None

        assert current_price.state == "unknown"
        assert charging_start.state == "unknown"
        assert charging_active.state == "off"


async def test_sensor_states_with_single_datapoint(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry, mock_datetime_now: MagicMock
):
    """Test sensor states when coordinator returns a single datapoint."""
    test_time = TEST_TIME
    single_data = [(test_time, 0.10)]

    async def mock_update():
        return single_data

    with patch(
        "custom_components.delayed_charging.coordinator.ElectricityPriceCoordinator._async_update_data",
        side_effect=mock_update,
    ):

        mock_config_entry.add_to_hass(hass)
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

        current_price = hass.states.get("sensor.current_price")
        charging_start = hass.states.get("sensor.delayed_charging_start")
        charging_active = hass.states.get("binary_sensor.delayed_charging_active")

        assert current_price is not None
        assert charging_start is not None
        assert charging_active is not None

        assert current_price.state == "0.1"
        assert charging_start.state != "unknown"
        assert charging_active.state == "on"


async def test_sensor_states_with_gaps(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry, mock_datetime_now: MagicMock
):
    """Test sensor states when coordinator returns data with gaps."""
    test_time = TEST_TIME
    gap_data = sorted(
        [
            (test_time, 0.20),
            (datetime.datetime(2025, 7, 28, 14, 0, 0, tzinfo=CONSTANT_SYSTEM_TZ), 0.10),
        ]
    )

    async def mock_update():
        return gap_data

    with patch(
        "custom_components.delayed_charging.coordinator.ElectricityPriceCoordinator._async_update_data",
        side_effect=mock_update,
    ):

        mock_config_entry.add_to_hass(hass)
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

        current_price = hass.states.get("sensor.current_price")
        charging_start = hass.states.get("sensor.delayed_charging_start")
        charging_active = hass.states.get("binary_sensor.delayed_charging_active")

        assert current_price is not None
        assert charging_start is not None
        assert charging_active is not None

        # At test_time, we should see the first price
        assert current_price.state == "0.2"
        # With data having gaps, we can still calculate charging start time if price is below threshold
        assert charging_start.state != "unknown"
        assert charging_active.state == "on"


# async def test_sensor_state_updates(hass: HomeAssistant, mock_config_entry: MockConfigEntry, mock_datetime_now: MagicMock):
#     """Test that sensor states update when coordinator data changes."""
#     test_time = TEST_TIME
#     initial_data = sorted(
#         [
#             (test_time, 0.10),
#             (datetime.datetime(2025, 7, 28, 11, 0, 0, tzinfo=CONSTANT_SYSTEM_TZ), 0.15),
#             (datetime.datetime(2025, 7, 28, 12, 0, 0, tzinfo=CONSTANT_SYSTEM_TZ), 0.20),
#         ]
#     )

#     update_counter = 0

#     async def mock_update():
#         nonlocal update_counter
#         if update_counter == 0:
#             update_counter += 1
#             return initial_data
#         return sorted(
#             [
#                 (test_time, 0.25),
#                 (datetime.datetime(2025, 8, 21, 13, 0, tzinfo=CONSTANT_SYSTEM_TZ), 0.30),
#                 (datetime.datetime(2025, 8, 21, 14, 0, tzinfo=CONSTANT_SYSTEM_TZ), 0.35),
#             ]
#         )

#     with patch(
#         "custom_components.delayed_charging.coordinator.ElectricityPriceCoordinator._async_update_data",
#         side_effect=mock_update,
#     ):

#         mock_config_entry.add_to_hass(hass)
#         assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
#         await hass.async_block_till_done()

#         # Check initial states
#         current_price = hass.states.get("sensor.current_price")
#         assert current_price is not None
#         assert current_price.state == "0.1"

#         # Trigger an update
#         coordinator = hass.data[DOMAIN][mock_config_entry.entry_id].runtime_data.coordinator
#         await coordinator.async_refresh()
#         await hass.async_block_till_done()

#         # Verify states have updated
#         current_price = hass.states.get("sensor.current_price")
#         assert current_price is not None
#         assert current_price.state == "0.25"

#         # Also verify the other sensors
#         charging_start = hass.states.get("sensor.delayed_charging_start")
#         charging_active = hass.states.get("binary_sensor.delayed_charging_active")

#         assert charging_start is not None
#         assert charging_active is not None
#         assert charging_start.state != "unknown"
#         assert charging_active.state == "off"
