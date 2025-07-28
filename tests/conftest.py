from unittest.mock import patch
from zoneinfo import ZoneInfo

import pytest

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
