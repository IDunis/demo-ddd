from typing import Optional

from trapilot.exchange import Exchange
from trapilot.util.migrations.binance_mig import migrate_binance_futures_names  # noqa F401
from trapilot.util.migrations.binance_mig import migrate_binance_futures_data
from trapilot.util.migrations.funding_rate_mig import migrate_funding_fee_timeframe


def migrate_data(config, exchange: Optional[Exchange] = None):
    migrate_binance_futures_data(config)

    migrate_funding_fee_timeframe(config, exchange)
