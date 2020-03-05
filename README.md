## Usage

The following creates a connection to betfair and returns the raw messages

```python
from betfairstreamer.server import BetfairConnection
from betfairstreamer.resources.api_messages import (
    Field,
    MarketDataFilter,
    MarketFilter,
    MarketSubscriptionMessage,
)

# Create and  authenticate a connection to Betfair
connection = BetfairConnection.create_connection()

market_filter = MarketFilter(event_type_ids=[7], country_codes=["GB"])

market_data_filter = MarketDataFilter(
    fields=[Field.EX_MARKET_DEF, Field.EX_BEST_OFFERS_DISP]
)

market_subscription = MarketSubscriptionMessage(
    market_filter=market_filter, market_data_filter=market_data_filter
)

c.send(market_subscription)


# Start reading messages from the stream.
while True:
    for stream_update in c.receive():
        print(m)
```