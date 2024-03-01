"""
This module contains class to define a RPC communications
"""
import logging
from abc import abstractmethod
from datetime import date, datetime, timedelta, timezone
from math import isnan
from typing import Any, Dict, Generator, List, Optional, Sequence, Tuple, Union

import psutil
from dateutil.relativedelta import relativedelta
from dateutil.tz import tzlocal
from numpy import NAN, inf, int64, mean
from pandas import DataFrame, NaT
from sqlalchemy import func, select

from trapilot.constants import Config
from trapilot.exceptions import PricingError, ExchangeError
from trapilot.enums import State, TradingMode
from trapilot.persistence import Trade
from trapilot.rpc.rpc_types import RPCSendMsg
from trapilot.util import (dt_humanize, shorten_date)

logger = logging.getLogger(__name__)


class RPCException(Exception):
    """
    Should be raised with a rpc-formatted message in an _rpc_* method
    if the required state is wrong, i.e.:

    raise RPCException('*Status:* `no active trade`')
    """

    def __init__(self, message: str) -> None:
        super().__init__(self)
        self.message = message

    def __str__(self):
        return self.message

    def __json__(self):
        return {
            'msg': self.message
        }


class RPCHandler:

    def __init__(self, rpc: 'RPC', config: Config) -> None:
        """
        Initializes RPCHandlers
        :param rpc: instance of RPC Helper class
        :param config: Configuration object
        :return: None
        """
        self._rpc = rpc
        self._config: Config = config

    @property
    def name(self) -> str:
        """ Returns the lowercase name of the implementation """
        return self.__class__.__name__.lower()

    @abstractmethod
    def cleanup(self) -> None:
        """ Cleanup pending module resources """

    @abstractmethod
    def send_msg(self, msg: RPCSendMsg) -> None:
        """ Sends a message to all registered rpc modules """


