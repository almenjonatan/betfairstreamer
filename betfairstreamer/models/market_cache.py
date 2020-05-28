from typing import Callable, Dict, List

import attr

from betfairstreamer.models.betfair_api import BetfairMarketChange, BetfairMarketChangeMessage
from betfairstreamer.models.market_book import MarketBook


def market_book_producer(market_update: BetfairMarketChange) -> MarketBook:
    return MarketBook.create_new_market_book(market_update)


@attr.s(auto_attribs=True, slots=True)
class MarketCache:
    market_books: Dict[str, MarketBook] = attr.Factory(dict)
    publish_time: int = 0
    market_book_factory: Callable[[BetfairMarketChange], MarketBook] = market_book_producer

    def update(self, stream_update: BetfairMarketChangeMessage) -> List[MarketBook]:

        updated_market_books = []

        self.publish_time = stream_update["pt"]

        for market_update in stream_update.get("mc", []):

            market_book = self.market_books.get(market_update["id"])

            if market_book is None:
                market_book = self.market_book_factory(market_update)
                self.market_books[market_book.market_id] = market_book

            market_book.update(market_update)

            updated_market_books.append(market_book)

        return updated_market_books

    def __call__(self, stream_update: BetfairMarketChangeMessage) -> List[MarketBook]:

        if "pt" not in stream_update:
            return []

        return self.update(stream_update)
