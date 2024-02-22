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

from trapilot.enums import LoanStatus, OrderSide, OrderStatus, PositionStatus
from trapilot.persistence.base import ModelBase, SessionType
from trapilot.util import dt_now


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
    entry_time: Mapped[Optional[int]] = mapped_column(Integer(255), nullable=True)
    exit_time: Mapped[Optional[int]] = mapped_column(Integer(255), nullable=True)
    last_trade_time: Mapped[Optional[int]] = mapped_column(Integer(255), nullable=True)
    last_time_stamp: Mapped[Optional[int]] = mapped_column(Integer(255), nullable=True)
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