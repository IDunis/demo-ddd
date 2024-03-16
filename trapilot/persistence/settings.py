"""
This module contains the class to persist trades into SQLite
"""
import logging
from dataclasses import dataclass
from typing import ClassVar

from sqlalchemy import (Integer, String, Boolean, Float)
from sqlalchemy.orm import Mapped, mapped_column

from trapilot.persistence.base import ModelBase, SessionType


logger = logging.getLogger(__name__)


@dataclass
class ProfitStruct:
    profit_abs: float
    profit_ratio: float
    total_profit: float
    total_profit_ratio: float


class SettingKey(ModelBase):
    __tablename__ = "setting_key"
    __allow_unmapped__ = True
    session: ClassVar[SessionType]

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    exhange: Mapped[str] = mapped_column(String(50))
    dry_run: Mapped[bool] = mapped_column(Boolean, default=True)
    api_key: Mapped[str] = mapped_column(String(255), nullable=True)
    api_secret: Mapped[str] = mapped_column(String(255), nullable=True)


class SettingNotify(ModelBase):
    __tablename__ = "setting_notify"
    __allow_unmapped__ = True
    session: ClassVar[SessionType]

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), nullable=True)
    port: Mapped[str] = mapped_column(Integer, nullable=True, default=465)
    smtp_server: Mapped[str] = mapped_column(String(255), nullable=True, default="smtp.gmail.com")
    sender_email: Mapped[str] = mapped_column(String(255), nullable=True)
    sender_password: Mapped[str] = mapped_column(String(255), nullable=True)
    receiver_email: Mapped[str] = mapped_column(String(255), nullable=True)
    receiver_email: Mapped[str] = mapped_column(String(255), nullable=True)


class SettingBacktest(ModelBase):
    __tablename__ = "setting_backtest"
    __allow_unmapped__ = True
    session: ClassVar[SessionType]

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    price_data: Mapped[str] = mapped_column(String(255), nullable=True)
    use_price: Mapped[str] = mapped_column(String(50), nullable=True, default="close")
    smooth_price: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)
    gui_output: Mapped[bool] = mapped_column(Boolean, nullable=True, default=True)
    show_tickers_with_zero_delta: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)
    save_initial_account_value: Mapped[bool] = mapped_column(Boolean, nullable=True, default=True)
    show_progress_during_backtest: Mapped[bool] = mapped_column(Boolean, nullable=True, default=True)
    cache_location: Mapped[str] = mapped_column(String(255), nullable=True, default="./user_data/price_caches")
    continuous_caching: Mapped[bool] = mapped_column(Boolean, nullable=True, default=True)
    resample_account_value_for_metrics: Mapped[str] = mapped_column(String(4), nullable=True, default="1d")
    quote_account_value_in: Mapped[str] = mapped_column(String(20), nullable=True, default="USDT")
    ignore_user_exception: Mapped[bool] = mapped_column(Boolean, nullable=True, default=True)
    risk_free_return_rate: Mapped[float] = mapped_column(Float(), nullable=True, default=0.0)
    benchmark_symbol: Mapped[str] = mapped_column(String(255), nullable=True)
