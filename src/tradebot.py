"""
TradeBot is the main module of this bot. It contains the class TradeBot()
"""
import logging
from datetime import datetime, timezone

from schedule import Scheduler

from src.constants import Config
from src.enums import State, RPCMessageType
from src.rpc import RPCManager
from src.mixins import LoggingMixin


logger = logging.getLogger(__name__)


class TradeBot(LoggingMixin):
    """
    TradeBot is the main class of the bot.
    This is from here the bot start its logic.
    """

    def __init__(self, config: Config) -> None:
        
        # Init bot state
        self.state = State.STOPPED

        # Init objects
        self.config = config

        # RPC runs in separate threads, can start handling external commands just after
        # initialization, even before TradeBot has a chance to start its throttling,
        # so anything in the TradeBot instance should be ready (initialized), including
        # the initial state of the bot.
        # Keep this at the end of this initialization method.
        self.rpc: RPCManager = RPCManager(self)

        self._schedule = Scheduler()

    def notify_status(self, msg: str, msg_type=RPCMessageType.STATUS) -> None:
        """
        Public method for users of this class (worker, etc.) to send notifications
        via RPC about changes in the bot status.
        """
        self.rpc.send_msg({
            'type': msg_type,
            'status': msg
        })

    def cleanup(self) -> None:
        """
        Cleanup pending resources on an already stopped bot
        :return: None
        """
        logger.info('Cleaning up modules ...')

    def startup(self) -> None:
        """
        Called on startup and after reloading the bot - triggers notifications and
        performs startup tasks
        """
        self.rpc.startup_messages(self.config, [], [])

    def check_for_open_trades(self):
        """
        Notify the user when the bot is stopped (not reloaded)
        and there are still open trades active.
        """
        msg = {
            'type': RPCMessageType.WARNING,
            'status':
                f"len(open_trades) open trades active.\n\n"
                f"Handle these trades manually on self.exchange.name, "
                f"or '/start' the bot again and use '/stopentry' "
                f"to handle open trades gracefully. \n"
                f"{'Note: Trades are simulated (dry run).' if self.config['dry_run'] else ''}",
        }
        self.rpc.send_msg(msg)
    
    def process(self) -> None:
        """
        Queries the persistence layer for open trades and handles them,
        otherwise a new trade is created.
        :return: True if one or more trades has been created or closed, False otherwise
        """

        self.last_process = datetime.now(timezone.utc)
    
    def process_stopped(self) -> None:
        """
        Close all orders that were left open
        """
        # if self.config['cancel_open_orders_on_exit']:
        #     self.cancel_all_open_orders()