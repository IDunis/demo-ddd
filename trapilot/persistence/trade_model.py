"""
This module contains the class to persist trades into SQLite
"""
import logging
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from math import isclose
from typing import Any, ClassVar, Dict, List, Optional, Union, Sequence, cast

from sqlalchemy import (Enum, Float, ForeignKey, Integer, JSON, ScalarResult, Select, String,
                        UniqueConstraint, desc, func, select)
from sqlalchemy.orm import Mapped, lazyload, mapped_column, relationship, validates

from trapilot.constants import BuySell, LongShort
from trapilot.exceptions import OperationalException
from trapilot.enums import LoanStatus, OrderSide, OrderStatus, PositionStatus, TradingMode
from trapilot.persistence.base import ModelBase, SessionType
from trapilot.util import dt_now, Precise


logger = logging.getLogger(__name__)


@dataclass
class ProfitStruct:
    profit_abs: float
    profit_ratio: float
    total_profit: float
    total_profit_ratio: float


class Order(ModelBase):
    __tablename__ = 'orders'
    __allow_unmapped__ = True
    session: ClassVar[SessionType]

    # Uniqueness should be ensured over pair, order_id
    # its likely that order_id is unique per Pair on some exchanges.
    # __table_args__ = (UniqueConstraint('ft_pair', 'order_id', name="_order_pair_order_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    trade_id: Mapped[int] = mapped_column(Integer, ForeignKey('trades.id'), index=True)

    _trade_live: Mapped["Trade"] = relationship("Trade", back_populates="orders", lazy="immediate")
    _trade_bt: "LocalTrade" = None  # type: ignore

    # order_side can only be 'buy', 'sell' or 'stoploss'
    # ft_order_side: Mapped[str] = mapped_column(String(25), nullable=False)
    # ft_pair: Mapped[str] = mapped_column(String(25), nullable=False)
    # ft_is_open: Mapped[bool] = mapped_column(nullable=False, default=True, index=True)
    # ft_amount: Mapped[float] = mapped_column(Float(), nullable=False)
    # ft_price: Mapped[float] = mapped_column(Float(), nullable=False)
    # ft_cancel_reason: Mapped[str] = mapped_column(String(CUSTOM_TAG_MAX_LENGTH), nullable=True)

    order_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(50), nullable=True)
    symbol: Mapped[Optional[str]] = mapped_column(String(25), nullable=True)
    quoted: Mapped[Optional[str]] = mapped_column(String(25), nullable=True)
    base: Mapped[Optional[str]] = mapped_column(String(25), nullable=True)
    side: Mapped[OrderSide] = mapped_column(String(25), nullable=True)
    quantity: Mapped[Optional[float]] = mapped_column(Float(), nullable=True)
    status: Mapped[Optional[OrderStatus]] = mapped_column(String(255), nullable=True)
    limit_price: Mapped[Optional[float]] = mapped_column(Float(), nullable=True)
    stop_price: Mapped[Optional[float]] = mapped_column(Float(), nullable=True)
    created_time: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    error: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    fee_asset: Mapped[Optional[float]] = mapped_column(Float(), nullable=True)
    is_open: Mapped[bool] = mapped_column(nullable=False, default=True, index=True)
    fills: Mapped[List[dict]] = mapped_column(JSON(), nullable=True)
    executed_quantity: Optional[Union[float, int]] = mapped_column(Float(), nullable=True)
    executed_price: Optional[Union[float, int]] = mapped_column(Float(), nullable=True)
    executed_time: Optional[int] = mapped_column(Integer(), nullable=True)

    # average: Mapped[Optional[float]] = mapped_column(Float(), nullable=True)
    # filled: Mapped[Optional[float]] = mapped_column(Float(), nullable=True)
    # remaining: Mapped[Optional[float]] = mapped_column(Float(), nullable=True)
    # cost: Mapped[Optional[float]] = mapped_column(Float(), nullable=True)
    # order_date: Mapped[datetime] = mapped_column(nullable=True, default=dt_now)
    # order_filled_date: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    # order_update_date: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    # funding_fee: Mapped[Optional[float]] = mapped_column(Float(), nullable=True)

    # ft_fee_base: Mapped[Optional[float]] = mapped_column(Float(), nullable=True)

    @property
    def order_date_utc(self) -> datetime:
        """ Order-date with UTC timezoneinfo"""
        return self.order_date.replace(tzinfo=timezone.utc)

    @staticmethod
    def get_open_orders() -> Sequence['Order']:
        """
        Retrieve open orders from the database
        :return: List of open orders
        """
        return Order.session.scalars(select(Order).filter(Order.is_open.is_(True))).all()

    @staticmethod
    def order_by_id(order_id: str) -> Optional['Order']:
        """
        Retrieve order based on order_id
        :return: Order or None
        """
        return Order.session.scalars(select(Order).filter(Order.order_id == order_id)).first()

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


