from enum import Enum
from typing import Optional, Union, List

class TralityData:
    def __init__(self):
        # Symbol information
        self.symbol: Optional[str] = None
        self.base: Optional[str] = None
        self.quoted: Optional[str] = None
        self.keys: Optional[List[str]] = None

        # Time information
        self.times: Optional[List[int]] = None
        self.first_time: Optional[int] = None
        self.last_time: Optional[int] = None

        # Price information
        self.first: Optional[float] = None
        self.last: Optional[float] = None
        self.open: Optional[float] = None
        self.open_last: Optional[float] = None
        self.high: Optional[float] = None
        self.high_last: Optional[float] = None
        self.low: Optional[float] = None
        self.low_last: Optional[float] = None
        self.close: Optional[float] = None
        self.close_last: Optional[float] = None
        self.price: Optional[float] = None
        self.price_last: Optional[float] = None
        self.volume: Optional[float] = None
        self.volume_last: Optional[float] = None
        self.oc: Optional[Union[float, str]] = None
        self.hl: Optional[Union[float, str]] = None
        self.hlc: Optional[Union[float, str]] = None
        self.ohlc: Optional[Union[float, str]] = None

    def select(self, key: str) -> Optional[Union[str, int, float, List[str], List[int], List[float]]]:
        if hasattr(self, key):
            return getattr(self, key)
        else:
            raise KeyError(f"{key} is not a valid key in TralityData")

    def select_last(self, key: str) -> Optional[Union[float, int]]:
        return getattr(self, f"{key}_last", None)

    def to_numpy(self) -> Optional[list]:
        pass

    def to_pandas(self) -> Optional[object]:
        pass

    def serialize(self) -> Optional[dict]:
        pass

    def is_valid(self) -> bool:
        pass

    def is_root(self) -> bool:
        pass


class OrderStatus(Enum):
    Created = 1
    Pending = 2
    PartiallyFilled = 3
    Filled = 4
    Canceled = 5
    Rejected = 6
    Expired = 7
    Error = 8
    BarrierTouched = 9
    StopTriggered = 10
    ForeignFilled = 11
    Unknown = 999

class OrderSide(Enum):
    Buy = 0
    Sell = 1

class TralityOrder:
    def __init__(self):
        self.id: Optional[str] = None
        self.link_id: Optional[str] = None
        self.type: Optional[str] = None
        self.symbol: Optional[str] = None
        self.quoted: Optional[str] = None
        self.base: Optional[str] = None
        self.side: Optional[OrderSide] = None
        self.quantity: Optional[Union[float, int]] = None
        self.status: Optional[OrderStatus] = None
        self.limit_price: Optional[Union[float, int]] = None
        self.stop_price: Optional[Union[float, int]] = None
        self.created_time: Optional[int] = None
        self.error: Optional[str] = None
        self.fees_asset: Optional[str] = None
        self.fills: Optional[List[dict]] = None
        self.executed_quantity: Optional[Union[float, int]] = None
        self.executed_price: Optional[Union[float, int]] = None
        self.executed_time: Optional[int] = None

    def is_pending(self) -> bool:
        return self.status == OrderStatus.Pending

    def is_placed(self) -> bool:
        return self.status == OrderStatus.Created or self.status == OrderStatus.Pending

    def is_filled(self) -> bool:
        return self.status == OrderStatus.Filled

    def is_canceled(self) -> bool:
        return self.status == OrderStatus.Canceled

    def is_rejected(self) -> bool:
        return self.status == OrderStatus.Rejected

    def is_error(self) -> bool:
        return self.status == OrderStatus.Error

    def refresh(self):
        # Implement the refresh logic here
        pass


class Balance:
    def __init__(self):
        self.asset: str = ""
        self.free: float = 0.0
        self.locked: float = 0.0


class TralityPosition:
    def __init__(self):
        self.id: str = ""
        self.symbol: str = ""
        self.status: PositionStatus = PositionStatus.Open
        self.entry_time: int = 0
        self.exit_time: int = 0
        self.last_trade_time: int = 0
        self.last_time_stamp: int = 0
        self.entry_price: float = 0.0
        self.average_price: float = 0.0
        self.exit_price: float = 0.0
        self.realized_pnl: float = 0.0
        self.unrealized_pnl: float = 0.0
        self.exposure: float = 0.0
        self.position_value: float = 0.0
        self.order_ids: list[str] = []
        self.offset_trades: list[OffsetTrade] = []
        self.number_of_trades: int = 0
        self.number_of_offsetting_trades: int = 0
        self.number_of_winning_trades: int = 0
        self.number_of_losing_trades: int = 0
        self.average_profit_per_winning_trade: float = 0.0
        self.average_loss_per_losing_trade: float = 0.0
        self.worst_trade_return: float = 0.0
        self.best_trade_return: float = 0.0
        self.worst_trade_pnl: float = 0.0
        self.best_trade_pnl: float = 0.0

class PositionStatus(Enum):
    Open = 1
    Dust = 2
    Closed = 3

class OffsetTrade:
    def __init__(self):
        self.timestamp: int = 0
        self.id: str = ""
        self.offset_order_id: str = ""
        self.trade_price: float = 0.0
        self.average_price: float = 0.0
        self.realized_pnl: float = 0.0
        self.trade_quantity: float = 0.0
        self.trade_value: float = 0.0
        self.relative_trade_size: float = 0.0



class TralityPortfolio:
    def __init__(self):
        self.quoted: str = ""
        self.balances: list[Balance] = []
        self.fee_balances: list[Balance] = []
        self.cum_fee_quoted: float = 0.0
        self.portfolio_value: float = 0.0
        self.locked_amount: float = 0.0
        self.realized_pnl: float = 0.0
        self.unrealized_pnl: float = 0.0
        self.excess_liquidity_quoted: float = 0.0
        self.open_positions: list[str] = []
        self.closed_positions: list[str] = []
        self.open_order_ids: list[str] = []
        self.last_buy_order_time: int = 0
        self.last_sell_order_time: int = 0
        self.number_of_trades: int = 0
        self.number_of_offsetting_trades: int = 0
        self.number_of_winning_trades: int = 0
        self.average_profit_per_winning_trade: float = 0.0
        self.average_loss_per_losing_trade: float = 0.0
        self.worst_trade_pnl: float = 0.0
        self.best_trade_pnl: float = 0.0
        self.worst_trade_return: float = 0.0
        self.best_trade_return: float = 0.0

class LoanStatus(Enum):
    Pending = 1
    Failed = 2
    Confirmed = 3

class RepaymentStatus(Enum):
    Pending = 1
    Failed = 2
    Confirmed = 3

class Loan:
    def __init__(self, id, asset, principal, time, status):
        self.id = id
        self.asset = asset
        self.principal = principal
        self.time = time
        self.status = status

class Repayment:
    def __init__(self, id, asset, principal, time, status):
        self.id = id
        self.asset = asset
        self.principal = principal
        self.time = time
        self.status = status


class Limit:
    def __init__(
        self,
        qty_min: Optional[str] = None,
        qty_max: Optional[str] = None,
        qty_step: Optional[str] = None,
        price_min: Optional[str] = None,
        price_max: Optional[str] = None,
        price_step: Optional[str] = None,
        cost_min: Optional[str] = None,
        cost_max: Optional[str] = None,
        cost_step: Optional[str] = None,
    ):
        self.qty_min = qty_min
        self.qty_max = qty_max
        self.qty_step = qty_step
        self.price_min = price_min
        self.price_max = price_max
        self.price_step = price_step
        self.cost_min = cost_min
        self.cost_max = cost_max
        self.cost_step = cost_step