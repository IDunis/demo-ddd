# flake8: noqa: F401
"""
Commands module.
Contains all start-commands, subcommands and CLI Interface creation.

Note: Be careful with file-scoped imports in these subfiles.
    as they are parsed on startup, nothing containing optional modules should be loaded.
"""
from flytrade.commands.analyze_commands import start_analysis_entries_exits
from flytrade.commands.arguments import Arguments
from flytrade.commands.build_config_commands import start_new_config
from flytrade.commands.data_commands import (start_convert_data, start_convert_trades,
                                              start_download_data, start_list_data)
from flytrade.commands.db_commands import start_convert_db
from flytrade.commands.deploy_commands import (start_create_userdir, start_install_ui,
                                                start_new_strategy)
from flytrade.commands.hyperopt_commands import start_hyperopt_list, start_hyperopt_show
from flytrade.commands.list_commands import (start_list_exchanges, start_list_freqAI_models,
                                              start_list_markets, start_list_strategies,
                                              start_list_timeframes, start_show_trades)
from flytrade.commands.optimize_commands import (start_backtesting, start_backtesting_show,
                                                  start_edge, start_hyperopt,
                                                  start_lookahead_analysis,
                                                  start_recursive_analysis)
from flytrade.commands.pairlist_commands import start_test_pairlist
from flytrade.commands.plot_commands import start_plot_dataframe, start_plot_profit
from flytrade.commands.strategy_utils_commands import start_strategy_update
from flytrade.commands.trade_commands import start_trading
from flytrade.commands.webserver_commands import start_webserver