class Position(ModelBase):
    """"""
    __tablename__ = 'positions'
    __allow_unmapped__ = True
    session: ClassVar[SessionType]

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symbol: Mapped[Optional[str]] = mapped_column(String(25), nullable=True)
    entry_time: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    exit_time: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    last_trade_time: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    last_time_stamp: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    entry_price: Mapped[Optional[float]] = mapped_column(Float(), nullable=True)
    average_price: Mapped[Optional[float]] = mapped_column(Float(), nullable=True)
    exit_price: Mapped[Optional[float]] = mapped_column(Float(), nullable=True)
    realized_pnl: Mapped[Optional[float]] = mapped_column(Float(), nullable=True)
    unrealized_pnl: Mapped[Optional[float]] = mapped_column(Float(), nullable=True)
    exposure: Mapped[Optional[float]] = mapped_column(Float(), nullable=True)
    position_value: Mapped[Optional[float]] = mapped_column(Float(), nullable=True)
    # order_ids: list[str] = []
    # offset_trades: list[OffsetTrade] = []
    number_of_trades: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    number_of_offsetting_trades: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    number_of_winning_trades: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    number_of_losing_trades: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    average_profit_per_winning_trade: Mapped[Optional[float]] = mapped_column(Float(), nullable=True)
    average_loss_per_losing_trade: Mapped[Optional[float]] = mapped_column(Float(), nullable=True)
    worst_trade_return: Mapped[Optional[float]] = mapped_column(Float(), nullable=True)
    best_trade_return: Mapped[Optional[float]] = mapped_column(Float(), nullable=True)
    worst_trade_pnl: Mapped[Optional[float]] = mapped_column(Float(), nullable=True)
    best_trade_pnl: Mapped[Optional[float]] = mapped_column(Float(), nullable=True)


class OffsetTrade(ModelBase):
    """"""
    __tablename__ = 'offset_trades'
    __allow_unmapped__ = True
    session: ClassVar[SessionType]

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    timestamp: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    offset_order_id: Mapped[Optional[str]] = mapped_column(String(), nullable=True)
    trade_price: Mapped[Optional[float]] = mapped_column(Integer(), nullable=True)
    average_price: Mapped[Optional[float]] = mapped_column(Integer(), nullable=True)
    realized_pnl: Mapped[Optional[float]] = mapped_column(Integer(), nullable=True)
    trade_quantity: Mapped[Optional[float]] = mapped_column(Integer(), nullable=True)
    trade_value: Mapped[Optional[float]] = mapped_column(Integer(), nullable=True)
    relative_trade_size: Mapped[Optional[float]] = mapped_column(Integer(), nullable=True)


class Loan(ModelBase):
    """"""
    __tablename__ = 'loans'
    __allow_unmapped__ = True
    session: ClassVar[SessionType]

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    asset: Mapped[Optional[str]] = mapped_column(String(), nullable=True)
    principal: Mapped[Optional[float]] = mapped_column(Float(), nullable=True)
    time: Mapped[Optional[float]] = mapped_column(Float(), nullable=True)
    status: Mapped[Optional[LoanStatus]] = mapped_column(Integer(), nullable=True, default=LoanStatus.Pending)


