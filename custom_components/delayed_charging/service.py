import datetime
import logging

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
    relative_time_series_in_past = [(now - dt, price) for dt, price in timeseries if dt <= now]

    if len(relative_time_series_in_past) == 0:
        _LOGGER.error("No current price data available.")
        return None
    else:
        current_price = relative_time_series_in_past[-1][1]
        _LOGGER.debug("Current price: %s", current_price)
        return current_price
