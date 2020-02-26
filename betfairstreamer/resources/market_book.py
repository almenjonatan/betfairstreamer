import enum
from datetime import datetime
from enum import auto
from typing import Dict, List

import attr
import numpy as np

from betfairstreamer.utils import parse_betfair_date
from betfairstreamer.resources.api_messages import MarketDefinition, RunnerDefinition


@attr.s
class RunnerBook:
    price_sizes = attr.ib(type=np.array)
    metadata = attr.ib(type=np.array)
    runner_definitions = attr.ib(type=List[RunnerDefinition])
    sort_priority_mapping = attr.ib(type=Dict[int, int])

    def update(self, runner_change: List[Dict]):
        for r in runner_change:
            batb = r.get("bdatb", {})
            batl = r.get("bdatl", {})

            sort_priority = self.sort_priority_mapping[r["id"]]

            if batb:
                new_values = np.array(batb)
                batb_index = new_values[:, 0].astype(int)
                self.price_sizes[sort_priority - 1, 0, batb_index, :] = new_values[
                    :, 1:
                ]

            if batl:
                new_values = np.array(batl)
                batl_index = new_values[:, 0].astype(int)

                self.price_sizes[sort_priority - 1, 1, batl_index, :] = new_values[
                    :, 1:
                ]

            if "ltp" in r:
                self.metadata[sort_priority - 1] = r["ltp"]

    @classmethod
    def create_instance(
        cls, runner_definitions: List[RunnerDefinition], runner_changes: List
    ):
        price_sizes = -1 * np.ones(shape=(len(runner_definitions), 2, 3, 2))
        metadata = np.zeros(shape=(len(runner_definitions)))
        sort_priority_mapping = {r.id: r.sort_priority for r in runner_definitions}

        runner_book = cls(
            price_sizes=price_sizes,
            metadata=metadata,
            runner_definitions=runner_definitions,
            sort_priority_mapping=sort_priority_mapping,
        )

        runner_book.update(runner_changes)

        return runner_book


@attr.s(slots=True, weakref_slot=False)
class MarketBook:

    market_id = attr.ib(type=str)
    market_definition = attr.ib(type=MarketDefinition)
    runner_book = attr.ib(type=RunnerBook, default=None)

    def update(self, market_update):

        if "marketDefinition" in market_update:
            self.market_definition = MarketDefinition.from_betfair_dict(
                market_update["marketDefinition"]
            )

        if market_update.get("img", False):
            self.runner_book = None

        if self.runner_book is None:
            self.runner_book = RunnerBook.create_instance(
                self.market_definition.runners, market_update.get("rc", [])
            )

        self.runner_book.update(market_update.get("rc", []))

    @classmethod
    def from_betfair_dict(cls, betfair_dict):
        assert "marketDefinition" in betfair_dict, "MarketDefinition must be present!"

        market_definition = MarketDefinition.from_betfair_dict(
            betfair_dict["marketDefinition"]
        )

        return cls(
            market_id=betfair_dict["id"],
            market_definition=market_definition,
            runner_book=RunnerBook.create_instance(
                runner_definitions=market_definition.runners,
                runner_changes=betfair_dict.get("rc", []),
            ),
        )
