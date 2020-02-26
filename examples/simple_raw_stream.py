from betfairstreamer.server import BetfairConnection
from betfairstreamer.resources.api_messages import (
    AuthenticationMessage,
    Field,
    MarketDataFilter,
    MarketFilter,
    MarketSubscriptionMessage,
    OP,
)
from betfairstreamer.resources.market_cache import MarketCache
import orjson
import json


c = BetfairConnection.create_connection("market_stream")

market_filter = MarketFilter(event_type_ids=[7], country_codes=["GB"])

market_data_filter = MarketDataFilter(
    fields=[Field.EX_MARKET_DEF, Field.EX_BEST_OFFERS_DISP, Field.EX_MARKET_DEF]
)

market_subscription = MarketSubscriptionMessage(
    market_filter=market_filter, market_data_filter=market_data_filter
)

print(json.dumps(market_subscription.to_dict()))

c.send(market_subscription.to_dict())

print(c.recieve())
mc = MarketCache()

while True:
    for m in c.recieve():
        for r in mc(orjson.loads(m)):
            print(r.market_id, r.runner_book.price_sizes[0, 0, 0, :])
