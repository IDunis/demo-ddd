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

CANCELED_EXCHANGE_STATES = ('cancelled', 'canceled', 'expired')

NON_OPEN_EXCHANGE_STATES = CANCELED_EXCHANGE_STATES + ('closed',)

CUSTOM_TAG_MAX_LENGTH = 255

DATETIME_PRINT_FORMAT = '%Y-%m-%d %H:%M:%S'

MATH_CLOSE_PREC = 1e-14  # Precision used for float comparisons

# Type for trades list
TradeList = List[List]

LongShort = Literal['long', 'short']
EntryExit = Literal['entry', 'exit']
BuySell = Literal['buy', 'sell']
MakerTaker = Literal['maker', 'taker']
BidAsk = Literal['bid', 'ask']
