import logging
import aiohttp
import datetime

_LOGGER = logging.getLogger(__name__)

SYSTEM_TZ = datetime.datetime.now().astimezone().tzinfo


def ts2dt(timestamp: int) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(timestamp / 1e3, tz=SYSTEM_TZ)


def same_date(dt1: datetime.datetime, dt2: datetime.datetime) -> bool:
    d1 = dt1.date()
    d2 = dt2.date()
    return d1 == d2


def dtfmt(dt: datetime.datetime) -> str:
    return dt.strftime("%Y-%m-%d %H-%M-%S")


async def get_pricing_info():
    """Get electricity price as function of time for current day."""

    empty_series: list[tuple[datetime.datetime, float]] = []

    now = datetime.datetime.now(SYSTEM_TZ)
    today = now.date()
    midnight = datetime.time(tzinfo=SYSTEM_TZ)
    last_midnight = datetime.datetime.combine(today, midnight)

    _LOGGER.debug("Now: %s", dtfmt(now))
    _LOGGER.debug("Today: %s", today)
    _LOGGER.debug("Last midnight: %s", dtfmt(last_midnight))
    _LOGGER.debug("System timezone: %s", SYSTEM_TZ)

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(
                "https://www.smard.de/app/chart_data/4169/DE/index_quarterhour.json"
            ) as response:
                data = await response.json()
                timestamps = data.get("timestamps")

            req_ts = None
            for ts in reversed(timestamps):
                if ts2dt(ts) <= last_midnight:
                    req_ts = ts
                    break
        except (aiohttp.ClientError, aiohttp.ClientPayloadError) as e:
            _LOGGER.error("Error fetching timestamp data from SMARD: %s", e)
            return empty_series

        try:
            async with session.get(
                f"https://www.smard.de/app/chart_data/4169/DE/4169_DE_quarterhour_{req_ts}.json"
            ) as response:
                data = await response.json()
                timeseries = data.get("series")
        except (aiohttp.ClientError, aiohttp.ClientPayloadError) as e:
            _LOGGER.error("Error fetching timeseries data from SMARD: %s", e)
            return empty_series

    filtered_series = [
        (dt, item[1])
        for item in timeseries
        if same_date(dt := ts2dt(item[0]), last_midnight) and item[1] is not None
    ]
    if len(filtered_series) == 0:
        _LOGGER.error("No time series data could be retrieved.")
    return filtered_series


def get_charging_start(
    timeseries: list[tuple[datetime.datetime, float]],
    threshold: float,
) -> datetime.datetime | None:
    series_neg = [item for item in timeseries if item[1] < threshold]

    if len(series_neg) == 0:
        charging_start = None
    else:
        charging_start = series_neg[0][0]

    return charging_start


def delayed_charging_is_active_today(
    timeseries: list[tuple[datetime.datetime, float]],
    threshold: float,
) -> bool:
    return any(item[1] < threshold for item in timeseries)


def get_current_price(
    timeseries: list[tuple[datetime.datetime, float]],
) -> float | None:
    now = datetime.datetime.now(SYSTEM_TZ)
    relative_time_series_in_past = [
        (now - dt, price) for dt, price in timeseries if dt <= now
    ]

    if len(relative_time_series_in_past) == 0:
        _LOGGER.error("No current price data available.")
        return None
    else:
        current_price = relative_time_series_in_past[-1][1]
        _LOGGER.debug("Current price: %s", current_price)
        return current_price
