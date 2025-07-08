#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import logging
import pprint
from custom_components.delayed_charging.service import (
    delayed_charging_is_active_today,
    get_charging_start,
    get_current_price,
    get_pricing_info,
)

logging.basicConfig(level=logging.DEBUG)

prices = asyncio.run(get_pricing_info())
pprint.pprint(prices)

charging_start = get_charging_start(prices)
if charging_start:
    print(f"Charging should start at: {charging_start}")
else:
    print("No suitable charging start time found.")

delayed_charging_active = delayed_charging_is_active_today(prices)
if delayed_charging_active:
    print("Delayed charging is active today.")
else:
    print("Delayed charging is not active today.")

current_price = get_current_price(prices)

if current_price is not None:
    print(f"Current price is: {current_price:.2f}")
else:
    print("No current price data available.")
