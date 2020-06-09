from __future__ import annotations

from typing import Dict, List

import attr
import numpy as np

from betfairstreamer.models.betfair_api import BetfairMarketChange, BetfairMarketDefinition, BetfairRunnerChange

BETFAIR_TICKS = [
    1.01,
    1.02,
    1.03,
    1.04,
    1.05,
    1.06,
    1.07,
    1.08,
    1.09,
    1.1,
    1.11,
    1.12,
    1.13,
    1.14,
    1.15,
    1.16,
    1.17,
    1.18,
    1.19,
    1.2,
    1.21,
    1.22,
    1.23,
    1.24,
    1.25,
    1.26,
    1.27,
    1.28,
    1.29,
    1.3,
    1.31,
    1.32,
    1.33,
    1.34,
    1.35,
    1.36,
    1.37,
    1.38,
    1.39,
    1.4,
    1.41,
    1.42,
    1.43,
    1.44,
    1.45,
    1.46,
    1.47,
    1.48,
    1.49,
    1.5,
    1.51,
    1.52,
    1.53,
    1.54,
    1.55,
    1.56,
    1.57,
    1.58,
    1.59,
    1.6,
    1.61,
    1.62,
    1.63,
    1.64,
    1.65,
    1.66,
    1.67,
    1.68,
    1.69,
    1.7,
    1.71,
    1.72,
    1.73,
    1.74,
    1.75,
    1.76,
    1.77,
    1.78,
    1.79,
    1.8,
    1.81,
    1.82,
    1.83,
    1.84,
    1.85,
    1.86,
    1.87,
    1.88,
    1.89,
    1.9,
    1.91,
    1.92,
    1.93,
    1.94,
    1.95,
    1.96,
    1.97,
    1.98,
    1.99,
    2,
    2.02,
    2.04,
    2.06,
    2.08,
    2.1,
    2.12,
    2.14,
    2.16,
    2.18,
    2.2,
    2.22,
    2.24,
    2.26,
    2.28,
    2.3,
    2.32,
    2.34,
    2.36,
    2.38,
    2.4,
    2.42,
    2.44,
    2.46,
    2.48,
    2.5,
    2.52,
    2.54,
    2.56,
    2.58,
    2.6,
    2.62,
    2.64,
    2.66,
    2.68,
    2.7,
    2.72,
    2.74,
    2.76,
    2.78,
    2.8,
    2.82,
    2.84,
    2.86,
    2.88,
    2.9,
    2.92,
    2.94,
    2.96,
    2.98,
    3,
    3.05,
    3.1,
    3.15,
    3.2,
    3.25,
    3.3,
    3.35,
    3.4,
    3.45,
    3.5,
    3.55,
    3.6,
    3.65,
    3.7,
    3.75,
    3.8,
    3.85,
    3.9,
    3.95,
    4,
    4.1,
    4.2,
    4.3,
    4.4,
    4.5,
    4.6,
    4.7,
    4.8,
    4.9,
    5,
    5.1,
    5.2,
    5.3,
    5.4,
    5.5,
    5.6,
    5.7,
    5.8,
    5.9,
    6,
    6.2,
    6.4,
    6.6,
    6.8,
    7,
    7.2,
    7.4,
    7.6,
    7.8,
    8,
    8.2,
    8.4,
    8.6,
    8.8,
    9,
    9.2,
    9.4,
    9.6,
    9.8,
    10,
    10.5,
    11,
    11.5,
    12,
    12.5,
    13,
    13.5,
    14,
    14.5,
    15,
    15.5,
    16,
    16.5,
    17,
    17.5,
    18,
    18.5,
    19,
    19.5,
    20,
    21,
    22,
    23,
    24,
    25,
    26,
    27,
    28,
    29,
    30,
    32,
    34,
    36,
    38,
    40,
    42,
    44,
    46,
    48,
    50,
    55,
    60,
    65,
    70,
    75,
    80,
    85,
    90,
    95,
    100,
    110,
    120,
    130,
    140,
    150,
    160,
    170,
    180,
    190,
    200,
    210,
    220,
    230,
    240,
    250,
    260,
    270,
    280,
    290,
    300,
    310,
    320,
    330,
    340,
    350,
    360,
    370,
    380,
    390,
    400,
    410,
    420,
    430,
    440,
    450,
    460,
    470,
    480,
    490,
    500,
    510,
    520,
    530,
    540,
    550,
    560,
    570,
    580,
    590,
    600,
    610,
    620,
    630,
    640,
    650,
    660,
    670,
    680,
    690,
    700,
    710,
    720,
    730,
    740,
    750,
    760,
    770,
    780,
    790,
    800,
    810,
    820,
    830,
    840,
    850,
    860,
    870,
    880,
    890,
    900,
    910,
    920,
    930,
    940,
    950,
    960,
    970,
    980,
    990,
    1000,
]

