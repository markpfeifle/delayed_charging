import logging
import aiohttp
import datetime
from datetime import timezone

_LOGGER = logging.getLogger(__name__)

THRESH = 40


def ts2dt(timestamp: int) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(timestamp / 1e3, timezone.utc)


def same_date(dt1: datetime.datetime, dt2: datetime.datetime) -> bool:
    d1 = dt1.date()
    d2 = dt2.date()
    return d1 == d2


def dtfmt(dt: datetime.datetime) -> str:
    return dt.strftime("%Y-%m-%d %H-%M-%S")


async def get_delayed_charging_start():
    """Get the delayed charging start time."""

    now_utc = datetime.datetime.now(timezone.utc)
    _LOGGER.debug(dtfmt(now_utc))

    midnight_utc = datetime.time(tzinfo=timezone.utc)

    today_utc = now_utc.date()
    today_midnight_utc = datetime.datetime.combine(today_utc, midnight_utc)

    _LOGGER.debug(dtfmt(today_midnight_utc))

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://www.smard.de/app/chart_data/4169/DE/index_quarterhour.json"
        ) as response:
            data = await response.json()
            timestamps = data.get("timestamps")

        req_ts = None
        for ts in reversed(timestamps):
            if ts2dt(ts) < today_midnight_utc:
                req_ts = ts
                break

        if req_ts:
            _LOGGER.debug(dtfmt(ts2dt(req_ts)))

        async with session.get(
            f"https://www.smard.de/app/chart_data/4169/DE/4169_DE_quarterhour_{req_ts}.json"
        ) as response:
            data = await response.json()
            timeseries = data.get("series")

    filtered_series = [
        (dt, item[1])
        for item in timeseries
        if same_date(dt := ts2dt(item[0]), today_midnight_utc) and item[1] is not None
    ]

    for dt, val in filtered_series:
        _LOGGER.debug(dtfmt(dt), val)

    series_neg = [item for item in filtered_series if item[1] < THRESH]

    for dt, val in series_neg:
        _LOGGER.debug(dtfmt(dt), val)

    if len(series_neg) == 0:
        charging_start = today_midnight_utc
    else:
        charging_start = series_neg[0][0]

    _LOGGER.debug(charging_start)

    return charging_start
