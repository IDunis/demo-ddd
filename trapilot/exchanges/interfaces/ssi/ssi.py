"""
    SSI exchange definitions and setup
    Copyright (C) 2021 Arun Annamalai, Emerson Dove, Brandon Fan

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

from trapilot.exchanges.auth.auth_constructor import AuthConstructor
from trapilot.exchanges.exchange import Exchange
from trapilot.exchanges.interfaces.ssi.ssi_api import REST, create_client


class SSI(Exchange):
    def __init__(
        self, portfolio_name=None, keys_path="user_data/keys.json", settings_path=None
    ):
        Exchange.__init__(self, "ssi", portfolio_name, settings_path)

        # Load the auth from the keys file
        auth = AuthConstructor(
            keys_path, portfolio_name, "ssi", ["api_key", "api_secret", "dry_run"]
        )

        dry_run = super().evaluate_sandbox(auth)

        calls = create_client(auth, dry_run)

        # Always finish the method with this function
        super().construct_interface_and_cache(calls)

    def get_exchange_state(self):
        return self.interface.get_products()

    def get_asset_state(self, symbol):
        return self.interface.get_account(symbol)

    def get_direct_calls(self) -> REST:
        return self.calls

    def get_market_clock(self):
        return self.calls.get_clock()
