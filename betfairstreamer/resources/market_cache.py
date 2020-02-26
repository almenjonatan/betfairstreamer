from typing import Dict, List

import attr
import orjson

from betfairstreamer.resources.market_book import MarketBook


@attr.s
class MarketCache:

    market_books = attr.ib(type=Dict[str, MarketBook], factory=dict)
    publish_time = attr.ib(type=int, default=0)

    def update(self, stream_update) -> List[MarketBook]:

        updated_market_books = []

        self.publish_time = stream_update["pt"]

        for market_update in stream_update.get("mc", []):

            if market_book := self.market_books.get(market_update["id"]):
                if market_book is not None:
                    market_book.update(market_update)
                    updated_market_books.append(market_book)
            else:
                market_book = MarketBook.from_betfair_dict(market_update)

                assert market_book is not None

                self.market_books[market_book.market_id] = market_book
                updated_market_books.append(market_book)

        return updated_market_books

    def __call__(self, stream_update) -> List[MarketBook]:

        if stream_update.get("op", "") == "mcm":
            return self.update(stream_update)

        return []

    def __len__(self):
        return len(self.market_books)
