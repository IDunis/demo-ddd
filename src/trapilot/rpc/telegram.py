# pragma pylint: disable=unused-argument, unused-variable, protected-access, invalid-name

"""
This module manage Telegram communication
"""
import asyncio
import json
import logging
import re
from copy import deepcopy
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from functools import partial, wraps
from html import escape
from itertools import chain
from math import isnan
from threading import Thread
from typing import Any, Callable, Coroutine, Dict, List, Literal, Optional, Union

from tabulate import tabulate
from telegram import (CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton,
                      ReplyKeyboardMarkup, Update)
from telegram.constants import MessageLimit, ParseMode
from telegram.error import BadRequest, NetworkError, TelegramError
from telegram.ext import Application, CallbackContext, CallbackQueryHandler, CommandHandler
from telegram.helpers import escape_markdown

from trapilot.__init__ import __version__
from trapilot.constants import Config
from trapilot.enums import TradingMode
from trapilot.exceptions import OperationalException
from trapilot.persistence import Trade
from trapilot.rpc import RPC, RPCException, RPCHandler
from trapilot.util import dt_humanize, fmt_coin


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
        self._thread = Thread(target=self._init, name='TelegramRPC')
        self._thread.start()

    def _init_keyboard(self) -> None:
        """
        Validates the keyboard configuration from telegram config
        section.
        """
        self._keyboard: List[List[Union[str, KeyboardButton]]] = [
            ['/status'],
            ['/start', '/stop', '/help']
        ]
        # do not allow commands with mandatory arguments and critical cmds
        # TODO: DRY! - its not good to list all valid cmds here. But otherwise
        #       this needs refactoring of the whole telegram module (same
        #       problem in _help()).
        valid_keys: List[str] = [
            r'/start$', r'/stop$', r'/status$', r'/status table$',
            r'/trades$', r'/performance$', r'/buys', r'/entries',
            r'/sells', r'/exits', r'/mix_tags',
            r'/daily$', r'/daily \d+$', r'/profit$', r'/profit \d+',
            r'/stats$', r'/count$', r'/locks$', r'/balance$',
            r'/stopbuy$', r'/stopentry$', r'/reload_config$', r'/show_config$',
            r'/logs$', r'/whitelist$', r'/whitelist(\ssorted|\sbaseonly)+$',
            r'/blacklist$', r'/bl_delete$',
            r'/weekly$', r'/weekly \d+$', r'/monthly$', r'/monthly \d+$',
            r'/forcebuy$', r'/forcelong$', r'/forceshort$',
            r'/forcesell$', r'/forceexit$',
            r'/edge$', r'/health$', r'/help$', r'/version$', r'/marketdir (long|short|even|none)$',
            r'/marketdir$'
        ]
        # Create keys for generation
        valid_keys_print = [k.replace('$', '') for k in valid_keys]

        # custom keyboard specified in config.json
        cust_keyboard = self._config['telegram'].get('keyboard', [])
        if cust_keyboard:
            combined = "(" + ")|(".join(valid_keys) + ")"
            # check for valid shortcuts
            invalid_keys = [b for b in chain.from_iterable(cust_keyboard)
                            if not re.match(combined, b)]
            if len(invalid_keys):
                err_msg = ('config.telegram.keyboard: Invalid commands for '
                           f'custom Telegram keyboard: {invalid_keys}'
                           f'\nvalid commands are: {valid_keys_print}')
                raise OperationalException(err_msg)
            else:
                self._keyboard = cust_keyboard
                logger.info('using custom keyboard from '
                            f'config.json: {self._keyboard}')

    def _init_telegram_app(self) -> Application:
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
            CommandHandler('help', self._help),
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

    @authorized_only
    async def _help(self, update: Update, context: CallbackContext) -> None:
        """
        Handler for /help.
        Show commands of the bot
        :param bot: telegram bot
        :param update: message update
        :return: None
        """

        message = (
            "_Bot Control_\n"
            "------------\n"
            "*/start:* `Starts the trader`\n"
            "*/stop:* Stops the trader\n"

            "\n_Statistics_\n"
            "------------\n"
            "*/status <trade_id>|[table]:* `Lists all open trades`\n"
            "         *<trade_id> :* `Lists one or more specific trades.`\n"
            "                        `Separate multiple <trade_id> with a blank space.`\n"
            "         *table :* `will display trades in a table`\n"
            "                `pending buy orders are marked with an asterisk (*)`\n"
            "                `pending sell orders are marked with a double asterisk (**)`\n"
            "*/help:* `This help message`"
            )

        await self._send_msg(message, parse_mode=ParseMode.MARKDOWN)

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

    @authorized_only
    async def _reload_config(self, update: Update, context: CallbackContext) -> None:
        """
        Handler for /reload_config.
        Triggers a config file reload
        :param bot: telegram bot
        :param update: message update
        :return: None
        """
        msg = self._rpc._rpc_reload_config()
        await self._send_msg(f"Status: `{msg['status']}`")

    @authorized_only
    async def _status(self, update: Update, context: CallbackContext) -> None:
        """
        Handler for /status.
        Returns the current TradeThread status
        :param bot: telegram bot
        :param update: message update
        :return: None
        """
        if context.args and 'table' in context.args:
            await self._status_table(update, context)
            return
        else:
            await self._status_msg(update, context)

    async def _status_msg(self, update: Update, context: CallbackContext) -> None:
        """
        handler for `/status` and `/status <id>`.

        """
        # Check if there's at least one numerical ID provided.
        # If so, try to get only these trades.
        trade_ids = []
        if context.args and len(context.args) > 0:
            trade_ids = [int(i) for i in context.args if i.isnumeric()]

        results = self._rpc._rpc_trade_status(trade_ids=trade_ids)
        position_adjust = self._config.get('position_adjustment_enable', False)
        max_entries = self._config.get('max_entry_position_adjustment', -1)
        for r in results:
            r['open_date_hum'] = dt_humanize(r['open_date'])
            r['num_entries'] = len([o for o in r['orders'] if o['ft_is_entry']])
            r['num_exits'] = len([o for o in r['orders'] if not o['ft_is_entry']
                                 and not o['ft_order_side'] == 'stoploss'])
            r['exit_reason'] = r.get('exit_reason', "")
            r['stake_amount_r'] = fmt_coin(r['stake_amount'], r['quote_currency'])
            r['max_stake_amount_r'] = fmt_coin(
                r['max_stake_amount'] or r['stake_amount'], r['quote_currency'])
            r['profit_abs_r'] = fmt_coin(r['profit_abs'], r['quote_currency'])
            r['realized_profit_r'] = fmt_coin(r['realized_profit'], r['quote_currency'])
            r['total_profit_abs_r'] = fmt_coin(
                r['total_profit_abs'], r['quote_currency'])
            lines = [
                "*Trade ID:* `{trade_id}`" +
                (" `(since {open_date_hum})`" if r['is_open'] else ""),
                "*Current Pair:* {pair}",
                f"*Direction:* {'`Short`' if r.get('is_short') else '`Long`'}"
                + " ` ({leverage}x)`" if r.get('leverage') else "",
                "*Amount:* `{amount} ({stake_amount_r})`",
                "*Total invested:* `{max_stake_amount_r}`" if position_adjust else "",
                "*Enter Tag:* `{enter_tag}`" if r['enter_tag'] else "",
                "*Exit Reason:* `{exit_reason}`" if r['exit_reason'] else "",
            ]

            if position_adjust:
                max_buy_str = (f"/{max_entries + 1}" if (max_entries > 0) else "")
                lines.extend([
                    "*Number of Entries:* `{num_entries}" + max_buy_str + "`",
                    "*Number of Exits:* `{num_exits}`"
                ])

            lines.extend([
                "*Open Rate:* `{open_rate:.8g}`",
                "*Close Rate:* `{close_rate:.8g}`" if r['close_rate'] else "",
                "*Open Date:* `{open_date}`",
                "*Close Date:* `{close_date}`" if r['close_date'] else "",
                " \n*Current Rate:* `{current_rate:.8g}`" if r['is_open'] else "",
                ("*Unrealized Profit:* " if r['is_open'] else "*Close Profit: *")
                + "`{profit_ratio:.2%}` `({profit_abs_r})`",
            ])

            if r['is_open']:
                if r.get('realized_profit'):
                    lines.extend([
                        "*Realized Profit:* `{realized_profit_ratio:.2%} ({realized_profit_r})`",
                        "*Total Profit:* `{total_profit_ratio:.2%} ({total_profit_abs_r})`"
                    ])

                # Append empty line to improve readability
                lines.append(" ")
                if (r['stop_loss_abs'] != r['initial_stop_loss_abs']
                        and r['initial_stop_loss_ratio'] is not None):
                    # Adding initial stoploss only if it is different from stoploss
                    lines.append("*Initial Stoploss:* `{initial_stop_loss_abs:.8f}` "
                                 "`({initial_stop_loss_ratio:.2%})`")

                # Adding stoploss and stoploss percentage only if it is not None
                lines.append("*Stoploss:* `{stop_loss_abs:.8g}` " +
                             ("`({stop_loss_ratio:.2%})`" if r['stop_loss_ratio'] else ""))
                lines.append("*Stoploss distance:* `{stoploss_current_dist:.8g}` "
                             "`({stoploss_current_dist_ratio:.2%})`")
                if r.get('open_orders'):
                    lines.append(
                        "*Open Order:* `{open_orders}`"
                        + ("- `{exit_order_status}`" if r['exit_order_status'] else ""))

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
    async def _status_table(self, update: Update, context: CallbackContext) -> None:
        """
        Handler for /status table.
        Returns the current TradeThread status in table format
        :param bot: telegram bot
        :param update: message update
        :return: None
        """
        fiat_currency = self._config.get('fiat_display_currency', '')
        statlist, head, fiat_profit_sum = self._rpc._rpc_status_table(
            self._config['stake_currency'], fiat_currency)

        show_total = not isnan(fiat_profit_sum) and len(statlist) > 1
        max_trades_per_msg = 50
        """
        Calculate the number of messages of 50 trades per message
        0.99 is used to make sure that there are no extra (empty) messages
        As an example with 50 trades, there will be int(50/50 + 0.99) = 1 message
        """
        messages_count = max(int(len(statlist) / max_trades_per_msg + 0.99), 1)
        for i in range(0, messages_count):
            trades = statlist[i * max_trades_per_msg:(i + 1) * max_trades_per_msg]
            if show_total and i == messages_count - 1:
                # append total line
                trades.append(["Total", "", "", f"{fiat_profit_sum:.2f} {fiat_currency}"])

            message = tabulate(trades,
                               headers=head,
                               tablefmt='simple')
            if show_total and i == messages_count - 1:
                # insert separators line between Total
                lines = message.split("\n")
                message = "\n".join(lines[:-1] + [lines[1]] + [lines[-1]])
            await self._send_msg(f"<pre>{message}</pre>", parse_mode=ParseMode.HTML,
                                 reload_able=True, callback_path="update_status_table",
                                 query=update.callback_query)

