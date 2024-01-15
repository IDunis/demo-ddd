# pragma pylint: disable=unused-argument, unused-variable, protected-access, invalid-name

"""
This module manage Telegram communication
"""
import asyncio
import logging
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from functools import wraps
from threading import Thread
from typing import Any, Callable, Coroutine, Dict, List, Optional, Union

from telegram import (CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton,
                      ReplyKeyboardMarkup, Update)
from telegram.constants import MessageLimit, ParseMode
from telegram.error import BadRequest, NetworkError, TelegramError
from telegram.ext import Application, CallbackContext, CallbackQueryHandler, CommandHandler
# from telegram.helpers import escape_markdown

from src.__init__ import __version__
from src.constants import Config
from src.enums import RPCMessageType
# from src.exceptions import OperationalException
from src.persistence import Trade
from src.rpc import RPC, RPCException, RPCHandler
from src.rpc.rpc_types import RPCSendMsg


MAX_MESSAGE_LENGTH = MessageLimit.MAX_TEXT_LENGTH


logger = logging.getLogger(__name__)

logger.debug('Included module rpc.telegram ...')


def safe_async_db(func: Callable[..., Any]):
    """
    Decorator to safely handle sessions when switching async context
    :param func: function to decorate
    :return: decorated function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        """ Decorator logic """
        try:
            return func(*args, **kwargs)
        finally:
            Trade.session.remove()

    return wrapper


@dataclass
class TimeunitMappings:
    header: str
    message: str
    message2: str
    callback: str
    default: int
    dateformat: str


def authorized_only(command_handler: Callable[..., Coroutine[Any, Any, None]]):
    """
    Decorator to check if the message comes from the correct chat_id
    :param command_handler: Telegram CommandHandler
    :return: decorated function
    """

    @wraps(command_handler)
    async def wrapper(self, *args, **kwargs):
        """ Decorator logic """
        update = kwargs.get('update') or args[0]

        # Reject unauthorized messages
        if update.callback_query:
            cchat_id = int(update.callback_query.message.chat.id)
        else:
            cchat_id = int(update.message.chat_id)

        chat_id = int(self._config['telegram']['chat_id'])
        if cchat_id != chat_id:
            logger.info(f'Rejected unauthorized message from: {update.message.chat_id}')
            return wrapper
        # Rollback session to avoid getting data stored in a transaction.
        Trade.rollback()
        logger.debug(
            'Executing handler: %s for chat_id: %s',
            command_handler.__name__,
            chat_id
        )
        try:
            return await command_handler(self, *args, **kwargs)
        except RPCException as e:
            await self._send_msg(str(e))
        except BaseException:
            logger.exception('Exception occurred within Telegram module')
        finally:
            Trade.session.remove()

    return wrapper


class Telegram(RPCHandler):
    """  This class handles all telegram communication """

    def __init__(self, rpc: RPC, config: Config) -> None:
        """
        Init the Telegram call, and init the super class RPCHandler
        :param rpc: instance of RPC Helper class
        :param config: Configuration object
        :return: None
        """
        super().__init__(rpc, config)

        self._app: Application
        self._loop: asyncio.AbstractEventLoop
        self._init_keyboard()
        self._start_thread()

    def _start_thread(self):
        """
        Creates and starts the polling thread
        """
        self._thread = Thread(target=self._init, name='FTTelegram')
        self._thread.start()

    def _init_keyboard(self) -> None:
        """
        Validates the keyboard configuration from telegram config
        section.
        """
        self._keyboard: List[List[Union[str, KeyboardButton]]] = [
            ['/daily', '/profit', '/balance'],
            ['/status', '/status table', '/performance'],
            ['/count', '/start', '/stop', '/help']
        ]

    def _init_telegram_app(self):
        return Application.builder().token(self._config['telegram']['token']).build()

    def _init(self) -> None:
        """
        Initializes this module with the given config,
        registers all known command handlers
        and starts polling for message updates
        Runs in a separate thread.
        """
        try:
            self._loop = asyncio.get_running_loop()
        except RuntimeError:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
        self._app = self._init_telegram_app()

        # Register command handler and start telegram message polling
        handles = [
            CommandHandler('status', self._status),
            CommandHandler('start', self._start),
            CommandHandler('stop', self._stop),
        ]
        callbacks = [
        ]
        for handle in handles:
            self._app.add_handler(handle)

        for callback in callbacks:
            self._app.add_handler(callback)

        logger.info(
            'rpc.telegram is listening for following commands: %s',
            [[x for x in sorted(h.commands)] for h in handles]
        )
        self._loop.run_until_complete(self._startup_telegram())

    async def _startup_telegram(self) -> None:
        await self._app.initialize()
        await self._app.start()
        if self._app.updater:
            await self._app.updater.start_polling(
                bootstrap_retries=-1,
                timeout=20,
                # read_latency=60,  # Assumed transmission latency
                drop_pending_updates=True,
                # stop_signals=[],  # Necessary as we don't run on the main thread
            )
            while True:
                await asyncio.sleep(10)
                if not self._app.updater.running:
                    break

    async def _cleanup_telegram(self) -> None:
        if self._app.updater:
            await self._app.updater.stop()
        await self._app.stop()
        await self._app.shutdown()

    def cleanup(self) -> None:
        """
        Stops all running telegram threads.
        :return: None
        """
        # This can take up to `timeout` from the call to `start_polling`.
        asyncio.run_coroutine_threadsafe(self._cleanup_telegram(), self._loop)
        self._thread.join()

    def compose_message(self, msg: RPCSendMsg) -> Optional[str]:
        if msg['type'] == RPCMessageType.ENTRY or msg['type'] == RPCMessageType.ENTRY_FILL:
            # message = self._format_entry_msg(msg)
            message = ("111111111111")

        elif msg['type'] == RPCMessageType.EXIT or msg['type'] == RPCMessageType.EXIT_FILL:
            # message = self._format_exit_msg(msg)
            message = ("22222222222")

        elif (
            msg['type'] == RPCMessageType.ENTRY_CANCEL
            or msg['type'] == RPCMessageType.EXIT_CANCEL
        ):
            message_side = 'enter' if msg['type'] == RPCMessageType.ENTRY_CANCEL else 'exit'
            # message = (f"\N{WARNING SIGN} *{self._exchange_from_msg(msg)}:* "
            #            f"Cancelling {'partial ' if msg.get('sub_trade') else ''}"
            #            f"{message_side} Order for {msg['pair']} "
            #            f"(#{msg['trade_id']}). Reason: {msg['reason']}.")
            message = ("333333333333")

        elif msg['type'] == RPCMessageType.PROTECTION_TRIGGER:
            message = (
                f"*Protection* triggered due to {msg['reason']}. "
                f"`{msg['pair']}` will be locked until `{msg['lock_end_time']}`."
            )

        elif msg['type'] == RPCMessageType.PROTECTION_TRIGGER_GLOBAL:
            message = (
                f"*Protection* triggered due to {msg['reason']}. "
                f"*All pairs* will be locked until `{msg['lock_end_time']}`."
            )

        elif msg['type'] == RPCMessageType.STATUS:
            message = f"*Status:* `{msg['status']}`"

        elif msg['type'] == RPCMessageType.WARNING:
            message = f"\N{WARNING SIGN} *Warning:* `{msg['status']}`"
        elif msg['type'] == RPCMessageType.EXCEPTION:
            # Errors will contain exceptions, which are wrapped in tripple ticks.
            message = f"\N{WARNING SIGN} *ERROR:* \n {msg['status']}"

        elif msg['type'] == RPCMessageType.STARTUP:
            message = f"{msg['status']}"
        elif msg['type'] == RPCMessageType.STRATEGY_MSG:
            message = f"{msg['msg']}"
        else:
            logger.debug("Unknown message type: %s", msg['type'])
            return None
        return message

    def send_msg(self, msg: RPCSendMsg) -> None:
        """ Send a message to telegram channel """

        default_noti = 'on'

        msg_type = msg['type']
        noti = ''
        if msg['type'] == RPCMessageType.EXIT:
            sell_noti = self._config['telegram'] \
                .get('notification_settings', {}).get(str(msg_type), {})
            # For backward compatibility sell still can be string
            if isinstance(sell_noti, str):
                noti = sell_noti
            else:
                noti = sell_noti.get(str(msg['exit_reason']), default_noti)
        else:
            noti = self._config['telegram'] \
                .get('notification_settings', {}).get(str(msg_type), default_noti)

        if noti == 'off':
            logger.info(f"Notification '{msg_type}' not sent.")
            # Notification disabled
            return
        
        message = self.compose_message(deepcopy(msg))
        if message:
            asyncio.run_coroutine_threadsafe(
                self._send_msg(message, disable_notification=(noti == 'silent')), self._loop)

    @authorized_only
    async def _status(self, update: Update, context: CallbackContext) -> None:
        """
        Handler for /status.
        Returns the current TradeThread status
        :param bot: telegram bot
        :param update: message update
        :return: None
        """

        await self._status_msg(update, context)

    async def _status_msg(self, update: Update, context: CallbackContext) -> None:
            r = []
            lines = [
                'âaaa'
            ]
            await self.__send_status_msg(lines, r)

    async def __send_status_msg(self, lines: List[str], r: Dict[str, Any]) -> None:
        """
        Send status message.
        """
        msg = ''

        for line in lines:
            if line:
                if (len(msg) + len(line) + 1) < MAX_MESSAGE_LENGTH:
                    msg += line + '\n'
                else:
                    await self._send_msg(msg.format(**r))
                    msg = "*Trade ID:* `{trade_id}` - continued\n" + line + '\n'

        await self._send_msg(msg.format(**r))

    @authorized_only
    async def _start(self, update: Update, context: CallbackContext) -> None:
        """
        Handler for /start.
        Starts TradeThread
        :param bot: telegram bot
        :param update: message update
        :return: None
        """
        msg = self._rpc._rpc_start()
        await self._send_msg(f"Status: `{msg['status']}`")

    @authorized_only
    async def _stop(self, update: Update, context: CallbackContext) -> None:
        """
        Handler for /stop.
        Stops TradeThread
        :param bot: telegram bot
        :param update: message update
        :return: None
        """
        msg = self._rpc._rpc_stop()
        await self._send_msg(f"Status: `{msg['status']}`")


    async def _update_msg(self, query: CallbackQuery, msg: str, callback_path: str = "",
                          reload_able: bool = False, parse_mode: str = ParseMode.MARKDOWN) -> None:
        if reload_able:
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("Refresh", callback_data=callback_path)],
            ])
        else:
            reply_markup = InlineKeyboardMarkup([[]])
        msg += f"\nUpdated: {datetime.now().ctime()}"
        if not query.message:
            return
        chat_id = query.message.chat_id
        message_id = query.message.message_id

        try:
            await self._app.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=msg,
                parse_mode=parse_mode,
                reply_markup=reply_markup
            )
        except BadRequest as e:
            if 'not modified' in e.message.lower():
                pass
            else:
                logger.warning('TelegramError: %s', e.message)
        except TelegramError as telegram_err:
            logger.warning('TelegramError: %s! Giving up on that message.', telegram_err.message)

    async def _send_msg(self, msg: str, parse_mode: str = ParseMode.MARKDOWN,
                        disable_notification: bool = False,
                        keyboard: Optional[List[List[InlineKeyboardButton]]] = None,
                        callback_path: str = "",
                        reload_able: bool = False,
                        query: Optional[CallbackQuery] = None) -> None:
        """
        Send given markdown message
        :param msg: message
        :param bot: alternative bot
        :param parse_mode: telegram parse mode
        :return: None
        """
        reply_markup: Union[InlineKeyboardMarkup, ReplyKeyboardMarkup]
        if query:
            await self._update_msg(query=query, msg=msg, parse_mode=parse_mode,
                                   callback_path=callback_path, reload_able=reload_able)
            return
        if reload_able and self._config['telegram'].get('reload', True):
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("Refresh", callback_data=callback_path)]])
        else:
            if keyboard is not None:
                reply_markup = InlineKeyboardMarkup(keyboard)
            else:
                reply_markup = ReplyKeyboardMarkup(self._keyboard, resize_keyboard=True)

        try:
            try:
                await self._app.bot.send_message(
                    self._config['telegram']['chat_id'],
                    text=msg,
                    parse_mode=parse_mode,
                    reply_markup=reply_markup,
                    disable_notification=disable_notification,
                )
            except NetworkError as network_err:
                # Sometimes the telegram server resets the current connection,
                # if this is the case we send the message again.
                logger.warning(
                    'Telegram NetworkError: %s! Trying one more time.',
                    network_err.message
                )
                await self._app.bot.send_message(
                    self._config['telegram']['chat_id'],
                    text=msg,
                    parse_mode=parse_mode,
                    reply_markup=reply_markup,
                    disable_notification=disable_notification,
                )
        except TelegramError as telegram_err:
            logger.warning(
                'TelegramError: %s! Giving up on that message.',
                telegram_err.message
            )
