"""
    __init__ file to give the module access to the libraries.
    Copyright (C) 2021

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import trapilot.blankly.data
import trapilot.blankly.indicators
import trapilot.blankly.utils.utils
from trapilot.blankly.deployment.reporter_headers import Reporter as __Reporter_Headers
from trapilot.blankly.enums import OrderStatus, OrderType, Side, TimeInForce
from trapilot.blankly.exchanges.interfaces.abc_exchange_interface import (
    ABCExchangeInterface as Interface,
)
from trapilot.blankly.exchanges.interfaces.alpaca.alpaca import Alpaca
from trapilot.blankly.exchanges.interfaces.binance.binance import Binance
from trapilot.blankly.exchanges.interfaces.binance_futures.binance_futures import BinanceFutures
from trapilot.blankly.exchanges.interfaces.paper_trade.paper_trade import PaperTrade
from trapilot.blankly.exchanges.managers.general_stream_manager import GeneralManager
from trapilot.blankly.exchanges.managers.orderbook_manager import OrderbookManager
from trapilot.blankly.exchanges.managers.ticker_manager import TickerManager
from trapilot.blankly.frameworks.model.model import Model as Model
from trapilot.blankly.frameworks.multiprocessing.bot import Trapilot
from trapilot.blankly.frameworks.screener.screener import Screener
from trapilot.blankly.frameworks.screener.screener_state import ScreenerState
from trapilot.blankly.frameworks.strategy import FuturesStrategy, FuturesStrategyState
from trapilot.blankly.frameworks.strategy import Strategy as Strategy
from trapilot.blankly.frameworks.strategy import StrategyState as StrategyState
from trapilot.blankly.utils import time_builder
from trapilot.blankly.utils.scheduler import Scheduler
from trapilot.blankly.utils.utils import trunc

__version__ = "2024.3-dev"
is_deployed = False
_screener_runner = None

_backtesting = trapilot.blankly.utils.check_backtesting()
try:
    from blankly_external import Reporter as __Reporter

    reporter = __Reporter_Headers()
    is_deployed = True
except ImportError:
    reporter = __Reporter_Headers()
