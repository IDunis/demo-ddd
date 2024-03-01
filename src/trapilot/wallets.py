# pragma pylint: disable=W0603
""" Wallet """

import logging
from copy import deepcopy
from datetime import datetime, timedelta
from typing import Dict, NamedTuple, Optional

from trapilot.constants import Config
from trapilot.enums import RunMode, TradingMode
from trapilot.exceptions import DependencyException
from trapilot.exchange import Exchange
from trapilot.util.datetime_helpers import dt_now

logger = logging.getLogger(__name__)


# wallet data structure
class Wallet(NamedTuple):
    currency: str
    free: float = 0
    used: float = 0
    total: float = 0


class PositionWallet(NamedTuple):
    symbol: str
    position: float = 0
    leverage: float = 0
    collateral: float = 0
    side: str = 'long'


class Wallets:

    def __init__(self, config: Config, exchange: Exchange, log: bool = True) -> None:
        self._config = config
        self._log = log
        self._exchange = exchange
        self._wallets: Dict[str, Wallet] = {}
        self._positions: Dict[str, PositionWallet] = {}
        self.start_cap = config['dry_run_wallet']
        self._last_wallet_refresh: Optional[datetime] = None
        self.update()

    def get_free(self, currency: str) -> float:
        balance = self._wallets.get(currency)
        if balance and balance.free:
            return balance.free
        else:
            return 0

    def get_used(self, currency: str) -> float:
        balance = self._wallets.get(currency)
        if balance and balance.used:
            return balance.used
        else:
            return 0

    def get_total(self, currency: str) -> float:
        balance = self._wallets.get(currency)
        if balance and balance.total:
            return balance.total
        else:
            return 0

    def update(self, require_update: bool = True) -> None:
        """
        Updates wallets from the configured version.
        By default, updates from the exchange.
        Update-skipping should only be used for user-invoked /balance calls, since
        for trading operations, the latest balance is needed.
        :param require_update: Allow skipping an update if balances were recently refreshed
        """
        now = dt_now()
        if (
            require_update
            or self._last_wallet_refresh is None
            or (self._last_wallet_refresh + timedelta(seconds=3600) < now)
        ):
            # if (not self._config['dry_run'] or self._config.get('runmode') == RunMode.LIVE):
            #     self._update_live()
            # else:
            #     self._update_dry()
            # if self._log:
            #     logger.info('Wallets synced.')
            self._last_wallet_refresh = now
