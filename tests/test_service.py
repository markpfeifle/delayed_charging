"""Tests for service.py module."""

import datetime
from unittest.mock import MagicMock, patch

from custom_components.delayed_charging.service import (
    SYSTEM_TZ,
    delayed_charging_is_active_today,
    dtfmt,
    get_charging_start,
    get_current_price,
    same_date,
    ts2dt,
)


def test_ts2dt():
    """Test timestamp to datetime conversion."""
    # Test a known timestamp (2025-07-01 03:00:00)
    timestamp = 1751331600000  # milliseconds
    expected_dt = datetime.datetime(2025, 7, 1, 3, 0, 0, tzinfo=SYSTEM_TZ)
    assert ts2dt(timestamp) == expected_dt


def test_same_date():
    """Test same_date function."""
    dt1 = datetime.datetime(2025, 7, 28, 10, 0, 0, tzinfo=SYSTEM_TZ)
    dt2 = datetime.datetime(2025, 7, 28, 15, 30, 0, tzinfo=SYSTEM_TZ)
    dt3 = datetime.datetime(2025, 7, 29, 10, 0, 0, tzinfo=SYSTEM_TZ)

    assert same_date(dt1, dt2) is True
    assert same_date(dt1, dt3) is False


def test_dtfmt():
    """Test datetime formatting."""
    dt = datetime.datetime(2025, 7, 28, 10, 0, 0, tzinfo=SYSTEM_TZ)
    assert dtfmt(dt) == "2025-07-28 10-00-00"


def test_get_charging_start():
    """Test get_charging_start function."""
    midnight = datetime.datetime(2025, 7, 28, 0, 0, 0, tzinfo=SYSTEM_TZ)
    timeseries = [
        (midnight, 15.0),
        (midnight + datetime.timedelta(hours=1), 12.0),
        (midnight + datetime.timedelta(hours=2), 8.0),
        (midnight + datetime.timedelta(hours=3), 18.0),
    ]

    # Test with threshold that finds a match
    assert get_charging_start(timeseries, 10.0) == midnight + datetime.timedelta(hours=2)

    # Test with threshold that doesn't find a match
    assert get_charging_start(timeseries, 5.0) is None

    # Test with empty timeseries
    assert get_charging_start([], 10.0) is None


def test_delayed_charging_is_active_today():
    """Test delayed_charging_is_active_today function."""
    midnight = datetime.datetime(2025, 7, 28, 0, 0, 0, tzinfo=SYSTEM_TZ)
    timeseries = [
        (midnight, 15.0),
        (midnight + datetime.timedelta(hours=1), 12.0),
        (midnight + datetime.timedelta(hours=2), 8.0),
        (midnight + datetime.timedelta(hours=3), 18.0),
    ]

    # Test when charging should be active (price below threshold)
    assert delayed_charging_is_active_today(timeseries, 10.0) is True

    # Test when charging should not be active (all prices above threshold)
    assert delayed_charging_is_active_today(timeseries, 5.0) is False

    # Test with empty timeseries
    assert delayed_charging_is_active_today([], 10.0) is False


@patch("custom_components.delayed_charging.service.datetime")
def test_get_current_price(mock_datetime: MagicMock):
    """Test get_current_price function."""
    now = datetime.datetime(2025, 7, 28, 10, 15, 0, tzinfo=SYSTEM_TZ)
    mock_datetime.datetime.now.return_value = now

    timeseries = [
        (datetime.datetime(2025, 7, 28, 9, 0, 0, tzinfo=SYSTEM_TZ), 15.0),
        (datetime.datetime(2025, 7, 28, 10, 0, 0, tzinfo=SYSTEM_TZ), 12.0),
        (datetime.datetime(2025, 7, 28, 11, 0, 0, tzinfo=SYSTEM_TZ), 8.0),
    ]

    # Test getting current price
    assert get_current_price(timeseries) == 12.0

    # Test with empty timeseries
    assert get_current_price([]) is None

    # Test with only future prices
    future_series = [(now + datetime.timedelta(hours=1), 8.0)]
    assert get_current_price(future_series) is None
