import datetime
import logging

import aiohttp

from custom_components.delayed_charging.service import SYSTEM_TZ, dtfmt, same_date, ts2dt

_LOGGER = logging.getLogger(__name__)

SMARD_COUNTRIES = {
    "Germany/Luxembourg": 4169,
    "Neighboring DE/LU": 5078,
    "Belgium": 4996,
    "Norway 2": 4997,
    "Austria": 4170,
    "Denmark 1": 252,
    "Denmark 2": 253,
    "France": 254,
    "Italy (North)": 255,
    "Netherlands": 256,
    "Poland": 257,
    "Sweden 4": 258,
    "Switzerland": 259,
    "Slovenia": 260,
    "Czech Republic": 261,
    "Hungary": 262,
}


async def get_pricing_info(country: str = "Germany/Luxembourg"):
    """Get electricity price as function of time for current day."""

    empty_series: list[tuple[datetime.datetime, float]] = []

    if country not in SMARD_COUNTRIES:
        _LOGGER.error("Country %s not supported. Supported countries: %s", country, list(SMARD_COUNTRIES.keys()))
        return empty_series

    country_id = SMARD_COUNTRIES[country]

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
                f"https://www.smard.de/app/chart_data/{country_id}/DE/index_quarterhour.json"
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
                f"https://www.smard.de/app/chart_data/{country_id}/DE/{country_id}_DE_quarterhour_{req_ts}.json"
            ) as response:
                data = await response.json()
                timeseries = data.get("series")
        except (aiohttp.ClientError, aiohttp.ClientPayloadError) as e:
            _LOGGER.error("Error fetching timeseries data from SMARD: %s", e)
            return empty_series

    filtered_series = [
        (dt, item[1]) for item in timeseries if same_date(dt := ts2dt(item[0]), last_midnight) and item[1] is not None
    ]
    if len(filtered_series) == 0:
        _LOGGER.error("No time series data could be retrieved.")
    return filtered_series
