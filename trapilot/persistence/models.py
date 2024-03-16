"""
This module contains the class to persist trades into SQLite
"""

import logging
import threading
from contextvars import ContextVar
from typing import Any, Dict, Final, Optional

from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import NoSuchModuleError
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import StaticPool

from trapilot.persistence.base import ModelBase
from trapilot.persistence.key_value_store import _KeyValueStoreModel
from trapilot.persistence.pairlock import PairLock
from trapilot.persistence.settings import (SettingBacktest, SettingKey,
                                           SettingNotify)
from trapilot.persistence.trade_model import Order, Trade

logger = logging.getLogger(__name__)


REQUEST_ID_CTX_KEY: Final[str] = "request_id"
_request_id_ctx_var: ContextVar[Optional[str]] = ContextVar(
    REQUEST_ID_CTX_KEY, default=None
)


def get_request_or_thread_id() -> Optional[str]:
    """
    Helper method to get either async context (for fastapi requests), or thread id
    """
    id = _request_id_ctx_var.get()
    if id is None:
        # when not in request context - use thread id
        id = str(threading.current_thread().ident)

    return id


_SQL_DOCS_URL = "http://docs.sqlalchemy.org/en/latest/core/engines.html#database-urls"


def init_db(db_url: str) -> None:
    """
    Initializes this module with the given config,
    registers all known command handlers
    and starts polling for message updates
    :param db_url: Database to use
    :return: None
    """
    kwargs: Dict[str, Any] = {}

    if db_url == "sqlite:///":
        raise Exception(
            f"Bad db-url {db_url}. For in-memory database, please use `sqlite://`."
        )
    if db_url == "sqlite://":
        kwargs.update(
            {
                "poolclass": StaticPool,
            }
        )
    # Take care of thread ownership
    if db_url.startswith("sqlite://"):
        kwargs.update(
            {
                "connect_args": {"check_same_thread": False},
            }
        )

    try:
        engine = create_engine(db_url, future=True, **kwargs)
    except NoSuchModuleError:
        raise Exception(
            f"Given value for db_url: '{db_url}' "
            f"is no valid database URL! (See {_SQL_DOCS_URL})"
        )

    # https://docs.sqlalchemy.org/en/13/orm/contextual.html#thread-local-scope
    # Scoped sessions proxy requests to the appropriate thread-local session.
    # Since we also use fastAPI, we need to make it aware of the request id, too
    Trade.session = scoped_session(
        sessionmaker(bind=engine, autoflush=False), scopefunc=get_request_or_thread_id
    )
    Order.session = Trade.session
    PairLock.session = Trade.session
    SettingBacktest.session = Trade.session
    SettingKey.session = Trade.session
    SettingNotify.session = Trade.session
    _KeyValueStoreModel.session = Trade.session

    ModelBase.metadata.create_all(engine)
