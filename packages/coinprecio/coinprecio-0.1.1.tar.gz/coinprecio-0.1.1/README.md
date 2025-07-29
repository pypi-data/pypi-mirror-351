# coinprecio

Cryptocurrency API client for fetching market price.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Install](#install)
- [Usage](#usage)
- [Supported API Backends](#supported-api-backends)
- [Supported Symbols](#supported-symbols)
- [Supported Currencies](#supported-currencies)
- [License](#license)

## <div id="prerequisites">Prerequisites</div>

Python >= 3.8

## <div id="install">Install</div>

```
pip install coinprecio
```

## <div id="usage">Usage</div>

*api(api_key, backend="coinmarketcap", symbol="BTC", currency="USD")*

```
from coinprecio import api

api_key = "YOUR_API_KEY"

coinapi = api(api_key)

# get price for the initialized symbol
btc_price = coinapi.get_price()

# get price dict for all supported symbols
prices = coinapi.get_price_all()
```

Note: *api_key* should be associated with the respective backend/API service.

## <div id="supported-api-backends">Supported API Backends</div>

* coinmarketcap

## <div id="supported-symbols">Supported Symbols</div>

* BTC
* ETH
* SOL
* BCH
* LTC

## <div id="supported-currencies">Supported Currencies</div>

* USD
* EUR
* JPY
* GBP

## <div id="license">License</div>

Distributed under the MIT License. See the accompanying file LICENSE.
