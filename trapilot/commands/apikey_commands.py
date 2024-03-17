import logging
from typing import Any, Dict

from questionary import Choice, confirm, select, text

from trapilot.exchange.common import SUPPORTED_EXCHANGES
from trapilot.exchange.exchange_utils import available_exchange_tlds
from trapilot.persistence.api_key import ApiKey

logger = logging.getLogger(__name__)


def validate_non_empty(text: str):
    if not text.strip():
        return "Please enter a value"
    return True


def start_create_api_key(args: Dict[str, Any]) -> None:
    exchange = select(
        "What exchange would you like to add a key for?", SUPPORTED_EXCHANGES
    ).unsafe_ask()

    data = {}
    data["exchange"] = exchange

    tlds = available_exchange_tlds(exchange)
    if len(tlds) > 0:
        tld = select(
            "What TLD are you using?",
            [Choice(f"{tld}") for tld in tlds],
        ).unsafe_ask()
        data["tld"] = tld

    data["name"] = text("Give this key a name:", instruction="(Optional)").unsafe_ask()
    data["api_key"] = (
        text(f"api_key:", validate=validate_non_empty).unsafe_ask().strip()
    )
    data["api_secret"] = (
        text(f"api_secret:", validate=validate_non_empty).unsafe_ask().strip()
    )
    dry_run = confirm("Is this testnet/sandbox key?", default=False).unsafe_ask()

    ApiKey.save_key(data, dry_run)
    return False


def start_list_api_key(args: Dict[str, Any]) -> None:
    pass


def start_remove_api_key(args: Dict[str, Any]) -> None:
    pass


def start_api_key(args: Dict[str, Any]) -> None:
    func = select(
        "What would you like to do?",
        [
            Choice("Add a key", start_create_api_key),
            Choice("Show all keys", start_list_api_key),
            Choice("Remove a key", start_remove_api_key),
        ],
    ).unsafe_ask()
    func(args)
