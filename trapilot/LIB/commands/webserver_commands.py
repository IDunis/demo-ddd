from typing import Any, Dict

from trapilot.LIB.enums import RunMode


def start_webserver(args: Dict[str, Any]) -> None:
    """
    Main entry point for webserver mode
    """
    from trapilot.LIB.configuration import setup_utils_configuration
    from trapilot.LIB.rpc.api_server import ApiServer

    # Initialize configuration

    config = setup_utils_configuration(args, RunMode.WEBSERVER)
    ApiServer(config, standalone=True)
