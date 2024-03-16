from typing import Optional

from trapilot.LIB.exchange import Exchange
from trapilot.LIB.util.migrations.binance_mig import (  # noqa F401
    migrate_binance_futures_data,
    migrate_binance_futures_names,
)
from trapilot.LIB.util.migrations.funding_rate_mig import migrate_funding_fee_timeframe


def migrate_data(config, exchange: Optional[Exchange] = None):
    migrate_binance_futures_data(config)

    migrate_funding_fee_timeframe(config, exchange)
