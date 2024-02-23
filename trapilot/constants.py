from typing import Any, Dict, List, Literal, Tuple

from trapilot.enums import CandleType, RPCMessageType

DATETIME_PRINT_FORMAT = '%Y-%m-%d %H:%M:%S'

# List of pairs with their timeframes
PairWithTimeframe = Tuple[str, str, CandleType]
ListPairsWithTimeframes = List[PairWithTimeframe]