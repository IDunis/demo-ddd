import datetime
import enum
from typing import TypeVar

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    MetaData,
    SmallInteger,
    String,
)
from sqlalchemy.orm import Mapped, declarative_base, relationship
from sqlalchemy.sql import func

__all__ = ("Base", "UsersTable", "ProductsTable", "OrdersTable")

meta = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_`%(constraint_name)s`",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)


class SIGN_UP_ENUM(str, enum.Enum):
    APP = "APP"
    ADMIN = "ADMIN"
    PUBLIC = "PUBLIC"
    SYNC = "SYNC"
    WEB = "WEB"


Base = declarative_base(metadata=meta)

ConcreteTable = TypeVar("ConcreteTable", bound=Base)


class UsersTable(Base):
    __tablename__ = "users"

    id: int = Column(Integer, primary_key=True)
    username: str = Column(String(100), nullable=False, unique=True)
    email: str = Column(String(100), nullable=True, unique=True)
    phone: str = Column(String(20), nullable=True)
    role: str = Column(String(20), nullable=True)
    first_name: str = Column(String(100), nullable=True)
    last_name: str = Column(String(100), nullable=True)
    surr_name: str = Column(String(100), nullable=True)
    salt: str = Column(String(20), nullable=True)
    password: str = Column(String(100), nullable=True)
    password_expired: DateTime = Column(DateTime, nullable=True)
    password_attempt: int = Column(SmallInteger, nullable=True, default=0)
    sign_up_date: datetime = Column(
        DateTime, nullable=True, default=datetime.datetime.utcnow
    )
    sign_up_from: SIGN_UP_ENUM = Column(
        Enum(SIGN_UP_ENUM), nullable=True, default=SIGN_UP_ENUM.ADMIN
    )
    is_activated: bool = Column(Boolean, nullable=True, default=False)
    is_blocked: bool = Column(Boolean, nullable=True, default=False)
    activated_date: datetime = Column(Date, nullable=True)
    blocked_date: datetime = Column(Date, nullable=True)
    created_at: datetime = Column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: datetime = Column(DateTime(timezone=True), onupdate=func.now())


class ProductsTable(Base):
    __tablename__ = "products"

    id: int = Column(Integer, primary_key=True)
    name: str = Column(String(255), nullable=False)
    price: int = Column(Integer, nullable=False)


class OrdersTable(Base):
    __tablename__ = "orders"

    id: int = Column(Integer, primary_key=True)
    amount: int = Column(Integer, nullable=False, default=1)

    product_id: int = Column(ForeignKey(ProductsTable.id), nullable=False)
    user_id: int = Column(ForeignKey(UsersTable.id), nullable=False)

    user: "Mapped[UsersTable]" = relationship("UsersTable", uselist=False)
    product: "Mapped[ProductsTable]" = relationship(
        "ProductsTable", uselist=False
    )
