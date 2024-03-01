"""
This module contains the argument manager class
"""
import argparse
from functools import partial
from pathlib import Path
from typing import Any, Dict, List, Optional

from trapilot.commands.cli_options import AVAILABLE_CLI_OPTIONS
from trapilot.constants import DEFAULT_CONFIG


ARGS_COMMON = ["verbosity", "logfile", "version", "config", "datadir", "user_data_dir"]

ARGS_STRATEGY = ["strategy", "strategy_path", "recursive_strategy_search", "freqaimodel",
                 "freqaimodel_path"]

ARGS_TRADE = ["db_url", "sd_notify", "dry_run", "dry_run_wallet", "fee"]

ARGS_WEBSERVER: List[str] = []

ARGS_COMMON_OPTIMIZE = ["timeframe", "timerange", "dataformat_ohlcv",
                        "max_open_trades", "stake_amount", "fee", "pairs"]

ARGS_BACKTEST = ARGS_COMMON_OPTIMIZE + ["position_stacking", "use_max_market_positions",
                                        "enable_protections", "dry_run_wallet", "timeframe_detail",
                                        "strategy_list", "export", "exportfilename",
                                        "backtest_breakdown", "backtest_cache",
                                        "freqai_backtest_live_models"]

ARGS_HYPEROPT = ARGS_COMMON_OPTIMIZE + ["hyperopt", "hyperopt_path",
                                        "position_stacking", "use_max_market_positions",
                                        "enable_protections", "dry_run_wallet", "timeframe_detail",
                                        "epochs", "spaces", "print_all",
                                        "print_colorized", "print_json", "hyperopt_jobs",
                                        "hyperopt_random_state", "hyperopt_min_trades",
                                        "hyperopt_loss", "disableparamexport",
                                        "hyperopt_ignore_missing_space", "analyze_per_epoch"]

ARGS_EDGE = ARGS_COMMON_OPTIMIZE + ["stoploss_range"]

ARGS_LIST_STRATEGIES = ["strategy_path", "print_one_column", "print_colorized",
                        "recursive_strategy_search"]

ARGS_LIST_FREQAIMODELS = ["freqaimodel_path", "print_one_column", "print_colorized"]

ARGS_LIST_HYPEROPTS = ["hyperopt_path", "print_one_column", "print_colorized"]

ARGS_BACKTEST_SHOW = ["exportfilename", "backtest_show_pair_list", "backtest_breakdown"]

ARGS_LIST_EXCHANGES = ["print_one_column", "list_exchanges_all"]

ARGS_LIST_TIMEFRAMES = ["exchange", "print_one_column"]

ARGS_LIST_PAIRS = ["exchange", "print_list", "list_pairs_print_json", "print_one_column",
                   "print_csv", "base_currencies", "quote_currencies", "list_pairs_all",
                   "trading_mode"]

ARGS_TEST_PAIRLIST = ["user_data_dir", "verbosity", "config", "quote_currencies",
                      "print_one_column", "list_pairs_print_json", "exchange"]

ARGS_CREATE_USERDIR = ["user_data_dir", "reset"]

ARGS_BUILD_CONFIG = ["config"]

ARGS_BUILD_STRATEGY = ["user_data_dir", "strategy", "template"]

ARGS_CONVERT_DATA_TRADES = ["pairs", "format_from_trades", "format_to", "erase", "exchange"]
ARGS_CONVERT_DATA = ["pairs", "format_from", "format_to", "erase", "exchange"]
ARGS_CONVERT_DATA_OHLCV = ARGS_CONVERT_DATA + ["timeframes", "trading_mode", "candle_types"]

ARGS_CONVERT_TRADES = ["pairs", "timeframes", "exchange", "dataformat_ohlcv", "dataformat_trades"]

ARGS_LIST_DATA = ["exchange", "dataformat_ohlcv", "pairs", "trading_mode", "show_timerange"]

ARGS_DOWNLOAD_DATA = ["pairs", "pairs_file", "days", "new_pairs_days", "include_inactive",
                      "timerange", "download_trades", "exchange", "timeframes",
                      "erase", "dataformat_ohlcv", "dataformat_trades", "trading_mode",
                      "prepend_data"]

ARGS_PLOT_DATAFRAME = ["pairs", "indicators1", "indicators2", "plot_limit",
                       "db_url", "trade_source", "export", "exportfilename",
                       "timerange", "timeframe", "no_trades"]

ARGS_PLOT_PROFIT = ["pairs", "timerange", "export", "exportfilename", "db_url",
                    "trade_source", "timeframe", "plot_auto_open", ]

ARGS_CONVERT_DB = ["db_url", "db_url_from"]

ARGS_INSTALL_UI = ["erase_ui_only", "ui_version"]

ARGS_SHOW_TRADES = ["db_url", "trade_ids", "print_json"]

ARGS_HYPEROPT_LIST = ["hyperopt_list_best", "hyperopt_list_profitable",
                      "hyperopt_list_min_trades", "hyperopt_list_max_trades",
                      "hyperopt_list_min_avg_time", "hyperopt_list_max_avg_time",
                      "hyperopt_list_min_avg_profit", "hyperopt_list_max_avg_profit",
                      "hyperopt_list_min_total_profit", "hyperopt_list_max_total_profit",
                      "hyperopt_list_min_objective", "hyperopt_list_max_objective",
                      "print_colorized", "print_json", "hyperopt_list_no_details",
                      "hyperoptexportfilename", "export_csv"]

