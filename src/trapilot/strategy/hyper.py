"""
IHyperStrategy interface, hyperoptable Parameter class.
This module defines a base class for auto-hyperoptable strategies.
"""
import logging
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple, Type, Union

from trapilot.constants import Config
from trapilot.strategy.parameters import BaseParameter


logger = logging.getLogger(__name__)


class HyperStrategyMixin:
    """
    A helper base class which allows HyperOptAuto class to reuse implementations of buy/sell
     strategy logic.
    """

    def __init__(self, config: Config, *args, **kwargs):
        """
        Initialize hyperoptable strategy mixin.
        """
        self.config = config
        self.ft_buy_params: List[BaseParameter] = []
        self.ft_sell_params: List[BaseParameter] = []
        self.ft_protection_params: List[BaseParameter] = []

        params = self.load_params_from_file()
        params = params.get('params', {})
        self._ft_params_from_file = params
        # Init/loading of parameters is done as part of ft_bot_start().

    def load_params_from_file(self) -> Dict:
        return {}
