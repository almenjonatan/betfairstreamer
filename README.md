# Betfairstreamer

What this library provides

* Run single or multiple streams simultaneously (single threaded)
* Market cache and order cache, these provide abstractions over the betfairstream
* Using numpy arrays to slicing markets selections.

## Usage

```
connection_pool = BetfairConnectionPool.create_connection_pool(
    subscription_messages=create_subscriptions(), session_token=session_token, app_key=app_key,
)

market_cache = MarketCache()
order_cache = OrderCache()

for update in connection_pool.read():
    update = orjson.loads(update)

    market_updates = market_cache(update)
    order_updates = order_cache(update)

    for market_book in market_updates:
        print(
            market_book.market_id,
            market_book.market_definition["runners"][0]["id"],
            market_book.market_definition["runners"][0]["sortPriority"],
            round(time.time() - market_cache.publish_time / 1000, 2),
            market_book.best_display[0, 0, 0, :],
        )

    for order in order_updates:
        print(order)
```
## Installation

```
pip install betfairstreamer
```


### Benchmark


### Full Example

```python
import logging
import os
import time

import orjson
from betfairlightweight import APIClient

from betfairstreamer.betfair_api import (
    BetfairMarketSubscriptionMessage,
    BetfairMarketFilter,
    BetfairMarketDataFilter,
    OP,
    BetfairOrderSubscriptionMessage,
)
from betfairstreamer.cache import MarketCache, OrderCache
from betfairstreamer.stream import BetfairConnectionPool

logging.basicConfig(level=logging.INFO)


def create_subscriptions():
    market_subscription = BetfairMarketSubscriptionMessage(
        id=1,
        op=OP.marketSubscription.value,
        marketFilter=BetfairMarketFilter(eventTypeIds=["7"], marketTypes=["WIN"]),
        marketDataFilter=BetfairMarketDataFilter(
            ladderLevels=3,  # WARNING! Ladder levels are fixed to 3 atm !!
            fields=[
                "EX_MARKET_DEF",
                "EX_BEST_OFFERS",
                "EX_LTP",
                "EX_BEST_OFFERS_DISP",
                "EX_ALL_OFFERS",
            ],
        ),
    )

    order_subscription = BetfairOrderSubscriptionMessage(id=2, op=OP.orderSubscription.value)

    return [market_subscription, order_subscription]


def get_app_key_session_token():
    username, password, app_key, cert_path = (
        os.environ["USERNAME"],
        os.environ["PASSWORD"],
        os.environ["APP_KEY"],
        os.environ["CERT_PATH"],
    )

    cert_path = os.path.abspath(cert_path)

    trading: APIClient = APIClient(
        username, password, app_key, certs=cert_path, locale=os.environ["LOCALE"]
    )
    trading.login()

    return trading.app_key, trading.session_token


app_key, session_token = get_app_key_session_token()

connection_pool = BetfairConnectionPool.create_connection_pool(
    subscription_messages=create_subscriptions(), session_token=session_token, app_key=app_key,
)

market_cache = MarketCache()
order_cache = OrderCache()

for update in connection_pool.read():
    update = orjson.loads(update)

    market_updates = market_cache(update)
    order_updates = order_cache(update)

    for market_book in market_updates:
        print(
            market_book.market_id,
            market_book.market_definition["runners"][0]["id"],
            market_book.market_definition["runners"][0]["sortPriority"],
            round(time.time() - market_cache.publish_time / 1000, 2),
            market_book.best_display[0, 0, 0, :],
        )

    for order in order_updates:
        print(order)

```


## Benchmark
```Benchmark
Setup: Two processes, one sending betfair stream messages , one receiving.

Hardware: I7 8550U, 16GB ram

Results: 
 * Using a market cache it can read around 25k messages/second
 * Without market cache >> 100 Mb/s

```

       