class RPC:
    """
    RPC class can be used to have extra feature, like bot data, and access to DB data
    """

    def __init__(self, tradebot) -> None:
        """
        Initializes all enabled rpc modules
        :param tradebot: Instance of a trading bot
        :return: None
        """
        self._tradebot = tradebot
        self._config: Config = tradebot.config

    def _rpc_start(self) -> Dict[str, str]:
        """ Handler for start """
        if self._tradebot.state == State.RUNNING:
            return {'status': 'already running'}

        self._tradebot.state = State.RUNNING
        return {'status': 'starting trader ...'}

    def _rpc_stop(self) -> Dict[str, str]:
        """ Handler for stop """
        if self._tradebot.state == State.RUNNING:
            self._tradebot.state = State.STOPPED
            return {'status': 'stopping trader ...'}

        return {'status': 'already stopped'}

    def _rpc_reload_config(self) -> Dict[str, str]:
        """ Handler for reload_config. """
        self._tradebot.state = State.RELOAD_CONFIG
        return {'status': 'Reloading config ...'}

    def _rpc_trade_status(self, trade_ids: List[int] = []) -> List[Dict[str, Any]]:
        """
        Below follows the RPC backend it is prefixed with rpc_ to raise awareness that it is
        a remotely exposed function
        """
        # Fetch open trades
        if trade_ids:
            trades: Sequence[Trade] = Trade.get_trades(trade_filter=Trade.id.in_(trade_ids)).all()
        else:
            trades = Trade.get_open_trades()

        if not trades:
            raise RPCException('no active trade')
        else:
            results = []
            for trade in trades:
                current_profit_fiat: Optional[float] = None
                total_profit_fiat: Optional[float] = None

                # prepare open orders details
                oo_details: Optional[str] = ""
                oo_details_lst = [
                    f'({oo.order_type} {oo.side} rem={oo.safe_remaining:.8f})'
                    for oo in trade.open_orders
                    if oo.ft_order_side not in ['stoploss']
                ]
                oo_details = ', '.join(oo_details_lst)

                total_profit_abs = 0.0
                total_profit_ratio: Optional[float] = None
                # calculate profit and send message to user
                if trade.is_open:
                    try:
                        current_rate = self._tradebot.exchange.get_rate(
                            trade.pair, side='exit', is_short=trade.is_short, refresh=False)
                    except (ExchangeError, PricingError):
                        current_rate = NAN
                    if len(trade.select_filled_orders(trade.entry_side)) > 0:

                        current_profit = current_profit_abs = current_profit_fiat = NAN
                        if not isnan(current_rate):
                            prof = trade.calculate_profit(current_rate)
                            current_profit = prof.profit_ratio
                            current_profit_abs = prof.profit_abs
                            total_profit_abs = prof.total_profit
                            total_profit_ratio = prof.total_profit_ratio
                    else:
                        current_profit = current_profit_abs = current_profit_fiat = 0.0

                else:
                    # Closed trade ...
                    current_rate = trade.close_rate
                    current_profit = trade.close_profit or 0.0
                    current_profit_abs = trade.close_profit_abs or 0.0

                # Calculate fiat profit
                if not isnan(current_profit_abs) and self._fiat_converter:
                    current_profit_fiat = self._fiat_converter.convert_amount(
                        current_profit_abs,
                        self._tradebot.config['stake_currency'],
                        self._tradebot.config['fiat_display_currency']
                    )
                    total_profit_fiat = self._fiat_converter.convert_amount(
                        total_profit_abs,
                        self._tradebot.config['stake_currency'],
                        self._tradebot.config['fiat_display_currency']
                    )

                # Calculate guaranteed profit (in case of trailing stop)
                stop_entry = trade.calculate_profit(trade.stop_loss)

                stoploss_entry_dist = stop_entry.profit_abs
                stoploss_entry_dist_ratio = stop_entry.profit_ratio

                # calculate distance to stoploss
                stoploss_current_dist = trade.stop_loss - current_rate
                stoploss_current_dist_ratio = stoploss_current_dist / current_rate

                trade_dict = trade.to_json()
                trade_dict.update(dict(
                    close_profit=trade.close_profit if not trade.is_open else None,
                    current_rate=current_rate,
                    profit_ratio=current_profit,
                    profit_pct=round(current_profit * 100, 2),
                    profit_abs=current_profit_abs,
                    profit_fiat=current_profit_fiat,
                    total_profit_abs=total_profit_abs,
                    total_profit_fiat=total_profit_fiat,
                    total_profit_ratio=total_profit_ratio,
                    stoploss_current_dist=stoploss_current_dist,
                    stoploss_current_dist_ratio=round(stoploss_current_dist_ratio, 8),
                    stoploss_current_dist_pct=round(stoploss_current_dist_ratio * 100, 2),
                    stoploss_entry_dist=stoploss_entry_dist,
                    stoploss_entry_dist_ratio=round(stoploss_entry_dist_ratio, 8),
                    open_orders=oo_details
                ))
                results.append(trade_dict)
            return results

    def _rpc_status_table(self, stake_currency: str,
                          fiat_display_currency: str) -> Tuple[List, List, float]:
        trades: List[Trade] = Trade.get_open_trades()
        nonspot = self._config.get('trading_mode', TradingMode.SPOT) != TradingMode.SPOT
        if not trades:
            raise RPCException('no active trade')
        else:
            trades_list = []
            fiat_profit_sum = NAN
            for trade in trades:
                # calculate profit and send message to user
                try:
                    current_rate = self._tradebot.exchange.get_rate(
                        trade.pair, side='exit', is_short=trade.is_short, refresh=False)
                except (PricingError, ExchangeError):
                    current_rate = NAN
                    trade_profit = NAN
                    profit_str = f'{NAN:.2%}'
                else:
                    if trade.nr_of_successful_entries > 0:
                        profit = trade.calculate_profit(current_rate)
                        trade_profit = profit.profit_abs
                        profit_str = f'{profit.profit_ratio:.2%}'
                    else:
                        trade_profit = 0.0
                        profit_str = f'{0.0:.2f}'
                direction_str = ('S' if trade.is_short else 'L') if nonspot else ''
                if self._fiat_converter:
                    fiat_profit = self._fiat_converter.convert_amount(
                        trade_profit,
                        stake_currency,
                        fiat_display_currency
                    )
                    if not isnan(fiat_profit):
                        profit_str += f" ({fiat_profit:.2f})"
                        fiat_profit_sum = fiat_profit if isnan(fiat_profit_sum) \
                            else fiat_profit_sum + fiat_profit

                active_attempt_side_symbols = [
                    '*' if (oo and oo.ft_order_side == trade.entry_side) else '**'
                    for oo in trade.open_orders
                ]

                # exemple: '*.**.**' trying to enter, exit and exit with 3 different orders
                active_attempt_side_symbols_str = '.'.join(active_attempt_side_symbols)

                detail_trade = [
                    f'{trade.id} {direction_str}',
                    trade.pair + active_attempt_side_symbols_str,
                    shorten_date(dt_humanize(trade.open_date, only_distance=True)),
                    profit_str
                ]

                if self._config.get('position_adjustment_enable', False):
                    max_entry_str = ''
                    if self._config.get('max_entry_position_adjustment', -1) > 0:
                        max_entry_str = f"/{self._config['max_entry_position_adjustment'] + 1}"
                    filled_entries = trade.nr_of_successful_entries
                    detail_trade.append(f"{filled_entries}{max_entry_str}")
                trades_list.append(detail_trade)
            profitcol = "Profit"
            if self._fiat_converter:
                profitcol += " (" + fiat_display_currency + ")"

            columns = [
                'ID L/S' if nonspot else 'ID',
                'Pair',
                'Since',
                profitcol]
            if self._config.get('position_adjustment_enable', False):
                columns.append('# Entries')
            return trades_list, columns, fiat_profit_sum
