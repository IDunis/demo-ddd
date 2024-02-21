"""
This module contains class to define a RPC communications
"""
import logging
from abc import abstractmethod
from typing import Any, Dict, Optional, Union

from nexttrade import __version__
from nexttrade.constants import Config
from nexttrade.enums import State
from nexttrade.rpc.fiat_convert import CryptoToFiatConverter
from nexttrade.rpc.rpc_types import RPCSendMsg


logger = logging.getLogger(__name__)


class RPCException(Exception):
    """
    Should be raised with a rpc-formatted message in an _rpc_* method
    if the required state is wrong, i.e.:

    raise RPCException('*Status:* `no active trade`')
    """

    def __init__(self, message: str) -> None:
        super().__init__(self)
        self.message = message

    def __str__(self):
        return self.message

    def __json__(self):
        return {
            'msg': self.message
        }


class RPCHandler:

    def __init__(self, rpc: 'RPC', config: Config) -> None:
        """
        Initializes RPCHandlers
        :param rpc: instance of RPC Helper class
        :param config: Configuration object
        :return: None
        """
        self._rpc = rpc
        self._config: Config = config

    @property
    def name(self) -> str:
        """ Returns the lowercase name of the implementation """
        return self.__class__.__name__.lower()

    @abstractmethod
    def cleanup(self) -> None:
        """ Cleanup pending module resources """

    @abstractmethod
    def send_msg(self, msg: RPCSendMsg) -> None:
        """ Sends a message to all registered rpc modules """


class RPC:
    """
    RPC class can be used to have extra feature, like bot data, and access to DB data
    """
    # Bind _fiat_converter if needed
    _fiat_converter: Optional[CryptoToFiatConverter] = None

    def __init__(self, trader) -> None:
        """
        Initializes all enabled rpc modules
        :param trader: Instance of a trader bot
        :return: None
        """
        self._trader = trader
        self._config: Config = trader.config
        if self._config.get('fiat_display_currency'):
            self._fiat_converter = CryptoToFiatConverter()

    @staticmethod
    def _rpc_show_config(config, botstate: Union[State, str],
                         strategy_version: Optional[str] = None) -> Dict[str, Any]:
        """
        Return a dict of config options.
        Explicitly does NOT return the full config to avoid leakage of sensitive
        information via rpc.
        """
        val = {
            'version': __version__,
            'strategy_version': strategy_version,
            'dry_run': config['dry_run'],
            'trading_mode': config.get('trading_mode', 'spot'),
            'short_allowed': config.get('trading_mode', 'spot') != 'spot',
            'stake_currency': config['stake_currency'],
            'stake_amount': str(config['stake_amount']),
            'available_capital': config.get('available_capital'),
            'max_open_trades': (config.get('max_open_trades', 0)
                                if config.get('max_open_trades', 0) != float('inf') else -1),
            'minimal_roi': config['minimal_roi'].copy() if 'minimal_roi' in config else {},
            'stoploss': config.get('stoploss'),
            'stoploss_on_exchange': config.get('order_types',
                                               {}).get('stoploss_on_exchange', False),
            'trailing_stop': config.get('trailing_stop'),
            'trailing_stop_positive': config.get('trailing_stop_positive'),
            'trailing_stop_positive_offset': config.get('trailing_stop_positive_offset'),
            'trailing_only_offset_is_reached': config.get('trailing_only_offset_is_reached'),
            'unfilledtimeout': config.get('unfilledtimeout'),
            'use_custom_stoploss': config.get('use_custom_stoploss'),
            'order_types': config.get('order_types'),
            'bot_name': config.get('bot_name', 'trader'),
            'timeframe': config.get('timeframe'),
            'exchange': config['exchange']['name'],
            'strategy': config['strategy'],
            'force_entry_enable': config.get('force_entry_enable', False),
            'exit_pricing': config.get('exit_pricing', {}),
            'entry_pricing': config.get('entry_pricing', {}),
            'state': str(botstate),
            'runmode': config['runmode'].value,
            'position_adjustment_enable': config.get('position_adjustment_enable', False),
            'max_entry_position_adjustment': (
                config.get('max_entry_position_adjustment', -1)
                if config.get('max_entry_position_adjustment') != float('inf')
                else -1)
        }
        return val

    def _rpc_start(self) -> Dict[str, str]:
        """ Handler for start """
        if self._trader.state == State.RUNNING:
            return {'status': 'already running'}

        self._trader.state = State.RUNNING
        return {'status': 'starting trader ...'}

    def _rpc_stop(self) -> Dict[str, str]:
        """ Handler for stop """
        if self._trader.state == State.RUNNING:
            self._trader.state = State.STOPPED
            return {'status': 'stopping trader ...'}

        return {'status': 'already stopped'}

    def _rpc_reload_config(self) -> Dict[str, str]:
        """ Handler for reload_config. """
        self._trader.state = State.RELOAD_CONFIG
        return {'status': 'Reloading config ...'}
