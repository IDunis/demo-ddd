"""
    Alpaca API creation definition.
    Copyright (C) 2021 Arun Annamalai

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

live_url = "https://fc-tradeapi.ssi.com.vn"
paper_url = "https://fc-tradeapi.ssi.com.vn"


class REST:
    def __init__(
        self,
        key_id: str = None,
        secret_key: str = None,
        base_url: str = None,
        api_version: str = None,
        oauth=None,
        raw_data: bool = False,
    ):
        self.key_id = key_id
        self.secret_key = secret_key
        self.base_url = base_url
        self.api_version = api_version
        self.oauth = oauth
        self.raw_data = raw_data

    def get_account(self) -> any:
        print("SSI REST get_account")
        return {}

    def get_clock(self) -> str:
        print("SSI REST get_clock")
        return ""


def create_client(auth: AuthConstructor, sandbox_mode=True):
    if sandbox_mode:
        api_url = paper_url
    else:
        api_url = live_url

    return REST(
        auth.keys["api_key"], auth.keys["api_secret"], api_url, "v2", raw_data=True
    )
