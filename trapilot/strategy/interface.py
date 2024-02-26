"""
IStrategy interface
This module defines the interface to apply for strategies
"""
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple, Union

from pandas import DataFrame

from trapilot.constants import Config, IntOrInf
from trapilot.enums import (MarketDirection)
from trapilot.exceptions import OperationalException
from trapilot.exchange import timeframe_to_minutes
from trapilot.strategy.hyper import HyperStrategyMixin
from trapilot.strategy.informative_decorator import (InformativeData, PopulateIndicators)
from trapilot.wallets import Wallets


logger = logging.getLogger(__name__)


class IStrategy(ABC, HyperStrategyMixin):
    """
    Interface for trapilot strategies
    Defines the mandatory structure must follow any custom strategies

    Attributes you can use:
        minimal_roi -> Dict: Minimal ROI designed for the strategy
        stoploss -> float: optimal stoploss designed for the strategy
        timeframe -> str: value of the timeframe to use with the strategy
    """
    # Strategy interface version
    # Default to version 2
    # Version 1 is the initial interface without metadata dict - deprecated and no longer supported.
    # Version 2 populate_* include metadata dict
    # Version 3 - First version with short and leverage support
    INTERFACE_VERSION: int = 3

    _ft_params_from_file: Dict
    # associated minimal roi
    minimal_roi: Dict = {}

    # associated stoploss
    stoploss: float

    # max open trades for the strategy
    max_open_trades:  IntOrInf

    # trailing stoploss
    trailing_stop: bool = False
    trailing_stop_positive: Optional[float] = None
    trailing_stop_positive_offset: float = 0.0
    trailing_only_offset_is_reached = False
    use_custom_stoploss: bool = False

    # Can this strategy go short?
    can_short: bool = False

    # associated timeframe
    timeframe: str

    # Optional order types
    order_types: Dict = {
        'entry': 'limit',
        'exit': 'limit',
        'stoploss': 'limit',
        'stoploss_on_exchange': False,
        'stoploss_on_exchange_interval': 60,
    }

    # Optional time in force
    order_time_in_force: Dict = {
        'entry': 'GTC',
        'exit': 'GTC',
    }

    # run "populate_indicators" only for new candle
    process_only_new_candles: bool = True

    use_exit_signal: bool
    exit_profit_only: bool
    exit_profit_offset: float
    ignore_roi_if_entry_signal: bool

    # Position adjustment is disabled by default
    position_adjustment_enable: bool = False
    max_entry_position_adjustment: int = -1

    # Number of seconds after which the candle will no longer result in a buy on expired candles
    ignore_buying_expired_candle_after: int = 0

    # Disable checking the dataframe (converts the error into a warning message)
    disable_dataframe_checks: bool = False

    # Count of candles the strategy requires before producing valid signals
    startup_candle_count: int = 0

    # Protections
    protections: List = []

    wallets: Optional[Wallets] = None
    # Filled from configuration
    stake_currency: str
    # container variable for strategy source code
    __source__: str = ''

    # Definition of plot_config. See plotting documentation for more details.
    plot_config: Dict = {}

    # A self set parameter that represents the market direction. filled from configuration
    market_direction: MarketDirection = MarketDirection.NONE

    def __init__(self, config: Config) -> None:
        self.config = config
        # Dict to determine if analysis is necessary
        self._last_candle_seen_per_pair: Dict[str, datetime] = {}
        super().__init__(config)

        # Gather informative pairs from @informative-decorated methods.
        self._ft_informative: List[Tuple[InformativeData, PopulateIndicators]] = []
        for attr_name in dir(self.__class__):
            cls_method = getattr(self.__class__, attr_name)
            if not callable(cls_method):
                continue
            informative_data_list = getattr(cls_method, '_ft_informative', None)
            if not isinstance(informative_data_list, list):
                # Type check is required because mocker would return a mock object that evaluates to
                # True, confusing this code.
                continue
            strategy_timeframe_minutes = timeframe_to_minutes(self.timeframe)
            for informative_data in informative_data_list:
                if timeframe_to_minutes(informative_data.timeframe) < strategy_timeframe_minutes:
                    raise OperationalException('Informative timeframe must be equal or higher than '
                                               'strategy timeframe!')
                if not informative_data.candle_type:
                    informative_data.candle_type = config['candle_type_def']
                self._ft_informative.append((informative_data, cls_method))
