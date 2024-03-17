"""
    Abstraction for creating interval driven user strategies for trading futures.
    Copyright (C) 2022 Matias Kotlik

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

import typing

from trapilot.blankly.exchanges.futures.futures_exchange import FuturesExchange
from trapilot.blankly.exchanges.futures.futures_strategy_logger import \
    FuturesStrategyLogger
from trapilot.blankly.exchanges.interfaces.futures_exchange_interface import \
    FuturesExchangeInterface
from trapilot.blankly.exchanges.interfaces.paper_trade.backtest_result import \
    BacktestResult
from trapilot.blankly.frameworks.strategy.strategy import Strategy
from trapilot.blankly.frameworks.strategy.strategy_base import StrategyBase


class FuturesStrategy(Strategy):

    def teardown(self):
        pass