ARGS_HYPEROPT_SHOW = ["hyperopt_list_best", "hyperopt_list_profitable", "hyperopt_show_index",
                      "print_json", "hyperoptexportfilename", "hyperopt_show_no_header",
                      "disableparamexport", "backtest_breakdown"]

ARGS_ANALYZE_ENTRIES_EXITS = ["exportfilename", "analysis_groups", "enter_reason_list",
                              "exit_reason_list", "indicator_list", "timerange",
                              "analysis_rejected", "analysis_to_csv", "analysis_csv_path"]

NO_CONF_REQURIED = ["convert-data", "convert-trade-data", "download-data", "list-timeframes",
                    "list-markets", "list-pairs", "list-strategies", "list-freqaimodels",
                    "list-data", "hyperopt-list", "hyperopt-show", "backtest-filter",
                    "plot-dataframe", "plot-profit", "show-trades", "trades-to-ohlcv",
                    "strategy-updater"]

NO_CONF_ALLOWED = ["create-userdir", "list-exchanges", "new-strategy"]

ARGS_STRATEGY_UPDATER = ["strategy_list", "strategy_path", "recursive_strategy_search"]

ARGS_LOOKAHEAD_ANALYSIS = [
    a for a in ARGS_BACKTEST if a not in ("position_stacking", "use_max_market_positions", 'cache')
    ] + ["minimum_trade_amount", "targeted_trade_amount", "lookahead_analysis_exportfilename"]

ARGS_RECURSIVE_ANALYSIS = ["timeframe", "timerange", "dataformat_ohlcv", "pairs", "startup_candle"]


class Arguments:
    """
    Arguments Class. Manage the arguments received by the cli
    """

    def __init__(self, args: Optional[List[str]]) -> None:
        self.args = args
        self._parsed_arg: Optional[argparse.Namespace] = None

    def get_parsed_arg(self) -> Dict[str, Any]:
        """
        Return the list of arguments
        :return: List[str] List of arguments
        """
        if self._parsed_arg is None:
            self._build_subcommands()
            self._parsed_arg = self._parse_args()

        return vars(self._parsed_arg)

    def _parse_args(self) -> argparse.Namespace:
        """
        Parses given arguments and returns an argparse Namespace instance.
        """
        parsed_arg = self.parser.parse_args(self.args)

        # Workaround issue in argparse with action='append' and default value
        # (see https://bugs.python.org/issue16399)
        # Allow no-config for certain commands (like downloading / plotting)
        if ('config' in parsed_arg and parsed_arg.config is None):
            conf_required = ('command' in parsed_arg and parsed_arg.command in NO_CONF_REQURIED)

            if 'user_data_dir' in parsed_arg and parsed_arg.user_data_dir is not None:
                user_dir = parsed_arg.user_data_dir
            else:
                # Default case
                user_dir = 'user_data'
                # Try loading from "user_data/config.json"
            cfgfile = Path(user_dir) / DEFAULT_CONFIG
            if cfgfile.is_file():
                parsed_arg.config = [str(cfgfile)]
            else:
                # Else use "config.json".
                cfgfile = Path.cwd() / DEFAULT_CONFIG
                if cfgfile.is_file() or not conf_required:
                    parsed_arg.config = [DEFAULT_CONFIG]

        return parsed_arg

    def _build_args(self, optionlist, parser):

        for val in optionlist:
            opt = AVAILABLE_CLI_OPTIONS[val]
            parser.add_argument(*opt.cli, dest=val, **opt.kwargs)

    def _build_subcommands(self) -> None:
        """
        Builds and attaches all subcommands.
        :return: None
        """
        # Build shared arguments (as group Common Options)
        _common_parser = argparse.ArgumentParser(add_help=False)
        group = _common_parser.add_argument_group("Common arguments")
        self._build_args(optionlist=ARGS_COMMON, parser=group)

        _strategy_parser = argparse.ArgumentParser(add_help=False)
        strategy_group = _strategy_parser.add_argument_group("Strategy arguments")
        self._build_args(optionlist=ARGS_STRATEGY, parser=strategy_group)

        # Build main command
        self.parser = argparse.ArgumentParser(description='Free, open source crypto trading bot')
        self._build_args(optionlist=['version'], parser=self.parser)

        # from freqtrade.commands import (start_analysis_entries_exits, start_backtesting,
        #                                 start_backtesting_show, start_convert_data,
        #                                 start_convert_db, start_convert_trades,
        #                                 start_create_userdir, start_download_data, start_edge,
        #                                 start_hyperopt, start_hyperopt_list, start_hyperopt_show,
        #                                 start_install_ui, start_list_data, start_list_exchanges,
        #                                 start_list_freqAI_models, start_list_markets,
        #                                 start_list_strategies, start_list_timeframes,
        #                                 start_lookahead_analysis, start_new_config,
        #                                 start_new_strategy, start_plot_dataframe, start_plot_profit,
        #                                 start_recursive_analysis, start_show_trades,
        #                                 start_strategy_update, start_test_pairlist, start_trading,
        #                                 start_webserver)
        from trapilot.commands import (start_trading)

        subparsers = self.parser.add_subparsers(dest='command',
                                                # Use custom message when no subhandler is added
                                                # shown from `main.py`
                                                # required=True
                                                )

        # Add trade subcommand
        trade_cmd = subparsers.add_parser(
            'trade',
            help='Trade module.',
            parents=[_common_parser, _strategy_parser]
        )
        trade_cmd.set_defaults(func=start_trading)
        self._build_args(optionlist=ARGS_TRADE, parser=trade_cmd)