FULL_PRICE_LADDER_INDEX = dict(zip(BETFAIR_TICKS, range(len(BETFAIR_TICKS))))


def create_sort_priority_mapping(market_definition: BetfairMarketDefinition) -> Dict[int, int]:
    return {r["id"]: r["sortPriority"] for r in market_definition["runners"]}


@attr.s(slots=True, auto_attribs=True)
class MarketBook:
    market_id: str
    market_definition: BetfairMarketDefinition
    metadata: np.ndarray
    sort_priority_mapping: Dict[int, int]
    best_display: np.ndarray
    best_offers: np.ndarray
    full_price_ladder: np.ndarray
    trd: np.ndarray

    def update_runners(self, runner_change: List[BetfairRunnerChange]) -> None:
        for r in runner_change:
            sort_priority = int(self.sort_priority_mapping[r["id"]] - 1)

            bdatb = r.get("bdatb", [])
            bdatl = r.get("bdatl", [])

            batb = r.get("batb", [])
            batl = r.get("batl", [])

            atl = r.get("atl", [])
            atb = r.get("atb", [])

            trd = r.get("trd", [])

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

            if atb:
                for u in atb:
                    if u[1] == 0:
                        self.full_price_ladder[sort_priority, 0, FULL_PRICE_LADDER_INDEX[u[0]], :] = 0
                    else:
                        self.full_price_ladder[sort_priority, 0, FULL_PRICE_LADDER_INDEX[u[0]], :] = u

            if atl:
                for u in atl:
                    if u[1] == 0:
                        self.full_price_ladder[sort_priority, 1, FULL_PRICE_LADDER_INDEX[u[0]], :] = 0
                    else:
                        self.full_price_ladder[sort_priority, 1, FULL_PRICE_LADDER_INDEX[u[0]], :] = u

            if trd:
                for u in trd:
                    self.trd[sort_priority, FULL_PRICE_LADDER_INDEX[u[0]], :] = u

            if "ltp" in r:
                self.metadata[sort_priority, 0] = r.get("ltp")
            if "tv" in r:
                self.metadata[sort_priority, 1] = r.get("tv")

    def update(self, market_change_message: BetfairMarketChange) -> None:

        market_definition = market_change_message.get("marketDefinition")

        if market_definition is not None:
            old_sort_priority_mapping = self.sort_priority_mapping.copy()
            new_sort_priority_mapping = create_sort_priority_mapping(market_definition)

            k = [old_sort_priority_mapping[k] - 1 for k in new_sort_priority_mapping]
            i = [v - 1 for v in new_sort_priority_mapping.values()]

            if i != k:
                self.full_price_ladder[i] = self.full_price_ladder[k]
                self.best_display[i] = self.best_display[k]
                self.best_offers[i] = self.best_offers[k]

            self.market_definition = market_change_message["marketDefinition"]

            self.sort_priority_mapping = new_sort_priority_mapping

        self.update_runners(market_change_message.get("rc", []))

    @classmethod
    def create_new_market_book(cls, market_change_message: BetfairMarketChange) -> MarketBook:

        number_of_runners = len(market_change_message["marketDefinition"]["runners"])

        ladder_levels = 10

        market_book = cls(
            market_id=market_change_message["id"],
            best_display=np.zeros(shape=(number_of_runners, 2, ladder_levels, 2)),
            best_offers=np.zeros(shape=(number_of_runners, 2, ladder_levels, 2)),
            full_price_ladder=np.zeros(shape=(number_of_runners, 2, 350, 2)),
            metadata=np.zeros(shape=(number_of_runners, 2)),
            sort_priority_mapping=create_sort_priority_mapping(market_change_message["marketDefinition"]),
            market_definition=market_change_message["marketDefinition"],
            trd=np.zeros(shape=(number_of_runners, 350, 2)),
        )

        return market_book
