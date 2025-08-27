from datetime import datetime
from unittest.mock import patch
from zoneinfo import ZoneInfo

import pytest

pytest_plugins = ["pytest_homeassistant_custom_component"]


# We pretend the system tz to be Central European (Summer) Time
@pytest.fixture(autouse=True, scope="session")
def patch_system_tz_service():
    """Patch the system timezone to a constant value for tests."""
    with patch("custom_components.delayed_charging.service.SYSTEM_TZ", ZoneInfo("Europe/Berlin")):
        yield


@pytest.fixture(autouse=True, scope="session")
def patch_system_tz_smard():
    """Patch the system timezone to a constant value for SMARD tests."""
    with patch("custom_components.delayed_charging.smard.SYSTEM_TZ", ZoneInfo("Europe/Berlin")):
        yield


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: None):
    yield


@pytest.fixture
def mock_coordinator_data() -> list[tuple[datetime, float]]:
    """Mock data that the coordinator should return."""
    return [
        (datetime(2025, 8, 21, 12, 0, tzinfo=ZoneInfo("Europe/Berlin")), 0.10),
        (datetime(2025, 8, 21, 13, 0, tzinfo=ZoneInfo("Europe/Berlin")), 0.15),
        (datetime(2025, 8, 21, 14, 0, tzinfo=ZoneInfo("Europe/Berlin")), 0.20),
    ]


@pytest.fixture
async def coordinator_update_patch(mock_coordinator_data: list[tuple[datetime, float]]):
    """Patch the coordinator's update method."""

    async def mock_update():
        return mock_coordinator_data

    with patch(
        "custom_components.delayed_charging.coordinator.ElectricityPriceCoordinator._async_update_data",
        side_effect=mock_update,
    ):
        yield
