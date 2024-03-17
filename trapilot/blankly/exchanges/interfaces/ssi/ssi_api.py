import json
import requests

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from trapilot.blankly.exchanges.auth.auth_constructor import AuthConstructor

class SsiAPI:
    __API_URL_BASE = 'https://fc-tradeapi.ssi.com.vn/api/v2/'
    __PAPER_API_URL_BASE = 'https://fc-tradeapi.ssi.com.vn/api/v2/'

    def __init__(self, auth: AuthConstructor, dry_run: bool = True, retries=1):
        self.api_key = auth.keys["api_key"]
        self.api_secret = auth.keys["api_secret"]
        if dry_run:
            self.api_base_url = self.__PAPER_API_URL_BASE
        else:
            self.api_base_url = self.__API_URL_BASE
        self.request_timeout = 120

        self.session = requests.Session()
        retries = Retry(total=retries, backoff_factor=0.5, status_forcelist=[502, 503, 504])
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

    def __request(self, url):
        print(url)
        try:
            response = self.session.get(url, timeout=self.request_timeout)
        except requests.exceptions.RequestException:
            raise

        try:
            response.raise_for_status()
            content = json.loads(response.content.decode('utf-8'))
            return content
        except Exception as e:
            # check if json (with error message) is returned
            try:
                content = json.loads(response.content.decode('utf-8'))
                raise ValueError(content)
            # if no json
            except json.decoder.JSONDecodeError:
                pass

            raise

    def __api_url_params(self, api_url, params, api_url_has_params=False):
        # if using pro version of CoinGecko, inject key in every call
        if self.api_key:
            params['x_cg_pro_api_key'] = self.api_key

        if params:
            # if api_url contains already params and there is already a '?' avoid
            # adding second '?' (api_url += '&' if '?' in api_url else '?'); causes
            # issues with request parametes (usually for endpoints with required
            # arguments passed as parameters)
            api_url += '&' if api_url_has_params else '?'
            for key, value in params.items():
                if type(value) == bool:
                    value = str(value).lower()

                api_url += "{0}={1}&".format(key, value)
            api_url = api_url[:-1]
        return api_url

    # ---------- PING ----------#
    def ping(self, **kwargs):
        """Check API server status"""

        api_url = '{0}ping'.format(self.api_base_url)
        api_url = self.__api_url_params(api_url, kwargs)

        return self.__request(api_url)

    # ---------- EXCHANGES ----------#
    # @func_args_preprocessing
    def get_exchanges_list(self, **kwargs):
        """List all exchanges"""

        api_url = '{0}exchanges'.format(self.api_base_url)
        api_url = self.__api_url_params(api_url, kwargs)

        return self.__request(api_url)

    # @func_args_preprocessing
    def get_exchanges_by_id(self, id, **kwargs):
        """Get exchange volume in BTC and tickers"""

        api_url = '{0}exchanges/{1}'.format(self.api_base_url, id)
        api_url = self.__api_url_params(api_url, kwargs)

        return self.__request(api_url)

    # @func_args_preprocessing
    def get_exchanges_tickers_by_id(self, id, **kwargs):
        """Get exchange tickers (paginated, 100 tickers per page)"""

        api_url = '{0}exchanges/{1}/tickers'.format(self.api_base_url, id)
        api_url = self.__api_url_params(api_url, kwargs)

        return self.__request(api_url)

    # @func_args_preprocessing
    # def get_exchanges_status_updates_by_id(self, id, **kwargs):
    #     """Get status updates for a given exchange"""
    #
    #     api_url = '{0}exchanges/{1}/status_updates'.format(self.api_base_url, id)
    #     api_url = self.__api_url_params(api_url, kwargs)
    #
    #     return self.__request(api_url)
