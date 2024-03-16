import logging
from typing import Optional

from trapilot.LIB.constants import Config
from trapilot.LIB.data.history.idatahandler import get_datahandler
from trapilot.LIB.enums import TradingMode
from trapilot.LIB.exchange import Exchange


logger = logging.getLogger(__name__)


def migrate_funding_fee_timeframe(config: Config, exchange: Optional[Exchange]):
    if (
        config.get('trading_mode', TradingMode.SPOT) != TradingMode.FUTURES
    ):
        # only act on futures
        return

    if not exchange:
        from trapilot.LIB.resolvers import ExchangeResolver
        exchange = ExchangeResolver.load_exchange(config, validate=False)

    ff_timeframe = exchange.get_option('funding_fee_timeframe')

    dhc = get_datahandler(config['datadir'], config['dataformat_ohlcv'])
    dhc.fix_funding_fee_timeframe(ff_timeframe)