class Repayment(ModelBase):
    """"""
    __tablename__ = 'repayments'
    __allow_unmapped__ = True
    session: ClassVar[SessionType]

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    asset: Mapped[Optional[str]] = mapped_column(String(), nullable=True)
    principal: Mapped[Optional[float]] = mapped_column(Float(), nullable=True)
    time: Mapped[Optional[float]] = mapped_column(Float(), nullable=True)
    status: Mapped[Optional[LoanStatus]] = mapped_column(Integer(), nullable=True, default=LoanStatus.Pending)



class Balance:
    def __init__(self):
        self.asset: str = ""
        self.free: float = 0.0
        self.locked: float = 0.0
class MarginBalance(Balance):
    def __init__(self):
        super().__init__()
        self.borrowed: float = 0.0
        self.interest: float = 0.0
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


class LocalTrade:
    """
    Trade database model.
    Used in backtesting - must be aligned to Trade model!

    """
    use_db: bool = False
    # Trades container for backtesting
    trades: List['LocalTrade'] = []
    trades_open: List['LocalTrade'] = []
    # Copy of trades_open - but indexed by pair
    bt_trades_open_pp: Dict[str, List['LocalTrade']] = defaultdict(list)
    bt_open_open_trade_count: int = 0
    total_profit: float = 0
    realized_profit: float = 0

    id: int = 0

    orders: List[Order] = []

    exchange: str = ''
    pair: str = ''
    base_currency: Optional[str] = ''
    stake_currency: Optional[str] = ''
    is_open: bool = True
    fee_open: float = 0.0
    fee_open_cost: Optional[float] = None
    fee_open_currency: Optional[str] = ''
    fee_close: Optional[float] = 0.0
    fee_close_cost: Optional[float] = None
    fee_close_currency: Optional[str] = ''
    open_rate: float = 0.0
    open_rate_requested: Optional[float] = None
    # open_trade_value - calculated via _calc_open_trade_value
    open_trade_value: float = 0.0
    close_rate: Optional[float] = None
    close_rate_requested: Optional[float] = None
    close_profit: Optional[float] = None
    close_profit_abs: Optional[float] = None
    stake_amount: float = 0.0
    max_stake_amount: Optional[float] = 0.0
    amount: float = 0.0
    amount_requested: Optional[float] = None
    open_date: datetime
    close_date: Optional[datetime] = None
    # absolute value of the stop loss
    stop_loss: float = 0.0
    # percentage value of the stop loss
    stop_loss_pct: Optional[float] = 0.0
    # absolute value of the initial stop loss
    initial_stop_loss: Optional[float] = 0.0
    # percentage value of the initial stop loss
    initial_stop_loss_pct: Optional[float] = None
    is_stop_loss_trailing: bool = False
    # stoploss order id which is on exchange
    stoploss_order_id: Optional[str] = None
    # last update time of the stoploss order on exchange
    stoploss_last_update: Optional[datetime] = None
    # absolute value of the highest reached price
    max_rate: Optional[float] = None
    # Lowest price reached
    min_rate: Optional[float] = None
    exit_reason: Optional[str] = ''
    exit_order_status: Optional[str] = ''
    strategy: Optional[str] = ''
    enter_tag: Optional[str] = None
    timeframe: Optional[int] = None

    trading_mode: TradingMode = TradingMode.SPOT
    amount_precision: Optional[float] = None
    price_precision: Optional[float] = None
    precision_mode: Optional[int] = None
    contract_size: Optional[float] = None

    # Leverage trading properties
    liquidation_price: Optional[float] = None
    is_short: bool = False
    leverage: float = 1.0

    # Margin trading properties
    interest_rate: float = 0.0

    # Futures properties
    funding_fees: Optional[float] = None
    # Used to keep running funding fees - between the last filled order and now
    # Shall not be used for calculations!
    funding_fee_running: Optional[float] = None

    def __init__(self, **kwargs):
        for key in kwargs:
            setattr(self, key, kwargs[key])
        self.recalc_open_trade_value()
        self.orders = []
        if self.trading_mode == TradingMode.MARGIN and self.interest_rate is None:
            raise OperationalException(
                f"{self.trading_mode.value} trading requires param interest_rate on trades")

    def recalc_open_trade_value(self) -> None:
        """
        Recalculate open_trade_value.
        Must be called whenever open_rate, fee_open is changed.
        """
        self.open_trade_value = self._calc_open_trade_value(self.amount, self.open_rate)

    def _calc_open_trade_value(self, amount: float, open_rate: float) -> float:
        """
        Calculate the open_rate including open_fee.
        :return: Price in of the open trade incl. Fees
        """
        open_trade = Precise(amount) * Precise(open_rate)
        fees = open_trade * Precise(self.fee_open)
        if self.is_short:
            return float(open_trade - fees)
        else:
            return float(open_trade + fees)

