"""Test the update coordinator."""

from typing import Any, cast

from homeassistant.core import HomeAssistant, State
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.delayed_charging.const import DOMAIN

MOCKED_ENTRY_ID = "1234567890abcdef"


def get_test_config_entry() -> MockConfigEntry:
    """Create a test config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        data={"country_id": "DE", "threshold": 0.15},
        entry_id=MOCKED_ENTRY_ID,
    )


async def test_coordinator_update(
    hass: HomeAssistant,
    mock_chart_data: list[dict[str, float | str]],
    coordinator_update_patch: Any,
):
    """Test coordinator updates successfully."""
    config_entry = get_test_config_entry()
    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done(wait_background_tasks=True)

    chart_data = cast(State, hass.states.get("sensor.current_price")).attributes.get("apexchart_series")

    assert mock_chart_data == chart_data


# async def test_coordinator_update_failure(hass: HomeAssistant):
#     """Test coordinator handles update failure."""
#     config_entry = get_test_config_entry()
#     config_entry.add_to_hass(hass)

#     with (
#         patch(
#             "custom_components.delayed_charging.coordinator.get_pricing_info",
#             side_effect=Exception("API Error"),
#         ),
#         pytest.raises(ConfigEntryNotReady),
#     ):
#         await hass.config_entries.async_setup(config_entry.entry_id)
#         await hass.async_block_till_done(wait_background_tasks=True)
