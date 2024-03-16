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

import trapilot.data
import trapilot.indicators
import trapilot.utils.utils
from trapilot.deployment.reporter_headers import Reporter as __Reporter_Headers
from trapilot.enums import OrderStatus, OrderType, Side, TimeInForce
from trapilot.exchanges.interfaces.abc_exchange_interface import \
    ABCExchangeInterface as Interface
from trapilot.exchanges.interfaces.alpaca.alpaca import Alpaca
from trapilot.exchanges.interfaces.binance.binance import Binance
from trapilot.exchanges.interfaces.binance_futures.binance_futures import \
    BinanceFutures
from trapilot.exchanges.interfaces.paper_trade.paper_trade import PaperTrade
from trapilot.exchanges.managers.general_stream_manager import GeneralManager
from trapilot.exchanges.managers.orderbook_manager import OrderbookManager
from trapilot.exchanges.managers.ticker_manager import TickerManager
from trapilot.frameworks.model.model import Model as Model
from trapilot.frameworks.multiprocessing.bot import Trapilot
from trapilot.frameworks.screener.screener import Screener
from trapilot.frameworks.screener.screener_state import ScreenerState
from trapilot.frameworks.strategy import FuturesStrategy, FuturesStrategyState
from trapilot.frameworks.strategy import Strategy as Strategy
from trapilot.frameworks.strategy import StrategyState as StrategyState
from trapilot.utils import time_builder
from trapilot.utils.scheduler import Scheduler
from trapilot.utils.utils import trunc

__version__ = "2024.3-dev"
is_deployed = False
_screener_runner = None

_backtesting = trapilot.utils.check_backtesting()
try:
    from blankly_external import Reporter as __Reporter

    reporter = __Reporter_Headers()
    is_deployed = True
except ImportError:
    reporter = __Reporter_Headers()
