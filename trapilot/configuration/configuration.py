"""
This module contains the configuration class
"""
import logging
import warnings
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from trapilot.constants import Config, TRADING_MODES, DEFAULT_DB_PROD_URL, DEFAULT_DB_DRYRUN_URL
from trapilot.enums import TradingMode
from trapilot.enums import RunMode

logger = logging.getLogger(__name__)


class Configuration:
    """
    Class to read and init the bot configuration
    Reuse this class for the bot, backtesting, hyperopt and every script that required configuration
    """

    def __init__(self, args: Dict[str, Any], runmode: Optional[RunMode] = None) -> None:
        self.args = args
        self.config: Optional[Config] = None
        self.runmode = runmode

    def get_config(self) -> Config:
        """
        Return the config. Use this method to get the bot config
        :return: Dict: Bot config
        """
        if self.config is None:
            self.config = self.load_config()

        return self.config

    def load_config(self) -> Dict[str, Any]:
        """
        Extract information for sys.argv and load the bot configuration
        :return: Configuration dictionary
        """
        # Load all configs
        config: Config = {}
        # config["dry_run"] = True
        # config["exchange"] = {}
        # config["db_url"] = "sqlite:////trapilot/user_data/tradesv3.sqlite"

        # config["user_data_dir"] = "data2"
        # config["strategy"] = "SampleStrategy"
        from pathlib import Path
        config = {
            "user_data_dir": Path("/user_data"),
            "max_open_trades": 3,
            "stake_currency": "BTC",
            "stake_amount": 0.05,
            "tradable_balance_ratio": 0.99,
            "fiat_display_currency": "USD",
            "amount_reserve_percent": 0.05,
            "available_capital": 1000,
            "amend_last_stake_amount": False,
            "last_stake_amount_min_ratio": 0.5,
            "dry_run": True,
            "dry_run_wallet": 1000,
            "cancel_open_orders_on_exit": False,
            "timeframe": "5m",
            "trailing_stop": False,
            "trailing_stop_positive": 0.005,
            "trailing_stop_positive_offset": 0.0051,
            "trailing_only_offset_is_reached": False,
            "use_exit_signal": True,
            "exit_profit_only": False,
            "exit_profit_offset": 0.0,
            "ignore_roi_if_entry_signal": False,
            "ignore_buying_expired_candle_after": 300,
            "trading_mode": TradingMode.SPOT,
            "margin_mode": "",
            "minimal_roi": {
                "40":  0.0,
                "30":  0.01,
                "20":  0.02,
                "0":  0.04
            },
            "stoploss": -0.10,
            "unfilledtimeout": {
                "entry": 10,
                "exit": 10,
                "exit_timeout_count": 0,
                "unit": "minutes"
            },
            "entry_pricing": {
                "price_side": "same",
                "use_order_book": True,
                "order_book_top": 1,
                "price_last_balance": 0.0,
                "check_depth_of_market": {
                    "enabled": False,
                    "bids_to_ask_delta": 1
                }
            },
            "exit_pricing":{
                "price_side": "same",
                "use_order_book": True,
                "order_book_top": 1,
                "price_last_balance": 0.0
            },
            "order_types": {
                "entry": "limit",
                "exit": "limit",
                "emergency_exit": "market",
                "force_exit": "market",
                "force_entry": "market",
                "stoploss": "market",
                "stoploss_on_exchange": False,
                "stoploss_price_type": "last",
                "stoploss_on_exchange_interval": 60,
                "stoploss_on_exchange_limit_ratio": 0.99
            },
            "order_time_in_force": {
                "entry": "GTC",
                "exit": "GTC"
            },
            "pairlists": [
                {"method": "StaticPairList"},
                {"method": "FullTradesFilter"},
                {
                    "method": "VolumePairList",
                    "number_assets": 20,
                    "sort_key": "quoteVolume",
                    "refresh_period": 1800
                },
                {"method": "AgeFilter", "min_days_listed": 10},
                {"method": "PrecisionFilter"},
                {"method": "PriceFilter", "low_price_ratio": 0.01, "min_price": 0.00000010},
                {"method": "SpreadFilter", "max_spread_ratio": 0.005},
                {
                    "method": "RangeStabilityFilter",
                    "lookback_days": 10,
                    "min_rate_of_change": 0.01,
                    "refresh_period": 1440
                }
            ],
            "exchange": {
                "name": "binance",
                "key": "your_exchange_key",
                "secret": "your_exchange_secret",
                "password": "",
                "log_responses": False,
                "unknown_fee_rate": 1,
                "ccxt_config": {},
                "ccxt_async_config": {},
                "pair_whitelist": [
                    "ALGO/BTC",
                    "ATOM/BTC",
                    "BAT/BTC",
                    "BCH/BTC",
                    "BRD/BTC",
                    "EOS/BTC",
                    "ETH/BTC",
                    "IOTA/BTC",
                    "LINK/BTC",
                    "LTC/BTC",
                    "NEO/BTC",
                    "NXS/BTC",
                    "XMR/BTC",
                    "XRP/BTC",
                    "XTZ/BTC"
                ],
                "pair_blacklist": [
                    "DOGE/BTC"
                ],
                "outdated_offset": 5,
                "markets_refresh_interval": 60
            },
            "edge": {
                "enabled": False,
                "process_throttle_secs": 3600,
                "calculate_since_number_of_days": 7,
                "allowed_risk": 0.01,
                "stoploss_range_min": -0.01,
                "stoploss_range_max": -0.1,
                "stoploss_range_step": -0.01,
                "minimum_winrate": 0.60,
                "minimum_expectancy": 0.20,
                "min_trade_number": 10,
                "max_trade_duration_minute": 1440,
                "remove_pumps": False
            },
            "telegram": {
                "enabled": False,
                "token": "your_telegram_token",
                "chat_id": "your_telegram_chat_id",
                "notification_settings": {
                    "status": "on",
                    "warning": "on",
                    "startup": "on",
                    "entry": "on",
                    "entry_fill": "on",
                    "exit": {
                        "roi": "off",
                        "emergency_exit": "off",
                        "force_exit": "off",
                        "exit_signal": "off",
                        "trailing_stop_loss": "off",
                        "stop_loss": "off",
                        "stoploss_on_exchange": "off",
                        "custom_exit": "off"
                    },
                    "exit_fill": "on",
                    "entry_cancel": "on",
                    "exit_cancel": "on",
                    "protection_trigger": "off",
                    "protection_trigger_global": "on",
                    "show_candle": "off"
                },
                "reload": True,
                "balance_dust_level": 0.01
            },
            "api_server": {
                "enabled": False,
                "listen_ip_address": "127.0.0.1",
                "listen_port": 8080,
                "verbosity": "error",
                "enable_openapi": False,
                "jwt_secret_key": "somethingrandom",
                "CORS_origins": [],
                "username": "freqtrader",
                "password": "SuperSecurePassword",
                "ws_token": "secret_ws_t0ken."
            },
            "external_message_consumer": {
                "enabled": False,
                "producers": [
                {
                    "name": "default",
                    "host": "127.0.0.2",
                    "port": 8080,
                    "ws_token": "secret_ws_t0ken."
                }
                ],
                "wait_timeout": 300,
                "ping_timeout": 10,
                "sleep_time": 10,
                "remove_entry_exit_signals": False,
                "message_size_limit": 8
            },
            "bot_name": "trapilot",
            "db_url": "sqlite:///tradesv3.sqlite",
            "initial_state": "running",
            "force_entry_enable": False,
            "internals": {
                "process_throttle_secs": 5,
                "heartbeat_interval": 60
            },
            "disable_dataframe_checks": False,
            "strategy": "Supertrend",
            "strategy_path": "user_data/strategies/",
            "recursive_strategy_search": False,
            "add_config_files": [],
            "reduce_df_footprint": False,
            "dataformat_ohlcv": "feather",
            "dataformat_trades": "feather"
        }
        return config

    def _process_trading_options(self, config: Config) -> None:
        if config['runmode'] not in TRADING_MODES:
            return

        if config.get('dry_run', False):
            logger.info('Dry run is enabled')
            if config.get('db_url') in [None, DEFAULT_DB_PROD_URL]:
                # Default to in-memory db for dry_run if not specified
                config['db_url'] = DEFAULT_DB_DRYRUN_URL
        else:
            if not config.get('db_url'):
                config['db_url'] = DEFAULT_DB_PROD_URL