class Trade(ModelBase, LocalTrade):
    """
    Trade database model.
    Also handles updating and querying trades

    Note: Fields must be aligned with LocalTrade class
    """
    __tablename__ = 'trades'
    session: ClassVar[SessionType]

    use_db: bool = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True)  # type: ignore

    orders: Mapped[List[Order]] = relationship(
        "Order", order_by="Order.id", cascade="all, delete-orphan", lazy="selectin",
        innerjoin=True)  # type: ignore

    exchange: Mapped[str] = mapped_column(String(25), nullable=False)  # type: ignore
    pair: Mapped[str] = mapped_column(String(25), nullable=False, index=True)  # type: ignore
    base_currency: Mapped[Optional[str]] = mapped_column(String(25), nullable=True)  # type: ignore
    stake_currency: Mapped[Optional[str]] = mapped_column(String(25), nullable=True)  # type: ignore
    is_open: Mapped[bool] = mapped_column(nullable=False, default=True, index=True)  # type: ignore
    fee_open: Mapped[float] = mapped_column(Float(), nullable=False, default=0.0)  # type: ignore
    fee_open_cost: Mapped[Optional[float]] = mapped_column(Float(), nullable=True)  # type: ignore
    fee_open_currency: Mapped[Optional[str]] = mapped_column(
        String(25), nullable=True)  # type: ignore
    fee_close: Mapped[Optional[float]] = mapped_column(
        Float(), nullable=False, default=0.0)  # type: ignore
    fee_close_cost: Mapped[Optional[float]] = mapped_column(Float(), nullable=True)  # type: ignore
    fee_close_currency: Mapped[Optional[str]] = mapped_column(
        String(25), nullable=True)  # type: ignore
    open_rate: Mapped[float] = mapped_column(Float())  # type: ignore
    open_rate_requested: Mapped[Optional[float]] = mapped_column(
        Float(), nullable=True)  # type: ignore
    # open_trade_value - calculated via _calc_open_trade_value
    open_trade_value: Mapped[float] = mapped_column(Float(), nullable=True)  # type: ignore
    close_rate: Mapped[Optional[float]] = mapped_column(Float())  # type: ignore
    close_rate_requested: Mapped[Optional[float]] = mapped_column(Float())  # type: ignore
    realized_profit: Mapped[float] = mapped_column(
        Float(), default=0.0, nullable=True)  # type: ignore
    close_profit: Mapped[Optional[float]] = mapped_column(Float())  # type: ignore
    close_profit_abs: Mapped[Optional[float]] = mapped_column(Float())  # type: ignore
    stake_amount: Mapped[float] = mapped_column(Float(), nullable=False)  # type: ignore
    max_stake_amount: Mapped[Optional[float]] = mapped_column(Float())  # type: ignore
    amount: Mapped[float] = mapped_column(Float())  # type: ignore
    amount_requested: Mapped[Optional[float]] = mapped_column(Float())  # type: ignore
    open_date: Mapped[datetime] = mapped_column(
        nullable=False, default=datetime.utcnow)  # type: ignore
    close_date: Mapped[Optional[datetime]] = mapped_column()  # type: ignore
    # absolute value of the stop loss
    stop_loss: Mapped[float] = mapped_column(Float(), nullable=True, default=0.0)  # type: ignore
    # percentage value of the stop loss
    stop_loss_pct: Mapped[Optional[float]] = mapped_column(Float(), nullable=True)  # type: ignore
    # absolute value of the initial stop loss
    initial_stop_loss: Mapped[Optional[float]] = mapped_column(
        Float(), nullable=True, default=0.0)  # type: ignore
    # percentage value of the initial stop loss
    initial_stop_loss_pct: Mapped[Optional[float]] = mapped_column(
        Float(), nullable=True)  # type: ignore
    is_stop_loss_trailing: Mapped[bool] = mapped_column(
        nullable=False, default=False)  # type: ignore
    # stoploss order id which is on exchange
    stoploss_order_id: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, index=True)  # type: ignore
    # last update time of the stoploss order on exchange
    stoploss_last_update: Mapped[Optional[datetime]] = mapped_column(nullable=True)  # type: ignore
    # absolute value of the highest reached price
    max_rate: Mapped[Optional[float]] = mapped_column(
        Float(), nullable=True, default=0.0)  # type: ignore
    # Lowest price reached
    min_rate: Mapped[Optional[float]] = mapped_column(Float(), nullable=True)  # type: ignore
    exit_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # type: ignore
    exit_order_status: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # type: ignore
    strategy: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # type: ignore
    enter_tag: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # type: ignore
    timeframe: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # type: ignore

    trading_mode: Mapped[TradingMode] = mapped_column(
        Enum(TradingMode), nullable=True)  # type: ignore
    amount_precision: Mapped[Optional[float]] = mapped_column(
        Float(), nullable=True)  # type: ignore
    price_precision: Mapped[Optional[float]] = mapped_column(Float(), nullable=True)  # type: ignore
    precision_mode: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # type: ignore
    contract_size: Mapped[Optional[float]] = mapped_column(Float(), nullable=True)  # type: ignore

    # Leverage trading properties
    leverage: Mapped[float] = mapped_column(Float(), nullable=True, default=1.0)  # type: ignore
    is_short: Mapped[bool] = mapped_column(nullable=False, default=False)  # type: ignore
    liquidation_price: Mapped[Optional[float]] = mapped_column(
        Float(), nullable=True)  # type: ignore

    # Margin Trading Properties
    interest_rate: Mapped[float] = mapped_column(
        Float(), nullable=False, default=0.0)  # type: ignore

    # Futures properties
    funding_fees: Mapped[Optional[float]] = mapped_column(
        Float(), nullable=True, default=None)  # type: ignore
    funding_fee_running: Mapped[Optional[float]] = mapped_column(
        Float(), nullable=True, default=None)  # type: ignore

    def __init__(self, **kwargs):
        from_json = kwargs.pop('__FROM_JSON', None)
        super().__init__(**kwargs)
        if not from_json:
            # Skip recalculation when loading from json
            self.realized_profit = 0
            self.recalc_open_trade_value()

    def recalc_open_trade_value(self) -> None:
        """
        Recalculate open_trade_value.
        Must be called whenever open_rate, fee_open is changed.
        """
        self.open_trade_value = self._calc_open_trade_value(self.amount, self.open_rate)

    def _calc_open_trade_value(self, amount: float, open_rate: float) -> float:
        """
        Calculate the open_rate including open_fee.
        :return: Price in of the open trade incl. Fees
        """
        open_trade = Precise(amount) * Precise(open_rate)
        fees = open_trade * Precise(self.fee_open)
        if self.is_short:
            return float(open_trade - fees)
        else:
            return float(open_trade + fees)