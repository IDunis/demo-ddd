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

from trapilot.blankly.exchanges.auth.auth_constructor import AuthConstructor
from trapilot.blankly.exchanges.exchange import Exchange
from trapilot.blankly.exchanges.interfaces.ssi.ssi_api import SsiAPI


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

        calls = SsiAPI(auth, dry_run)

        # Always finish the method with this function
        super().construct_interface_and_cache(calls)

    def get_direct_calls(self) -> SsiAPI:
        return self.calls
