#!/usr/bin/env python3
import asyncio
import logging
import pprint

from custom_components.delayed_charging.service import (
    delayed_charging_is_active_today,
    get_charging_start,
    get_current_price,
)
from custom_components.delayed_charging.smard import get_pricing_info

logging.basicConfig(level=logging.DEBUG)

THRESH = 0.0

prices = asyncio.run(get_pricing_info("254"))
pprint.pprint(prices)

charging_start = get_charging_start(prices, THRESH)
if charging_start:
    print(f"Charging should start at: {charging_start}")
else:
    print("No suitable charging start time found.")

delayed_charging_active = delayed_charging_is_active_today(prices, THRESH)
if delayed_charging_active:
    print("Delayed charging is active today.")
else:
    print("Delayed charging is not active today.")

current_price = get_current_price(prices)

if current_price is not None:
    print(f"Current price is: {current_price:.2f}")
else:
    print("No current price data available.")
