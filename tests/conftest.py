from datetime import datetime as datetime_class
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
def mock_coordinator_data() -> list[tuple[datetime_class, float]]:
    """Mock data that the coordinator should return."""
    return [
        (datetime_class(2025, 8, 21, 12, 0, tzinfo=ZoneInfo("Europe/Berlin")), 0.10),
        (datetime_class(2025, 8, 21, 13, 0, tzinfo=ZoneInfo("Europe/Berlin")), 0.15),
        (datetime_class(2025, 8, 21, 14, 0, tzinfo=ZoneInfo("Europe/Berlin")), 0.20),
    ]


@pytest.fixture
def mock_chart_data() -> list[dict[str, float | str]]:
    return [
        {"x": "2025-08-21T12:00:00+02:00", "y": 0.1},
        {"x": "2025-08-21T13:00:00+02:00", "y": 0.15},
        {"x": "2025-08-21T14:00:00+02:00", "y": 0.2},
    ]


@pytest.fixture
async def coordinator_update_patch(mock_coordinator_data: list[tuple[datetime_class, float]]):
    """Patch the coordinator's update method."""

    async def mock_update():
        return mock_coordinator_data

    with patch(
        "custom_components.delayed_charging.coordinator.ElectricityPriceCoordinator._async_update_data",
        side_effect=mock_update,
    ):
        yield


""" @pytest.fixture
def mock_datetime_now():
    def _mock_datetime_now(fake_now: datetime_class | None = None, module: str | None = None):
        real_datetime_class = datetime_class
        if fake_now is None:
            fake_now = datetime_class(2025, 7, 28, 10, 15, 0, tzinfo=ZoneInfo("Europe/Berlin"))
        if module is None:
            module = "smard"

        patch_path = f"custom_components.delayed_charging.{module}.datetime.datetime"
        with patch(patch_path) as mock_datetime:
            mock_datetime.now.return_value = fake_now
            mock_datetime.side_effect = \
                lambda *args, **kwargs: datetime_class(*args, **kwargs)  # type: ignore
            mock_datetime.combine.side_effect = \
                lambda *args, **kwargs: real_datetime_class.combine(*args, **kwargs)  # type: ignore
            mock_datetime.fromtimestamp.side_effect = \
                lambda *args, **kwargs: real_datetime_class.fromtimestamp(*args, **kwargs)  # type: ignore
            yield fake_now

    return _mock_datetime_now """
