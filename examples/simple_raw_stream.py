import json

import orjson

from betfairstreamer.resources.api_messages import (OP, AuthenticationMessage,
                                                    Field, MarketDataFilter,
                                                    MarketFilter,
                                                    MarketSubscriptionMessage)
from betfairstreamer.resources.market_cache import MarketCache
from betfairstreamer.server import BetfairConnection

c = BetfairConnection.create_connection("market_stream")

market_filter = MarketFilter(event_type_ids=[7], country_codes=["GB"])

market_data_filter = MarketDataFilter(
    fields=[Field.EX_MARKET_DEF, Field.EX_BEST_OFFERS_DISP, Field.EX_MARKET_DEF]
)

market_subscription = MarketSubscriptionMessage(
    market_filter=market_filter, market_data_filter=market_data_filter
)

c.send(market_subscription)

print(c.recieve())
mc = MarketCache()

while True:
    for m in c.recieve():
        for r in mc(orjson.loads(m)):
            print(r.market_id, r.runner_book.price_sizes[0, 0, 0, :])
