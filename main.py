#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import logging
import pprint
from custom_components.delayed_charging.service import get_pricing_info

logging.basicConfig(level=logging.DEBUG)

prices = asyncio.run(get_pricing_info())
pprint.pprint(prices)
