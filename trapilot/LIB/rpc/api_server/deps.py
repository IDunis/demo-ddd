from typing import Any, AsyncIterator, Dict, Optional
from uuid import uuid4

from fastapi import Depends, HTTPException

from trapilot.LIB.constants import Config
from trapilot.LIB.enums import RunMode
from trapilot.LIB.persistence import Trade
from trapilot.LIB.persistence.models import _request_id_ctx_var
from trapilot.LIB.rpc.api_server.webserver_bgwork import ApiBG
from trapilot.LIB.rpc.rpc import RPC, RPCException

from .webserver import ApiServer


def get_rpc_optional() -> Optional[RPC]:
    if ApiServer._has_rpc:
        return ApiServer._rpc
    return None


async def get_rpc() -> Optional[AsyncIterator[RPC]]:

    _rpc = get_rpc_optional()
    if _rpc:
        request_id = str(uuid4())
        ctx_token = _request_id_ctx_var.set(request_id)
        Trade.rollback()
        try:
            yield _rpc
        finally:
            Trade.session.remove()
            _request_id_ctx_var.reset(ctx_token)

    else:
        raise RPCException("Bot is not in the correct state")


def get_config() -> Dict[str, Any]:
    return ApiServer._config


def get_api_config() -> Dict[str, Any]:
    return ApiServer._config["api_server"]


def _generate_exchange_key(config: Config) -> str:
    """
    Exchange key - used for caching the exchange object.
    """
    return f"{config['exchange']['name']}_{config.get('trading_mode', 'spot')}"


def get_exchange(config=Depends(get_config)):
    exchange_key = _generate_exchange_key(config)
    if not (exchange := ApiBG.exchanges.get(exchange_key)):
        from trapilot.LIB.resolvers import ExchangeResolver

        exchange = ExchangeResolver.load_exchange(
            config, validate=False, load_leverage_tiers=False
        )
        ApiBG.exchanges[exchange_key] = exchange
    return exchange


def get_message_stream():
    return ApiServer._message_stream


def is_webserver_mode(config=Depends(get_config)):
    if config["runmode"] != RunMode.WEBSERVER:
        raise HTTPException(status_code=503, detail="Bot is not in the correct state.")
    return None
