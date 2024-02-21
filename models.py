from enum import Enum
from decimal import Decimal
from typing import Optional, Union, List

import numpy as np
import pandas as pd

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
        data = [getattr(self, attr) for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")]
        return np.array(data)

    def to_pandas(self) -> Optional[object]:
        data = {attr: [getattr(self, attr)] for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")}
        return pd.DataFrame(data)

    def serialize(self) -> Optional[dict]:
        data = {attr: getattr(self, attr) for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")}
        return data

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


def order_market_amount(symbol: str, amount: float) -> TralityOrder:
    return TralityOrder()
def order_market_value(symbol: str, amount: float) -> TralityOrder:
    return TralityOrder()
def order_market_target(symbol: str, target_percent: float) -> TralityOrder:
    return TralityOrder()

def order_limit_amount(symbol: str, amount: float, limit_price: float) -> TralityOrder:
    return TralityOrder()
def order_limit_value(symbol: str, value: float, limit_price: float) -> TralityOrder:
    return TralityOrder()
def order_limit_target(symbol: str, target_percent: float, limit_price: float) -> TralityOrder:
    return TralityOrder()

def order_iftouched_market_amount(symbol: str, amount: float, stop_price: float) -> TralityOrder:
    return TralityOrder()
def order_iftouched_market_value(symbol: str, value: float, stop_price: float) -> TralityOrder:
    return TralityOrder()

def order_iftouched_limit_amount(symbol: str, amount: float, stop_price: float, limit_price: float) -> TralityOrder:
    return TralityOrder()
def order_iftouched_limit_value(symbol: str, value: float, stop_price: float, limit_price: float) -> TralityOrder:
    return TralityOrder()

def order_take_profit(symbol: str, amount: float, stop_percent: float, subtract_fees: bool = False) -> TralityOrder:
    return TralityOrder()
def order_stop_loss(symbol: str, amount: float, stop_percent: float, subtract_fees: bool = False) -> TralityOrder:
    return TralityOrder()

def order_trailing_iftouched_amount(symbol: str, amount: float, trailing_percent: float, stop_price: float) -> TralityOrder:
    return TralityOrder()
def order_trailing_iftouched_value(symbol: str, value: float, trailing_percent: float, stop_price: float) -> TralityOrder:
    return TralityOrder()

def order_amount(symbol: str, amount: float, stop_price: float, limit_price: float) -> TralityOrder:
    return TralityOrder()
def order_value(symbol: str, value: float, stop_price: float, limit_price: float) -> TralityOrder:
    return TralityOrder()
def order_target(symbol: str, target_percent: float, limit_price: float) -> TralityOrder:
    return TralityOrder()

def query_order(id: str) -> Optional[TralityOrder]:
    return TralityOrder()
def query_open_orders() -> list[TralityOrder]:
    return []

def cancel_order(order_id: str) -> TralityOrder:
    return TralityOrder()
def subtract_order_fees(amount: float) -> float:
    return 0.1

def query_balance(asset: str) -> Balance:
    return Balance()
def query_balance_free(asset: str) -> Decimal:
    return Decimal(3.14)
def query_balance_locked(asset: str) -> Decimal:
    return Decimal(3.14)
def query_balances() -> list[Balance]:
    return []

def has_open_position(symbol: str, include_dust: bool =False) -> bool:
    return True
def query_open_position_by_symbol(symbol: str, include_dust: bool = False) -> Optional[TralityPosition]:
    return None
def query_position_by_id(position_id: str) -> Optional[TralityPosition]:
    return None
def query_open_positions(include_dust: bool = False) -> list[TralityPosition]:
    return []
# def query_position_pnl(symbol: str) -> Pnl if exists else None
def query_position_offset_trades(symbol: str) -> list[OffsetTrade]:
    return []
# def query_position_profitability(symbol: str) -> ProfitabilityMetrics if exists else None
def query_losing_positions(include_dust: bool = False) -> list[TralityPosition]:
    return []
def query_winning_positions(include_dust: bool = False) -> list[TralityPosition]:
    return []
def query_position_weight(symbol: str) -> Decimal:
    return Decimal(2)
def query_position_weights() -> dict[Decimal]:
    decimal_number1 = Decimal('123.456')
    decimal_number2 = Decimal(3.14)
    decimal_number3 = Decimal('42.0')
    decimal_dict = {
        'value1': decimal_number1,
        'value2': decimal_number2,
        'value3': decimal_number3
    }
    return decimal_dict

def close_position(symbol: str) -> TralityOrder:
    return TralityOrder()
def close_all_positions() -> list[TralityOrder]:
    return []
def adjust_position(symbol: str, weight: float) -> TralityOrder:
    return TralityOrder()

def query_portfolio() -> TralityPortfolio:
    return TralityPortfolio()
def query_portfolio_pnl() -> dict: #A PNL namedtuple with attributes: realized and unrealized
    portfolio = query_portfolio()
    return {
        "realized": portfolio.realized_pnl,
        "unrealized": portfolio.unrealized_pnl,
    }
def query_portfolio_value() -> Decimal:
    portfolio = query_portfolio()
    return Decimal(portfolio.portfolio_value)
def query_portfolio_profitablity() -> dict: # PortfolioProfitabilityMetric
    return {}
# Pnl = namedtuple("Pnl",["realized","unrealized"])
# ProfitabilityMetrics = namedtuple("ProfitablityMetrics",["numberOfTrades","numberOfOffsettingTrades",
#                                                         "numberOfWinningTrades","averageProfitPerWinningTrade",
#                                                         "averageLossPerLosingTrade","worstTradeReturn","bestTradeReturn",
#                                                         "worstTradePnl","bestTradePnl"])

def margin_borrow(asset: str, amount: float) -> Loan:
    return Loan()