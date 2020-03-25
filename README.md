## Installation

```
pip install betfairstreamer
```
## Usage

### Subscribe to multiple streams (order, market)

```python
import os

from betfairlightweight import APIClient

from betfairstreamer.betfair.models import (
    OrderSubscriptionMessage,
    MarketFilter,
    MarketDataFilter,
    MarketSubscriptionMessage,
)

from betfairstreamer.betfair.enums import Field

from betfairstreamer.cache.market_cache import MarketCache

from betfairstreamer.server import (
    BetfairConnection, 
    BetfairConnectionPool
)

username, password, app_key, cert_path = (os.environ["USERNAME"], 
                                          os.environ["PASSWORD"], 
                                          os.environ["APP_KEY"], 
                                          os.environ["CERT_PATH"],
                                         )

cert_path = os.path.abspath(cert_path)

trading: APIClient = APIClient(username, password, app_key, certs=cert_path, locale=os.environ["LOCALE"])
trading.login()

session_token = trading.session_token

market_subscription = MarketSubscriptionMessage(
    id=1,
    market_filter=MarketFilter(
        country_codes=["GB"], 
        event_type_ids=["1"], 
        market_types=["MATCH_ODDS"]
    ),
    market_data_filter=MarketDataFilter(
        ladder_levels=3,                        # WARNING! Ladder levels are fixed to 3 atm !!
        fields=[
            Field.EX_MARKET_DEF,
            Field.EX_BEST_OFFERS,
            Field.EX_LTP,
            Field.EX_BEST_OFFERS_DISP
        ]
    ),   
)

order_subscription =  OrderSubscriptionMessage(id=2)

connection_pool = BetfairConnectionPool.create_connection_pool(
    subscription_messages=[market_subscription, order_subscription],
    session_token=trading.session_token,
    app_key=trading.app_key
)

try:
    while True:
        for update in connection_pool.read():  
            print(update)
except Exception:
    pass
finally:
    # "Must" be done if running within a jupyter notebook, else connections will be kept open.
    connection_pool.close()
```

### Market cache

```python
market_cache = MarketCache()

while True:
    for update in connection_pool.read():  
        decoded_update = orjson.loads(update)
        market_books: List[MarketBook] = market_cache(decoded_update)
```

### Order cache

```python
# If we do not care about completed orders.
order_cache = OrderCache()

# If we want to get our completed order (EXECUTION_COMPLETE) we have have to fetch them from
# betfair rest api. 
trading # type: APIClient

current_orders = trading.betting.list_current_orders()

order_cache = OrderCache.from_betfair(current_orders)  
```


### Marketbook

Each marketbook is backed by numpy arrays..

The array contains four axes. [SORT_PRIORITY, SIDE (Back/Lay), LADDER_LEVEL, PRICE/SIZE]

```python
market_book: MarketBook

##  best_offers is populated if you are using Field.EX_BEST_OFFERS

### Access price on first selection on side back and on first ladder level
market_book.runner_book.best_offers[0, 0, 0, 0] # scalar value

### Access price and size on second selection side lay,  first ladder level
market_book.runner_book.best_offers[1, 1, 0, :] # np.shape(...) == (2,)

##  using Field.Field.EX_BEST_OFFERS_DISP, populate best_display (virtualised prices/ what betfair homepage display) 

market_book.runner_book.best_display[0, 0, 0, 0] # scalar value
market_book.runner_book.best_display[1, 1, 0, :] # np.shape(...) == (2,)
```
For more information checkout numpy slicing.

### Historical Data
market_cache and order_cache takes a single (dict) update and updates it respective cache and returns the market_books that were supplied in the update.

```python
f = open("stream_data_file", "r")

stream_updates = f.readlines()

for stream_update in stream_updates:
    market_books = market_cache(stream_update)
    order_books = order_cache(stream_udpate)
```



### Benchmark

#### Setup: Two processes (multiprocessing), one producer, one consumer. Hardware intel 8550U, 16Gb ram.

Read from socket > 100Mb/s  

Read from socket and using marketcache > 30k updates/s

