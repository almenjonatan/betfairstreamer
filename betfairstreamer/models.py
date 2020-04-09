from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import attr
import numpy as np
from betfairlightweight.resources.bettingresources import CurrentOrder

from betfairstreamer.betfair_api import (
    BetfairMarketChange,
    BetfairMarketDefinition,
    BetfairOrder,
    BetfairRunnerChange,
    OrderStatus,
    OrderType,
    PersistenceType,
    Side,
)
from betfairstreamer.definitions import BETFAIR_TICKS
from betfairstreamer.utils import localize_betfair_date, parse_utc_timestamp

FULL_PRICE_LADDER_INDEX = dict(zip(BETFAIR_TICKS, range(len(BETFAIR_TICKS))))


@attr.s(slots=True, auto_attribs=True)
class Order:
    market_id: str
    selection_id: int
    bet_id: str
    bsp_liability: float
    status: OrderStatus
    side: Side
    persistence_type: PersistenceType
    order_type: OrderType
    price: float
    regulator_code: str
    size: float
    placed_date: Optional[datetime]
    matched_date: Optional[datetime]
    lapsed_date: Optional[datetime]
    regulator_auth_code: Optional[str]
    lapse_status_reason_code: Optional[str]
    handicap: Optional[float]
    size_cancelled: float
    size_voided: float
    size_lapsed: float
    average_price_matched: float
    size_matched: float
    size_remaining: float
    customer_strategy_reference: Optional[str]
    customer_order_reference: Optional[str]

    @classmethod
    def from_stream(cls, market_id: str, selection_id: int, order: BetfairOrder) -> Order:
        return cls(
            market_id=market_id,
            selection_id=selection_id,
            side=Side[order["side"]],
            size_voided=order["sv"],
            persistence_type=PersistenceType[str(order.get("pt"))],
            order_type=OrderType[order["ot"]],
            lapse_status_reason_code=order.get("lsrc"),
            handicap=None,
            price=order["p"],
            size_cancelled=order["sc"],
            regulator_code=order["rc"],
            size=order["s"],
            placed_date=parse_utc_timestamp(order["pd"]),
            regulator_auth_code=order["rac"],
            matched_date=parse_utc_timestamp(order.get("md")),
            lapsed_date=parse_utc_timestamp(order.get("ld")),
            size_lapsed=order["sl"],
            average_price_matched=order.get("avp", 0),
            size_matched=order["sm"],
            bet_id=order["id"],
            bsp_liability=order.get("bsp", 0),
            customer_strategy_reference=order["rfs"],
            customer_order_reference=order["rfo"],
            status=OrderStatus[order["status"]],
            size_remaining=order["sr"],
        )

    @classmethod
    def from_betfairlightweight(cls, order: CurrentOrder) -> Order:
        return Order(
            bet_id=order.bet_id,
            market_id=order.market_id,
            selection_id=order.selection_id,
            handicap=order.handicap,
            price=order.price_size.price,
            size=order.price_size.size,
            side=Side[order.side],
            status=OrderStatus[order.status],
            persistence_type=PersistenceType[order.persistence_type],
            order_type=OrderType[order.order_type],
            bsp_liability=order.bsp_liability,
            placed_date=localize_betfair_date(order.placed_date),
            average_price_matched=order.average_price_matched,
            size_matched=order.size_matched,
            size_remaining=order.size_remaining,
            size_lapsed=order.size_lapsed,
            size_cancelled=order.size_cancelled,
            regulator_code=order.regulator_code,
            customer_order_reference=order.customer_order_ref,
            customer_strategy_reference=order.customer_strategy_ref,
            matched_date=localize_betfair_date(order.matched_date),
            lapse_status_reason_code=None,
            lapsed_date=None,
            regulator_auth_code=None,
            size_voided=order.size_voided,
        )

    def serialize(self) -> Dict[Any, Any]:
        out = {}
        for k, v in attr.asdict(self).items():

            if isinstance(v, Enum):
                v = v.value

            if isinstance(v, datetime):
                v = v.isoformat()

            camel_case_key = [word.title() for word in k.split("_")]
            camel_case_key[0] = camel_case_key[0].lower()
            out["".join(camel_case_key)] = v

        return out


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

    def update_runners(self, runner_change: List[BetfairRunnerChange]) -> None:
        for r in runner_change:
            sort_priority = int(self.sort_priority_mapping[r["id"]] - 1)

            bdatb = r.get("bdatb", [])
            bdatl = r.get("bdatl", [])

            batb = r.get("batb", [])
            batl = r.get("batl", [])

            atb = r.get("atb", [])
            atl = r.get("atl", [])

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
                indexes = [FULL_PRICE_LADDER_INDEX[u[0]] for u in atb]
                self.full_price_ladder[sort_priority, 0, indexes, :] = np.array(atb)

            if atl:
                indexes = [FULL_PRICE_LADDER_INDEX[u[0]] for u in atl]
                self.full_price_ladder[sort_priority, 1, indexes, :] = np.array(atl)

            if "ltp" in r:
                self.metadata[sort_priority, 0] = r.get("ltp")
            if "tv" in r:
                self.metadata[sort_priority, 1] = r.get("tv")

    def update(self, market_change_message: BetfairMarketChange) -> None:

        if market_change_message.get("marketDefinition"):
            self.market_definition = market_change_message["marketDefinition"]

        self.update_runners(market_change_message.get("rc", []))

    @classmethod
    def create_new_market_book(cls, market_change_message: BetfairMarketChange) -> MarketBook:

        number_of_runners = len(market_change_message["marketDefinition"]["runners"])

        market_book = cls(
            market_id=market_change_message["id"],
            best_display=-1 * np.ones(shape=(number_of_runners, 2, 3, 2)),
            best_offers=-1 * np.ones(shape=(number_of_runners, 2, 3, 2)),
            full_price_ladder=-1 * np.ones(shape=(number_of_runners, 2, 350, 2)),
            metadata=np.zeros(shape=(number_of_runners, 2)),
            sort_priority_mapping=create_sort_priority_mapping(
                market_change_message["marketDefinition"]
            ),
            market_definition=market_change_message["marketDefinition"],
        )

        return market_book
