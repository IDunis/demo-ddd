"""
This module contains the class to persist trades into SQLite
"""

import logging
from dataclasses import dataclass
from typing import Any, ClassVar, Optional

from sqlalchemy import Boolean, Float, Integer, ScalarResult, Select, String, select
from sqlalchemy.orm import Mapped, mapped_column

from trapilot.persistence.base import ModelBase, SessionType

logger = logging.getLogger(__name__)


class ApiKey(ModelBase):
    __tablename__ = "api_key"
    __allow_unmapped__ = True
    session: ClassVar[SessionType]

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    exhange: Mapped[str] = mapped_column(String(50))
    name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    tld: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    dry_run: Mapped[bool] = mapped_column(Boolean, default=True)
    api_key: Mapped[str] = mapped_column(String(255), nullable=True)
    api_secret: Mapped[str] = mapped_column(String(255), nullable=True)

    @staticmethod
    def get_keys_query(filter=None) -> Select:
        if filter is not None:
            if not isinstance(filter, list):
                filter = [filter]
            query = select(ApiKey).filter(*filter)
        else:
            query = select(ApiKey)
        return query

    @staticmethod
    def get_keys(filter=None) -> ScalarResult["ApiKey"]:
        query = ApiKey.get_keys_query(filter)
        return ApiKey.session.scalars(query)

    @staticmethod
    def save_key(data: dict, dry_run: bool = True) -> ScalarResult["ApiKey"]:
        apikey = ApiKey.get_keys(
            [
                ApiKey.dry_run.is_(dry_run),
                ApiKey.exhange.is_(data.get("exchange")),
                ApiKey.tld.is_(data.get("tld")),
            ]
        ).first()

        if not apikey:
            apikey = ApiKey(
                dry_run=dry_run,
                exhange=data.get("exchange"),
                tld=data.get("tld"),
            )

        apikey.name = data.get("name")
        apikey.api_key = data.get("api_key")
        apikey.api_secret = data.get("api_secret")

        ApiKey.session.add(apikey)
        ApiKey.session.commit()
