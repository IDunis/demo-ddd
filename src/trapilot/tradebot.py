"""
Trapilot is the main module of this bot. It contains the class Trapilot()
"""
import logging
import traceback
from copy import deepcopy
from datetime import datetime, time, timedelta, timezone
from math import isclose
from threading import Lock
from time import sleep
from typing import Any, Dict, List, Optional, Tuple

from schedule import Scheduler

from trapilot.constants import Config, ExchangeConfig
from trapilot.enums import (ExitCheckTuple, ExitType, RPCMessageType, SignalDirection, State, TradingMode)
from trapilot.mixins import LoggingMixin
from trapilot.persistence import init_db
from trapilot.resolvers import ExchangeResolver, StrategyResolver
from trapilot.rpc.rpc_manager import RPCManager
from trapilot.strategy.interface import IStrategy
from trapilot.wallets import Wallets


logger = logging.getLogger(__name__)


class TradeBot(LoggingMixin):
    """
    Trapilot is the main class of the bot.
    This is from here the bot start its logic.
    """

    def __init__(self, config: Config) -> None:
        """
        Init all variables and objects the bot needs to work
        :param config: configuration dict, you can use Configuration.get_config()
        to get the config dict.
        """
        self.active_pair_whitelist: List[str] = []

        # Init bot state
        self.state = State.STOPPED

        # Init objects
        self.config = config
        exchange_config: ExchangeConfig = deepcopy(config['exchange'])
        # Remove credentials from original exchange config to avoid accidental credentail exposure
        # remove_exchange_credentials(config['exchange'], True)

        self.strategy: IStrategy = StrategyResolver.load_strategy(self.config)

        # Check config consistency here since strategies can set certain options
        # validate_config_consistency(config)

        self.exchange = ExchangeResolver.load_exchange(
            self.config, exchange_config=exchange_config, load_leverage_tiers=True)

        init_db(self.config['db_url'])

        self.wallets = Wallets(self.config, self.exchange)

        self.trading_mode: TradingMode = self.config.get('trading_mode', TradingMode.SPOT)
        self.last_process: Optional[datetime] = None

        # RPC runs in separate threads, can start handling external commands just after
        # initialization, even before Freqtradebot has a chance to start its throttling,
        # so anything in the Freqtradebot instance should be ready (initialized), including
        # the initial state of the bot.
        # Keep this at the end of this initialization method.
        self.rpc: RPCManager = RPCManager(self)

        # Set initial bot state from config
        initial_state = self.config.get('initial_state')
        self.state = State[initial_state.upper()] if initial_state else State.STOPPED

        # Protect exit-logic from forcesell and vice versa
        self._exit_lock = Lock()
        # LoggingMixin.__init__(self, logger, timeframe_to_seconds(self.strategy.timeframe))

        self._schedule = Scheduler()

        if self.trading_mode == TradingMode.FUTURES:

            def update():
                self.update_funding_fees()
                self.wallets.update()

            # TODO: This would be more efficient if scheduled in utc time, and performed at each
            # TODO: funding interval, specified by funding_fee_times on the exchange classes
            for time_slot in range(0, 24):
                for minutes in [1, 31]:
                    t = str(time(time_slot, minutes, 2))
                    self._schedule.every().day.at(t).do(update)

    def notify_status(self, msg: str, msg_type=RPCMessageType.STATUS) -> None:
        """
        Public method for users of this class (worker, etc.) to send notifications
        via RPC about changes in the bot status.
        """
        # self.rpc.send_msg({
        #     'type': msg_type,
        #     'status': msg
        # })

    def cleanup(self) -> None:
        """
        Cleanup pending resources on an already stopped bot
        :return: None
        """
        logger.info('Cleaning up modules ...')

    def startup(self) -> None:
        """
        Called on startup and after reloading the bot - triggers notifications and
        performs startup tasks
        """
        # migrate_binance_futures_names(self.config)
        # set_startup_time()

        self.rpc.startup_messages(self.config)


