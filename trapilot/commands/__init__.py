# flake8: noqa: F401
"""
Commands module.
Contains all start-commands, subcommands and CLI Interface creation.

Note: Be careful with file-scoped imports in these subfiles.
    as they are parsed on startup, nothing containing optional modules should be loaded.
"""
from trapilot.commands.analyze_commands import start_analysis_entries_exits
from trapilot.commands.apikey_commands import start_api_key
from trapilot.commands.arguments import Arguments
from trapilot.commands.build_config_commands import start_new_config
from trapilot.commands.data_commands import (
    start_convert_data,
    start_convert_trades,
    start_download_data,
    start_list_data,
)
from trapilot.commands.db_commands import start_convert_db
from trapilot.commands.deploy_commands import (
    start_create_userdir,
    start_install_ui,
    start_new_strategy,
)
from trapilot.commands.hyperopt_commands import start_hyperopt_list, start_hyperopt_show
from trapilot.commands.list_commands import (
    start_list_exchanges,
    start_list_freqAI_models,
    start_list_markets,
    start_list_strategies,
    start_list_timeframes,
    start_show_trades,
)
from trapilot.commands.optimize_commands import (
    start_backtesting,
    start_backtesting_show,
    start_edge,
    start_hyperopt,
    start_lookahead_analysis,
    start_recursive_analysis,
)
from trapilot.commands.pairlist_commands import start_test_pairlist
from trapilot.commands.plot_commands import start_plot_dataframe, start_plot_profit
from trapilot.commands.strategy_utils_commands import start_strategy_update
from trapilot.commands.trade_commands import start_trading
from trapilot.commands.webserver_commands import start_webserver
