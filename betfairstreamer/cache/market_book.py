from __future__ import annotations

from typing import Dict, List

import attr
import numpy as np

from betfairstreamer.betfair.definitions import MarketChangeDict, RunnerChangeDict
from betfairstreamer.betfair.models import MarketDefinition


@attr.s(slots=True)
class RunnerBook:
    metadata = attr.ib(type=np.array)
    sort_priority_mapping = attr.ib(type=Dict[int, int])
    best_display = attr.ib(type=np.array, default=None)
    best_offers = attr.ib(type=np.array, default=None)

    def update(self, runner_change: List[RunnerChangeDict]) -> None:

        for r in runner_change:
            sort_priority = self.sort_priority_mapping[r["id"]] - 1

            bdatb = r.get("bdatb", [])
            bdatl = r.get("bdatl", [])

            batb = r.get("batb", [])
            batl = r.get("batl", [])

            if bdatb:
                new_values = np.array(bdatb)
                bdatb_index = new_values[:, 0].astype(int)
                self.best_display[sort_priority, 0, bdatb_index, :] = new_values[:, 1:]

            if bdatl:
                new_values = np.array(bdatl)
                bdatl_index = new_values[:, 0].astype(int)
                self.best_display[sort_priority, 1, bdatl_index, :] = new_values[:, 1:]

            if batb:
                new_values = np.array(batb)
                batb_index = new_values[:, 0].astype(int)
                self.best_offers[sort_priority, 0, batb_index, :] = new_values[:, 1:]

            if batl:
                new_values = np.array(batl)
                batl_index = new_values[:, 0].astype(int)
                self.best_offers[sort_priority, 1, batl_index, :] = new_values[:, 1:]

            self.metadata[sort_priority][:] = [r.get("ltp", 0), r.get("tv", 0)]

    @classmethod
    def from_betfair(cls, market_definition: MarketDefinition) -> RunnerBook:

        number_of_runners = len(market_definition.runners)

        best_display = -1 * np.ones(shape=(number_of_runners, 2, 3, 2))
        best_offers = -1 * np.ones(shape=(number_of_runners, 2, 3, 2))

        metadata = np.zeros(shape=(number_of_runners, 2))

        sort_priority_mapping = {r.id: r.sort_priority for r in market_definition.runners}

        return cls(
            best_display=best_display,
            best_offers=best_offers,
            metadata=metadata,
            sort_priority_mapping=sort_priority_mapping,
        )


@attr.s(slots=True)
class MarketBook:

    market_id = attr.ib(type=str)
    market_definition = attr.ib(type=MarketDefinition)
    runner_book = attr.ib(type=RunnerBook)

    def update(self, market_book: MarketChangeDict) -> None:

        if market_book.get("marketDefinition") is not None:
            self.market_definition = MarketDefinition.from_betfair(market_book["marketDefinition"])

        if market_book.get("img", False):
            self.runner_book = RunnerBook.from_betfair(self.market_definition)

        self.runner_book.update(market_book.get("rc", []))

    @classmethod
    def from_betfair(cls, market_book: MarketChangeDict) -> MarketBook:

        market_definition = MarketDefinition.from_betfair(market_book["marketDefinition"])
        runner_book = RunnerBook.from_betfair(market_definition)

        return cls(
            market_id=market_book["id"],
            market_definition=market_definition,
            runner_book=runner_book,
        )
