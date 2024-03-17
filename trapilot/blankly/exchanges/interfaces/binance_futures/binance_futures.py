"""
    Binance Futures Exchange object.
    Copyright (C) 2021 Matias Kotlik

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

from binance.client import Client

from trapilot.blankly.exchanges.auth.auth_constructor import AuthConstructor
from trapilot.blankly.exchanges.futures.futures_exchange import FuturesExchange
from trapilot.blankly.exchanges.interfaces.binance_futures.binance_futures_interface import (
    BinanceFuturesInterface,
)
from trapilot.blankly.exchanges.interfaces.futures_exchange_interface import (
    FuturesExchangeInterface,
)


class BinanceFutures(FuturesExchange):

    def __init__(
        self,
        portfolio_name=None,
        keys_path="user_data/keys.json",
        preferences_path=None,
    ):
        super().__init__("binance_futures", portfolio_name, preferences_path)

        # Load auth from keys file
        auth = AuthConstructor(
            keys_path, portfolio_name, "binance", ["api_key", "api_secret", "dry_run"]
        )

        self.__calls = Client(
            api_key=auth.keys["api_key"],
            api_secret=auth.keys["api_secret"],
            testnet=auth.keys["dry_run"],
        )

        self.__interface = BinanceFuturesInterface(self.exchange_type, self.calls)

        self.initialize()

    @property
    def calls(self):
        return self.__calls

    @property
    def interface(self) -> FuturesExchangeInterface:
        return self.__interface
