"""
    SSI API Interface Definition
    Copyright (C) 2021  Arun Annamalai, Emerson Dove, Brandon Fan

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

import time
import warnings
from datetime import datetime as dt, timezone

import pandas as pd

from trapilot.exchanges.interfaces.exchange_interface import ExchangeInterface
from trapilot.exchanges.orders.limit_order import LimitOrder
from trapilot.exchanges.orders.market_order import MarketOrder
from trapilot.exchanges.orders.stop_loss import StopLossOrder
from trapilot.exchanges.orders.take_profit import TakeProfitOrder
from trapilot.utils import utils as utils
from trapilot.utils.exceptions import APIException
from trapilot.utils.time_builder import build_minute, time_interval_to_seconds, number_interval_to_string


class SsiInterface(ExchangeInterface):
    def __init__(self, exchange_name, authenticated_api):
        self.__unique_assets = None
        super().__init__(exchange_name, authenticated_api, valid_resolutions=[60, 60 * 5, 60 * 15,
                                                                              60 * 60 * 24])

    def init_exchange(self):
        try:
            account_info = self.calls.get_account()
        except Exception as e:
            raise APIException(e.__str__() + ". Are you trying to use your normal exchange keys "
                                             "while in sandbox mode? \nTry toggling the \'sandbox\' setting "
                                             "in your user_data/keys.json or check if the keys were input correctly into your "
                                             "user_data/keys.json.")
        try:
            if account_info['account_blocked']:
                warnings.warn('Your SSI account is indicated as blocked for trading....')
        except KeyError:
            raise LookupError("SSI API call failed")

        filtered_assets = []
        self.__unique_assets = filtered_assets

    def get_products(self) -> dict:
        assets = {}
        return assets