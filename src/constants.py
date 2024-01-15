# pragma pylint: disable=too-few-public-methods

"""
bot constants
"""
from typing import Any, Dict, List, Literal, Tuple

Config = Dict[str, Any]

PROCESS_THROTTLE_SECS = 5  # sec
RETRY_TIMEOUT = 30  # sec
DEFAULT_CONFIG = 'config.json'


MINIMAL_CONFIG = {
    "stake_currency": "",
    "dry_run": True,
    "exchange": {
        "name": "",
        "key": "",
        "secret": "",
        "pair_whitelist": [],
        "ccxt_async_config": {
        }
    }
}

SUPPORTED_FIAT = [
    "AUD", "BRL", "CAD", "CHF", "CLP", "CNY", "CZK", "DKK",
    "EUR", "GBP", "HKD", "HUF", "IDR", "ILS", "INR", "JPY",
    "KRW", "MXN", "MYR", "NOK", "NZD", "PHP", "PKR", "PLN",
    "RUB", "UAH", "SEK", "SGD", "THB", "TRY", "TWD", "ZAR",
    "USD", "BTC", "ETH", "XRP", "LTC", "BCH", "BNB"
]