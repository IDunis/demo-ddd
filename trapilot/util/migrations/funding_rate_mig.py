import logging
from typing import Optional

from trapilot.constants import Config
from trapilot.data.history.idatahandler import get_datahandler
from trapilot.enums import TradingMode
from trapilot.exchange import Exchange

logger = logging.getLogger(__name__)


def migrate_funding_fee_timeframe(config: Config, exchange: Optional[Exchange]):
    if config.get("trading_mode", TradingMode.SPOT) != TradingMode.FUTURES:
        # only act on futures
        return

    if not exchange:
        from trapilot.resolvers import ExchangeResolver

        exchange = ExchangeResolver.load_exchange(config, validate=False)

    ff_timeframe = exchange.get_option("funding_fee_timeframe")

    dhc = get_datahandler(config["datadir"], config["dataformat_ohlcv"])
    dhc.fix_funding_fee_timeframe(ff_timeframe)
