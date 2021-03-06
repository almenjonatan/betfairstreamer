from __future__ import annotations

from typing import Dict, List

import attr

from betfairstreamer.models.betfair_api import BetfairMarketChangeMessage
from betfairstreamer.models.market_book import MarketBook


@attr.s(auto_attribs=True, slots=True)
class MarketCache:
    market_books: Dict[str, MarketBook] = attr.Factory(dict)
    publish_time: int = 0

    def update(self, stream_update: BetfairMarketChangeMessage) -> List[MarketBook]:

        if "pt" not in stream_update:
            return []

        updated_market_books = []

        self.publish_time = stream_update["pt"]

        for market_update in stream_update.get("mc", []):

            if market_update.get("img"):
                market_book = MarketBook.create_new_market_book(market_update)
                self.market_books[market_book.market_id] = market_book
            else:
                market_book = self.market_books[market_update["id"]]
                market_book.update(market_update)

            updated_market_books.append(market_book)

        return updated_market_books

    def serialise(self) -> BetfairMarketChangeMessage:

        return BetfairMarketChangeMessage(
            op="mcm",
            pt=self.publish_time,
            mc=[market_book.serialise() for market_id, market_book in self.market_books.items()],
        )

    def __call__(self, stream_update: BetfairMarketChangeMessage) -> List[MarketBook]:

        if "pt" not in stream_update:
            return []

        return self.update(stream_update)
