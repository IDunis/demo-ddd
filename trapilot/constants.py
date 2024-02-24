from typing import Any, Dict, List, Literal, Tuple

from trapilot.enums import CandleType, RPCMessageType

DATETIME_PRINT_FORMAT = '%Y-%m-%d %H:%M:%S'

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