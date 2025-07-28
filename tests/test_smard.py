"""Tests for smard.py module."""

from datetime import datetime
from typing import cast
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiohttp import ClientError, ClientPayloadError, web

from custom_components.delayed_charging.service import SYSTEM_TZ
from custom_components.delayed_charging.smard import get_pricing_info

TIMESTAMPS_HAPPY = {
    "timestamps": [
        1753484400000,  # 2025-07-26 01:00:00 (CEST)
        1753570800000,  # 2025-07-27 01:00:00 (CEST)
        1753657200000,  # 2025-07-28 01:00:00 (CEST)
    ]
}

TIMESERIES_HAPPY = {
    "series": [
        [1753657200000, 15.0],  # 2025-07-28 01:00:00 (CEST)
        [1753660800000, 12.0],  # 2025-07-28 02:00:00 (CEST)
        [1753664400000, 18.0],  # 2025-07-28 03:00:00 (CEST)
    ]
}

TIMESTAMPS_EMPTY = {"timestamps": cast(list[int], [])}

TIMESERIES_EMPTY = {"series": cast(list[tuple[int, float]], [])}

INVALID_JSON = web.Response(text="Invalid JSON")


@pytest.fixture
def mock_datetime_now():
    real_datetime_class = datetime
    fake_now = datetime(2025, 7, 28, 10, 15, 0, tzinfo=SYSTEM_TZ)
    with patch("custom_components.delayed_charging.smard.datetime.datetime") as mock_datetime:
        mock_datetime.now.return_value = fake_now
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)  # type: ignore
        mock_datetime.combine.side_effect = lambda *args, **kwargs: real_datetime_class.combine(*args, **kwargs)  # type: ignore
        mock_datetime.fromtimestamp.side_effect = lambda *args, **kwargs: real_datetime_class.fromtimestamp(*args, **kwargs)  # type: ignore
        yield fake_now


async def test_get_pricing_info_success(mock_datetime_now: MagicMock):
    """Test successful API calls."""

    mock_response = AsyncMock()
    mock_response.__aenter__.return_value = mock_response
    mock_response.json.side_effect = [TIMESTAMPS_HAPPY, TIMESERIES_HAPPY]

    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        result = await get_pricing_info("4169")

        assert len(result) == 3
        assert result[0][1] == 15.0
        assert result[1][1] == 12.0
        assert result[2][1] == 18.0
        assert result[0][0] == datetime(2025, 7, 28, 1, 0, 0, tzinfo=SYSTEM_TZ)
        assert result[1][0] == datetime(2025, 7, 28, 2, 0, 0, tzinfo=SYSTEM_TZ)
        assert result[2][0] == datetime(2025, 7, 28, 3, 0, 0, tzinfo=SYSTEM_TZ)


async def test_get_pricing_info_invalid_country(mock_datetime_now: MagicMock):
    """Test with invalid country."""
    result = await get_pricing_info("InvalidCountry")
    assert result == []


async def test_get_pricing_info_empty_timestamps(mock_datetime_now: MagicMock):
    """Test with empty timestamp response."""
    mock_response = AsyncMock()
    mock_response.__aenter__.return_value = mock_response
    mock_response.json.return_value = TIMESTAMPS_EMPTY

    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        result = await get_pricing_info("4169")
        assert result == []


async def test_get_pricing_info_empty_timeseries(mock_datetime_now: MagicMock):
    """Test with empty timeseries response."""
    mock_response = AsyncMock()
    mock_response.__aenter__.return_value = mock_response
    mock_response.json.side_effect = [TIMESTAMPS_HAPPY, TIMESERIES_EMPTY]

    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        result = await get_pricing_info("4169")
        assert result == []


async def test_get_pricing_info_invalid_json(mock_datetime_now: MagicMock):
    """Test with invalid JSON response."""
    mock_response = AsyncMock()
    mock_response.__aenter__.return_value = mock_response
    mock_response.json.side_effect = [INVALID_JSON, INVALID_JSON]

    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        result = await get_pricing_info("4169")
        assert result == []


async def test_get_pricing_info_client_error(mock_datetime_now: MagicMock):
    """Test client error handling."""
    mock_response = AsyncMock()
    mock_response.__aenter__.side_effect = ClientError()

    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        result = await get_pricing_info("4169")
        assert result == []


async def test_get_pricing_info_payload_error(mock_datetime_now: MagicMock):
    """Test payload error handling."""
    mock_response = AsyncMock()
    mock_response.__aenter__.side_effect = ClientPayloadError()

    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        result = await get_pricing_info("4169")
        assert result == []
