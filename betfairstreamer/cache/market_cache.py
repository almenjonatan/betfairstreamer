from typing import Dict, List

import attr

from betfairstreamer.betfair.definitions import MarketChangeMessageDict
from betfairstreamer.betfair.models import MarketBook


@attr.s
class MarketCache:

    market_books = attr.ib(type=Dict[str, MarketBook], factory=dict)
    publish_time = attr.ib(type=int, default=0)

    def update(self, stream_update: MarketChangeMessageDict) -> List[MarketBook]:

        updated_market_books = []

        self.publish_time = stream_update["pt"]

        for market_update in stream_update.get("mc", []):
            market_book = self.market_books.get(market_update["id"])

            if not market_book:
                market_book = MarketBook.from_betfair(market_update)
                self.market_books[market_book.market_id] = market_book

            market_book.update(market_update)

            updated_market_books.append(market_book)

        return updated_market_books

    def __call__(self, stream_update: MarketChangeMessageDict) -> List[MarketBook]:

        if stream_update.get("op", "") == "mcm":
            return self.update(stream_update)

        return []
