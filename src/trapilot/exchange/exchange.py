# pragma pylint: disable=W0603
"""
Cryptocurrency Exchanges support
"""
import asyncio
import inspect
import logging
import signal
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from math import floor
from threading import Lock
from typing import Any, Coroutine, Dict, List, Literal, Optional, Tuple, Union

import ccxt
import ccxt.async_support as ccxt_async
from cachetools import TTLCache
from ccxt import TICK_SIZE
from dateutil import parser
from pandas import DataFrame, concat

from trapilot.constants import (Config, ExchangeConfig, PairWithTimeframe)


logger = logging.getLogger(__name__)


class Exchange:
    def __init__(self, config: Config, *, exchange_config: Optional[ExchangeConfig] = None,
                 validate: bool = True, load_leverage_tiers: bool = False) -> None:
        """
        Initializes this module with the given config,
        it does basic validation whether the specified exchange and pairs are valid.
        :return: None
        """
        self._api: ccxt.Exchange
        self._api_async: ccxt_async.Exchange = None
        self._markets: Dict = {}
        self._trading_fees: Dict[str, Any] = {}
        self._leverage_tiers: Dict[str, List[Dict]] = {}
        # Lock event loop. This is necessary to avoid race-conditions when using force* commands
        # Due to funding fee fetching.
        self._loop_lock = Lock()
        self.loop = self._init_async_loop()
        self._config: Config = {}

        self._config.update(config)

        # Holds last candle refreshed time of each pair
        self._pairs_last_refresh_time: Dict[PairWithTimeframe, int] = {}
        # Timestamp of last markets refresh
        self._last_markets_refresh: int = 0

        # Cache for 10 minutes ...
        self._cache_lock = Lock()
        self._fetch_tickers_cache: TTLCache = TTLCache(maxsize=2, ttl=60 * 10)
        # Cache values for 300 to avoid frequent polling of the exchange for prices
        # Caching only applies to RPC methods, so prices for open trades are still
        # refreshed once every iteration.
        # Shouldn't be too high either, as it'll freeze UI updates in case of open orders.
        self._exit_rate_cache: TTLCache = TTLCache(maxsize=100, ttl=300)
        self._entry_rate_cache: TTLCache = TTLCache(maxsize=100, ttl=300)

        # Holds candles
        self._klines: Dict[PairWithTimeframe, DataFrame] = {}

        # Holds all open sell orders for dry_run
        self._dry_run_open_orders: Dict[str, Any] = {}

    def _init_async_loop(self) -> asyncio.AbstractEventLoop:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop
