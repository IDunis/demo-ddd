"""
This module contains class to manage RPC communications (Telegram, API, ...)
"""
import logging
from collections import deque
from typing import List

from trapilot.rpc import RPC, RPCHandler


logger = logging.getLogger(__name__)


class RPCManager:
    """
    Class to manage RPC objects (Telegram, API, ...)
    """

    def __init__(self, tradebot) -> None:
        """ Initializes all enabled rpc modules """
        self.registered_modules: List[RPCHandler] = []
        self._rpc = RPC(tradebot)
        config = tradebot.config
        # Enable telegram
        if config.get('telegram', {}).get('enabled', False):
            logger.info('Enabling rpc.telegram ...')
            from freqtrade.rpc.telegram import Telegram
            self.registered_modules.append(Telegram(self._rpc, config))

