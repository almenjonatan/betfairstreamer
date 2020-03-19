## Usage

### Subscribe and read from single market stream.

```python
market_stream = BetfairConnection.create_connection(
    subscription_message, session_token=session_token, app_key=app_key
)

while True:
    update: =  market_stream.read() # List[bytes]
    print(update)
```

### Subscribe to multiple streams (order, market), using network polling

```python

order_connection = BetfairConnection.create_connection(
    order_subscription_message, session_token=session_token, app_key=app_key
)

market_connection = BetfairConnection.create_connection(
    market_subscription_message, session_token=session_token, app_key=app_key
)

connection_pool = BetfairConnectionPool()
connection_pool.add(order_connection)
connection_pool.add(market_connection)

while True:
    for update in connection_pool.read(): # Generator[List[bytes], None, None]  
        print(update)

```

### Create Subscriptions

Id field is submitted back to you by betfair on every change message. Used to differentiate streams or group together. Betfair do not check
for uniqueness.
```python
market_subscription_message = MarketSubscriptionMessage(
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
            Field.EX_BEST_OFFERS_DISP
        ]
    ),   
)

order_subscription =  OrderSubscriptionMessage(id=2)
```

### Session Token

```python
from betfairlightweight import APIClient

trading: APIClient = APIClient(username, password, app_key, certs=cert_path)
trading.login()

session_token = trading.session_token
```

### Imports

```python
from betfairlightweight import APIClient

from betfairstreamer.betfair.models import (
    OrderSubscriptionMessage,
    MarketFilter,
    MarketDataFilter,
    MarketSubscriptionMessage,
)
from betfairstreamer.cache.market_cache import MarketCache
from betfairstreamer.server import BetfairConnection, BetfairConnectionPool

```

### Using market cache.
Assuming you have received a list of stream updates into a list ( List[bytes] )
```python
import orjson

updates: List[bytes] = ...

market_cache = MarketCache()

for update in updates:
    decoded_update = orjson.loads(update)
    market_books: List[MarketBook] = market_cache(decoded_update)
```


### Marketbook

Each marketbook is backed by numpy arrays. This makes it easy to take slices and do vectorized calculations.

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

### Performance

#### Setup: Two processes (multiprocessing), one producer, one consumer. Hardware intel 4790K, 16Gb ram.

Read from socket > 100Mb/s  

Read from socket and using marketcache > 30k updates/s

