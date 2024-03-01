from typing import Any, Dict, List, Literal, Tuple

from trapilot.enums import CandleType, RPCMessageType

DEFAULT_CONFIG = 'config.json'
PROCESS_THROTTLE_SECS = 5  # sec
HYPEROPT_EPOCH = 100  # epochs
RETRY_TIMEOUT = 30  # sec
DEFAULT_DB_PROD_URL = 'sqlite:///tradesv3.sqlite'
DEFAULT_DB_DRYRUN_URL = 'sqlite:///tradesv3.dryrun.sqlite'
UNLIMITED_STAKE_AMOUNT = 'unlimited'
DATETIME_PRINT_FORMAT = '%Y-%m-%d %H:%M:%S'
EXPORT_OPTIONS = ['none', 'trades', 'signals']
BACKTEST_BREAKDOWNS = ['day', 'week', 'month']
BACKTEST_CACHE_AGE = ['none', 'day', 'week', 'month']
BACKTEST_CACHE_DEFAULT = 'day'
HYPEROPT_LOSS_BUILTIN = ['ShortTradeDurHyperOptLoss', 'OnlyProfitHyperOptLoss',
                         'SharpeHyperOptLoss', 'SharpeHyperOptLossDaily',
                         'SortinoHyperOptLoss', 'SortinoHyperOptLossDaily',
                         'CalmarHyperOptLoss',
                         'MaxDrawDownHyperOptLoss', 'MaxDrawDownRelativeHyperOptLoss',
                         'ProfitDrawDownHyperOptLoss']

TRADING_MODES = ['spot', 'margin', 'futures']


REQUIRED_ORDERTIF = ['entry', 'exit']
REQUIRED_ORDERTYPES = ['entry', 'exit', 'stoploss', 'stoploss_on_exchange']


USERPATH_HYPEROPTS = 'hyperopts'
USERPATH_STRATEGIES = 'strategies'
USERPATH_NOTEBOOKS = 'notebooks'
USERPATH_FREQAIMODELS = 'freqaimodels'


DECIMAL_PER_COIN_FALLBACK = 3  # Should be low to avoid listing all possible FIAT's
DECIMALS_PER_COIN = {
  'BTC': 8,
  'ETH': 5,
}

# List of pairs with their timeframes
PairWithTimeframe = Tuple[str, str, CandleType]
ListPairsWithTimeframes = List[PairWithTimeframe]

# Type for trades list
TradeList = List[List]

LongShort = Literal['long', 'short']
EntryExit = Literal['entry', 'exit']
BuySell = Literal['buy', 'sell']
MakerTaker = Literal['maker', 'taker']
BidAsk = Literal['bid', 'ask']
OBLiteral = Literal['asks', 'bids']

Config = Dict[str, Any]
# Exchange part of the configuration.
ExchangeConfig = Dict[str, Any]
IntOrInf = float


EntryExecuteMode = Literal['initial', 'pos_adjust', 'replace']