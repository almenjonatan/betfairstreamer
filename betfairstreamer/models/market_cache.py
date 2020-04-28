from typing import Dict, List

import attr

from betfairstreamer.models.betfair_api import BetfairMarketChangeMessage
from betfairstreamer.models.market_book import MarketBook


@attr.s(auto_attribs=True, slots=True)
class MarketCache:
    market_books: Dict[str, MarketBook] = attr.Factory(dict)
    publish_time: int = 0

    def update(self, stream_update: BetfairMarketChangeMessage) -> List[MarketBook]:

        updated_market_books = []

        if "pt" not in stream_update:
            return []

        self.publish_time = stream_update["pt"]

        for market_update in stream_update.get("mc", []):

            market_book = self.market_books.get(market_update["id"])

            if market_book is None or market_update.get("img", False):
                market_book = MarketBook.create_new_market_book(market_update)
                self.market_books[market_book.market_id] = market_book

            market_book.update_runners(market_update.get("rc", []))
            updated_market_books.append(market_book)

        return updated_market_books

    def __call__(self, stream_update: BetfairMarketChangeMessage) -> List[MarketBook]:
        return self.update(stream_update)
