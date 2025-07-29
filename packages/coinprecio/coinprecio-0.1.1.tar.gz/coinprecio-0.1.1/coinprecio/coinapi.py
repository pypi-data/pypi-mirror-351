# Copyright (c) 2025 Joel Torres
# Distributed under the MIT License. See the accompanying file LICENSE.

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import requests
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from .exceptions import *
from .symbols import symbols
from .currencies import currencies

_COINAPI_BACKEND = "coinmarketcap"
_COINAPI_CURRENCY = "USD"
_COINAPI_SYMBOL = "BTC"


class _CoinApi(ABC):
    @abstractmethod
    def get_price(self):
        pass

    @abstractmethod
    def get_price_all(self):
        pass


@dataclass
class _CoinApiData:
    domain: str
    api_key: str = field(repr=False)
    symbol: str
    currency: str

    def __post_init__(self):
        if not isinstance(self.api_key, str) or len(self.api_key) == 0:
            raise CoinApiDataError("api_key must be a string and not empty")

        if not isinstance(self.symbol, str) or self.symbol not in symbols:
            raise CoinApiDataError("symbol must be a string and in the supported symbol list")

        if not isinstance(self.currency, str) or self.currency not in currencies:
            raise CoinApiDataError("currency must be a string and in the supported currency list")


class _CoinMarketCapApi(_CoinApi, _CoinApiData):
    def __init__(self, api_key: str, symbol: str, currency: str):

        _CoinApiData.__init__(self, "https://pro-api.coinmarketcap.com",
                              api_key, symbol, currency)

        self.api_headers = {
            "Accepts": "application/json",
            "X-CMC_PRO_API_KEY": self.api_key,
        }

        self.api_urls = [f"{self.domain}/v2/cryptocurrency/quotes/latest"]
        self.api_endpoints = {
            "get_price": {
                    "url": self.api_urls[0],
                    "params": {
                        "symbol": self.symbol,
                        "convert": self.currency
                    }
            },
            "get_price_all": {
                    "url": self.api_urls[0],
                    "params": {
                        "symbol": ",".join(symbols),
                        "convert": self.currency
                }
            }
        }


    def get_price(self):

        response = _fetch(self.api_endpoints["get_price"]["url"],
                          self.api_headers,
                          self.api_endpoints["get_price"]["params"]).json()

        data = response["data"]

        return data[self.symbol][0]["quote"][self.currency]["price"]

    def get_price_all(self):

        response = _fetch(self.api_endpoints["get_price_all"]["url"],
                          self.api_headers,
                          self.api_endpoints["get_price_all"]["params"]).json()

        data = response["data"]

        return {symbol: data[symbol][0]["quote"][self.currency]["price"]
                for symbol in symbols}


def _fetch(api_url, api_headers, api_parameters):
    try:
        response = requests.get(api_url,
                                headers=api_headers,
                                params=api_parameters)
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        raise CoinApiFetchError(f"Unable to connect to API URL: {api_url}") from None

    if response.status_code == 200:
        return response
    else:
        raise CoinApiFetchError(f"HTTP response was not 200 OK, got status: {response.status_code}")


def api(api_key: str, backend: str = _COINAPI_BACKEND,
        symbol: str = _COINAPI_SYMBOL, currency: str = _COINAPI_CURRENCY) -> _CoinApi:

    env_backend = os.getenv("COINAPI_BACKEND")
    env_symbol = os.getenv("COINAPI_SYMBOL")
    env_currency = os.getenv("COINAPI_CURRENCY")
    if env_backend:
        backend = env_backend
    if env_symbol:
        symbol = env_symbol
    if env_currency:
        currency = env_currency

    if backend == "coinmarketcap":
        return _CoinMarketCapApi(api_key, symbol, currency)
    else:
        raise CoinApiFactoryError(f"Unsupported API backend: {backend}")
