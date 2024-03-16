"""
    Updated CLI for interacting with and uploading trapilot models.
    Copyright (C) 2022 Matias Kotlik

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import argparse
import json
import logging
import os.path
import pkgutil
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import traceback
import webbrowser
from pathlib import Path
from typing import Any, Dict, Optional

from questionary import Choice

from trapilot import __version__
from trapilot.deployment.api import API
from trapilot.deployment.deploy import get_python_version, zip_dir
from trapilot.deployment.exchange_data import (
    EXCHANGE_CHOICES,
    EXCHANGE_CHOICES_NO_KEYLESS,
    EXCHANGES,
    Exchange,
    exc_display_name,
)
from trapilot.deployment.keys import add_key, load_keys, write_keys
from trapilot.deployment.login import get_token, logout, poll_login
from trapilot.deployment.ui import (
    confirm,
    path,
    print_failure,
    print_success,
    print_work,
    select,
    show_spinner,
    text,
)
from trapilot.utils.gc_setup import gc_set_threshold
from trapilot.utils.utils import (
    load_backtest_preferences,
    load_deployment_settings,
    load_user_preferences,
)

TEMPLATES = {
    "strategy": {"none": "none.py", "rsi_bot": "rsi_bot.py"},
    "screener": {"none": "none_screener.py", "rsi_screener": "rsi_screener.py"},
}

# AUTH_URL = 'https://app.trapilot.finance/auth/signin?redirectUrl=/deploy'

logger = logging.getLogger(__name__)


def validate_non_empty(text):
    if not text.strip():
        return "Please enter a value"
    return True


def create_model(api, name, description, model_type, project_id=None):
    with show_spinner("Creating model") as spinner:
        try:
            # Expanded this logic because the other one was broken
            if project_id is not None:
                model = api.create_model(project_id, model_type, name, description)
            else:
                model = api.create_model(api.user_id, model_type, name, description)
        except Exception:
            spinner.fail("Failed to create model")
            raise
        spinner.ok("Created model")

    return model


# def ensure_login() -> API:
#     # TODO print selected team ?
#     api = is_logged_in()
#     if api:
#         return api
#     return launch_login_flow()


# def is_logged_in() -> Optional[API]:
#     token = get_token()
#     if not token:
#         return
#
#     # log into deployment api
#     try:
#         return API(token)
#     except Exception:  # TODO
#         return


# def launch_login_flow() -> API:
#     try:
#         webbrowser.open_new(AUTH_URL)
#         print_work(f'Your browser was opened to {AUTH_URL}. Open the window and login.')
#     except Exception:
#         print_work(f'Could not find a browser to open. Navigate to {AUTH_URL} and login')
#
#     api = None
#     with show_spinner(f'Waiting for login') as spinner:
#         try:
#             api = poll_login()
#         except Exception:
#             pass  # we just check for api being valid, poll_login can return None
#
#         if not api:
#             spinner.fail('Failed to login')
#             sys.exit(1)
#
#         spinner.ok('Logged in')
#     return api


def add_key_interactive(exchange: Exchange):
    tld = None
    if exchange.tlds:
        tld = select(
            "What TLD are you using?",
            [Choice(f"{exchange.name}.{tld}", tld) for tld in exchange.tlds],
        ).unsafe_ask()
    name = text("Give this key a name:", instruction="(Optional)").unsafe_ask()

    saved_data = {}
    for instruction, key in exchange.key_info.items():
        saved_data[key] = (
            text(f"{instruction}:", validate=validate_non_empty).unsafe_ask().strip()
        )
    saved_data["dry_run"] = confirm(
        "Is this testnet/sandbox key?", default=False
    ).unsafe_ask()

    if add_key(exchange, tld, name, saved_data):
        print_success(
            f"Your API key for {exchange.display_name} was added to this model"
        )
        return tld
    print_failure(
        f"Your API Key for {exchange.display_name} was not added to the model"
    )
    return False


def init_starter_model(model):
    path = model.get("path", ".")
    url = model.get("url", "https://github.com/trapilot-finance/examples")
    exchange_name = model.get("exchange", "alpaca")
    model_type = model.get("modelType", "strategy")

    with tempfile.TemporaryDirectory() as dir:
        with show_spinner("Downloading files") as spinner:
            ret = subprocess.run(
                ["git", "clone", url, dir],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            ).returncode
            if ret != 0:
                spinner.fail(
                    "Failed to download starter model. Make sure you have `git` installed."
                )
                return
            for file in os.listdir(os.path.join(dir, path)):
                try:
                    shutil.move(os.path.join(dir, path, file), "./")
                except OSError as e:
                    spinner.fail(
                        f"Failed while copying files: {e}. Try again in an empty directory."
                    )
                    return
            spinner.ok("Downloaded files")

    clean_trapilot_json()

    exchange = next((e for e in EXCHANGES if e.name == exchange_name), None)

    if (
        exchange
        and confirm(
            f"Would you like to add {exchange.display_name} keys to your model?"
        ).unsafe_ask()
    ):
        add_key_interactive(exchange)

    # if confirm('Would you like to connect this model to the Trapilot Platform?').unsafe_ask():
    #     api = ensure_login()
    #     ensure_model(api)

    print_success("Done!")


def clean_trapilot_json():
    with open("user_data/trapilot.json", "r") as file:
        data = json.load(file)
    del data["model_id"]
    del data["project_id"]
    del data["api_key"]
    del data["api_pass"]
    with open("user_data/trapilot.json", "w") as file:
        json.dump(data, file, indent=4)


def trapilot_init(args):
    # warn nonempty dir
    files = [f for f in os.listdir() if not f.startswith(".")]
    if (
        files
        and not confirm(
            "This directory is not empty. Would you like to continue anyways?"
        ).unsafe_ask()
    ):
        return

    api = None
    if args.model:
        # api = ensure_login()
        # starters = api.get_starter_models() or []
        # model = next((m for m in starters if m['shortName'] == args.model), None)
        # if not model:
        #     print_failure('That starter model doesn\'t exist. Make sure you are typing the name properly.')
        #     return
        print_failure("Starter models are currently disabled.")
        ## init_starter_model(model)
        return

    exchange = select(
        "What exchange would you like to connect to?", EXCHANGE_CHOICES
    ).unsafe_ask()

    model_type = "strategy"
    tld = None
    template = None
    if exchange:
        model_type = select(
            "What type of model do you want to create?",
            [Choice(mt.title(), mt) for mt in TEMPLATES],
        ).unsafe_ask()
        templates = TEMPLATES[model_type]

        template_name = select(
            "What template would you like to use for your new model?", templates
        ).unsafe_ask()
        template = templates[template_name]

        if confirm(
            "Would you like to add keys for this exchange?\n"
            "You can do this later at any time by running `trapilot key add`"
        ).unsafe_ask():
            tld = add_key_interactive(exchange)

    api = None
    model = None
    # if args.prompt_login and confirm('Would you like to connect this model to the Trapilot Platform?').unsafe_ask():
    #     if not api:
    #         api = ensure_login()
    #     model = get_model_interactive(api, model_type)

    with show_spinner("Generating files") as spinner:
        files = [
            ("tradebot.py", generate_bot_py(exchange, template), False),
            ("user_data/backtest.json", generate_backtest_json(exchange), False),
            # ('user_data/requirements.txt', 'blankly\n', False),
            ("user_data/keys.json", generate_keys_json(), True),
            (
                "user_data/trapilot.json",
                generate_trapilot_json(api, model, model_type),
                False,
            ),
            ("user_data/settings.json", generate_settings_json(tld or "com"), False),
        ]
        spinner.ok("Generated files")

    for path, data, force_overwrite in files:
        exists = Path(path).exists()
        overwrite_prompt = confirm(
            f"{path} already exists, would you like to overwrite it?", default=False
        )
        if force_overwrite or not exists or overwrite_prompt.unsafe_ask():
            with open(path, "w") as file:
                file.write(data)

    # TODO open on platform WITHOUT STARTING

    print_success(
        "Done! Your model was created. Run `python tradebot.py` to run a backtest and get started."
    )


def get_model_interactive(api, model_type):
    create = select(
        "Would you like to create a new model or attach to an existing one?",
        [Choice("Create new model", True), Choice("Attach to existing model", False)],
    ).unsafe_ask()
    if create:
        default_name = Path.cwd().name  # default name is working dir name
        name = text(
            "Model name?", default=default_name, validate=validate_non_empty
        ).unsafe_ask()
        description = text("Model description?", instruction="(Optional)").unsafe_ask()
        teams = api.list_teams()
        team_id = None
        if teams:
            team_choices = [Choice("Create on my personal account", False)] + [
                Choice(team.get("name", team["id"]), team["id"]) for team in teams
            ]
            team_id = select(
                "What team would you like to create this model under?", team_choices
            ).unsafe_ask()
        return create_model(api, name, description, model_type, team_id)

    with show_spinner("Loading models...") as spinner:
        models = api.list_all_models()
        spinner.ok("Loaded")

    if not models:
        print_failure(
            "You have no models on the platform. Are you logged into the right account?"
        )
        sys.exit()

    model = select(
        "Select an existing model to attach to:",
        [Choice(get_model_repr(model), model) for model in models],
    ).unsafe_ask()
    if model.get("type", None) != model_type:
        pass  # TODO
    return model


def get_model_repr(model: dict) -> str:
    name = model.get("name", model["id"])
    team = model.get("team", {}).get("name", None)
    if team:
        name = team + " - " + name
    return name


def generate_settings_json(tld: str):
    data = load_user_preferences(override_allow_nonexistent=True)

    data["settings"]["binance"]["binance_tld"] = tld
    # data['settings']['ftx']['ftx_tld'] = tld
    # data['settings']['ftx_futures']['ftx_tld'] = tld
    return json.dumps(data, indent=4)


def generate_keys_json():
    try:
        with open("user_data/keys.json") as file:
            keys = json.load(file)
    except FileNotFoundError:
        keys = {}

    for exchange in EXCHANGES:
        keys[exchange.name] = keys.get(
            exchange.name,
            {"example-portfolio": {v: "*" * 20 for v in exchange.key_info.values()}},
        )
        for portfolio in keys[exchange.name].values():
            portfolio["sandbox"] = portfolio.get("sandbox", False)
    return json.dumps(keys, indent=4)


def generate_trapilot_json(
    api: Optional[API],
    model: Optional[dict],
    model_type: str,
    main_script: str = "bot.py",
):
    data = load_deployment_settings()
    data["main_script"] = main_script
    data["type"] = model_type
    data["python_version"] = get_python_version()

    if model:
        data["model_id"] = model["id"]
        data["project_id"] = model["projectId"]

    if api:
        project_id = model["projectId"] if model else api.user_id
        keys = api.generate_keys(project_id, f'Local keys for {data["model_id"]}')
        data["api_key"] = keys["apiKey"]
        data["api_pass"] = keys["apiPass"]
    return json.dumps(data, indent=4)


def generate_backtest_json(exchange: Optional[Exchange]) -> str:
    currency = exchange.currency if exchange else "USD"
    data = load_backtest_preferences(override_allow_nonexistent=True)

    data["settings"]["quote_account_value_in"] = currency
    return json.dumps(data, indent=4)


def generate_bot_py(exchange: Optional[Exchange], template: str) -> str:
    if not exchange:
        # template should be None
        return pkgutil.get_data("trapilot", "data/templates/keyless.py").decode("utf-8")
    bot_py = pkgutil.get_data("trapilot", f"data/templates/{template}").decode("utf-8")
    for pattern, replacement in [
        (
            "EXCHANGE_NAME",
            exchange.display_name,
        ),
        (
            "EXCHANGE_CLASS",
            exchange.python_class,
        ),
        (
            "SYMBOL_LIST",
            "['" + "', '".join(exchange.symbols) + "']",
        ),
        (
            "SYMBOL",
            exchange.symbols[0],
        ),
        ("QUOTE_ASSET", exchange.currency),
    ]:
        bot_py = bot_py.replace(pattern, replacement)
    return bot_py


# def trapilot_login(args):
#     if is_logged_in():
#         print_success('You are already logged in')
#         return
#
#     launch_login_flow()


def trapilot_logout(args):
    with show_spinner("Logging out of the Trapilot Platform") as spinner:
        try:
            logout()
        except Exception:
            spinner.fail("Failed to logout")
            raise
        spinner.ok("Logged out")


# def ensure_model(api: API):
#     # create model if it doesn't exist
#     try:
#         with open('user_data/trapilot.json', 'r') as file:
#             data = json.load(file)
#     except FileNotFoundError:
#         print_failure('There was no model detected in this directory. Try running `trapilot init` to create one')
#         sys.exit(1)
#
#     if 'plan' not in data:
#         data['plan'] = select('Select a plan:', [Choice(f'{name} - CPU: {info["cpu"]} RAM: {info["ram"]}', name)
#                                                  for name, info in api.get_plans('live').items()]).unsafe_ask()
#
#     if 'model_id' not in data or 'project_id' not in data:
#         model = get_model_interactive(api, data.get('type', 'strategy'))
#         data['model_id'] = model['modelId']
#         data['project_id'] = model['projectId']
#
#     if 'api_key' not in data or 'api_pass' not in data:
#         keys = api.generate_keys(data['project_id'], f'Local keys for {data["model_id"]}')
#         data['api_key'] = keys['apiKey']
#         data['api_pass'] = keys['apiPass']
#
#     files = [f for f in os.listdir() if not f.startswith('.')]
#     if 'main_script' not in data or data['main_script'].lstrip('./') not in files:
#         if 'bot.py' in files:
#             data['main_script'] = 'bot.py'
#         else:
#             data['main_script'] = path(
#                 'What is the path to your main script/entry point? (Usually bot.py)').unsafe_ask()
#
#     if data['main_script'].lstrip('./') not in files:
#         print_failure(
#             f'The file {data["main_script"]} could not be found. Please create it or set a different entry point.')
#         sys.exit()
#
#     # save model_id and plan back into user_data/trapilot.json
#     with open('user_data/trapilot.json', 'w') as file:
#         json.dump(data, file, indent=4)
#
#     return data


def missing_deployment_files() -> list:
    paths = [
        "user_data/trapilot.json",
        "user_data/keys.json",
        "user_data/backtest.json",
        "user_data/settings.json",
        "requirements.txt",
    ]
    return [path for path in paths if not Path(path).is_file()]


# def trapilot_deploy(args):
#     api = ensure_login()
#
#     data = ensure_model(api)
#     for path in missing_deployment_files():
#         if not confirm(f'{path} is missing. Are you sure you want to continue?',
#                        default=False).unsafe_ask():
#             print_failure('Deployment cancelled')
#             print_failure(f'You can try `trapilot init` to regenerate the {path} file.')
#             return
#
#     description = text('Enter a description for this version of the model:').unsafe_ask()
#
#     with show_spinner('Uploading model') as spinner:
#         model_path = zip_dir('.', data['ignore_files'])
#
#         params = {
#             'file_path': model_path,
#             'project_id': data['project_id'],  # set by ensure_model
#             'model_id': data['model_id'],  # set by ensure_model
#             'version_description': description,
#             'python_version': get_python_version(),
#             'type_': data.get('type', 'strategy'),
#             'plan': data['plan']  # set by ensure_model
#         }
#         if data['type'] == 'screener':
#             params['schedule'] = data['screener']['schedule']
#
#         response = api.deploy(**params)
#         if response.get('status', None) == 'success':
#             spinner.ok('Model uploaded')
#         else:
#             spinner.fail('Error: ' + response['error'])


def trapilot_add_key(args):
    exchange = select(
        "What exchange would you like to add a key for?", EXCHANGE_CHOICES_NO_KEYLESS
    ).unsafe_ask()
    add_key_interactive(exchange)


def trapilot_list_key(args):
    data = load_keys()
    for exchange_name, keys in data.items():
        for name, key_data in keys.items():
            # filter 'empty'
            if any((isinstance(d, str) and "*" in d) for d in key_data.values()):
                continue
            exchange_display_name = exc_display_name(exchange_name)
            print_work(f"{exchange_display_name}: {name}")
            for k, v in key_data.items():
                print_work(f"    {k}: {v}")


def trapilot_remove_key(args):
    data = load_keys()

    key_choices = [
        Choice(f"{exc_display_name(exchange)}: {name}", (exchange, name))
        for exchange, keys in data.items()
        for name in keys
    ]
    if not key_choices:
        return
    exchange, key = select(
        "Which key would you like to delete?", key_choices
    ).unsafe_ask()

    del data[exchange][key]
    write_keys(data)


def trapilot_key(args):
    func = select(
        "What would you like to do?",
        [
            Choice("Add a key", trapilot_add_key),
            Choice("Show all keys", trapilot_list_key),
            Choice("Remove a key", trapilot_remove_key),
        ],
    ).unsafe_ask()
    func(args)


def start_monitor(args):
    try:
        import psutil
    except ImportError:
        raise ImportError(
            "Must install psutil (pip install psutil) to monitor "
            "the Trapilot process"
        )
    print("Process must be killed to halt monitoring.")

    pid = os.getpid()
    process = psutil.Process(pid)
    while True:
        monitor_string = "\rCPU Usage: "
        monitor_string += str(process.cpu_percent())
        monitor_string += " | "
        monitor_string += "Memory Usage: "
        monitor_string += str(process.memory_percent())
        sys.stdout.write(monitor_string)
        sys.stdout.flush()
        time.sleep(1)


def start_trade(args: Dict[str, Any]) -> int:
    """
    Main entry point for trading mode
    """
    # Import here to avoid loading worker module when it's not used
    # from trapilot.worker import Worker

    def term_handler(signum, frame):
        # Raise KeyboardInterrupt - so we can handle it in the same way as Ctrl-C
        raise KeyboardInterrupt()

    # Create and run worker
    worker = None
    try:
        signal.signal(signal.SIGTERM, term_handler)
        # worker = Worker(args)
        # worker.run()
        print("DO NOTHING")
    except Exception as e:
        logger.error(str(e))
        logger.exception("Fatal exception!")
    except KeyboardInterrupt:
        logger.info("SIGINT received, aborting ...")
    finally:
        if worker:
            logger.info("worker found ... calling exit")
            worker.exit()
    return 0


def main():
    parser = argparse.ArgumentParser(
        prog="trapilot", description="Trapilot CLI & deployment tool"
    )
    subparsers = parser.add_subparsers(required=True)

    init_parser = subparsers.add_parser(
        "init", help="Initialize a new model in the current directory"
    )
    init_parser.add_argument("model", nargs="?", help="select a starter model")
    init_parser.add_argument(
        "-n",
        "--no-login",
        action="store_false",
        dest="prompt_login",
        help="don't prompt to connect to Trapilot Platform",
    )
    init_parser.set_defaults(func=trapilot_init)

    # login_parser = subparsers.add_parser('login', help='Login to the Trapilot Platform')
    # login_parser.set_defaults(func=trapilot_login)

    # logout_parser = subparsers.add_parser('logout', help='Logout of the Trapilot Platform')
    # logout_parser.set_defaults(func=trapilot_logout)

    # deploy_parser = subparsers.add_parser('deploy', help='Upload this model to the Trapilot Platform')
    # deploy_parser.set_defaults(func=trapilot_deploy)

    monitor_parser = subparsers.add_parser(
        "monitor", help="Process must be killed to halt monitoring"
    )
    monitor_parser.set_defaults(func=start_monitor)

    monitor_parser = subparsers.add_parser(
        "trade", help="Main entry point for trading mode"
    )
    monitor_parser.set_defaults(func=start_trade)

    key_parser = subparsers.add_parser("key", help="Manage model Exchange API keys")
    key_parser.set_defaults(func=trapilot_key)
    key_subparsers = key_parser.add_subparsers()

    key_add_parser = key_subparsers.add_parser(
        "remove", help="Delete API Keys from this model"
    )
    key_add_parser.set_defaults(func=trapilot_remove_key)

    key_add_parser = key_subparsers.add_parser(
        "list", help="List API Keys that this model is using"
    )
    key_add_parser.set_defaults(func=trapilot_list_key)

    key_add_parser = key_subparsers.add_parser(
        "add", help="Add an API Key to this model"
    )
    key_add_parser.set_defaults(func=trapilot_add_key)

    # run the selected command
    args = parser.parse_args()
    try:
        logger.info(f"trapilot {__version__}")
        gc_set_threshold()
        args.func(args)
    except KeyboardInterrupt:
        print_failure("Cancelled by user")
    except Exception:
        print_failure("An error occurred. Traceback:")
        traceback.print_exc()


if __name__ == "__main__":
    main()
