from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

import attr

from betfairstreamer.models.betfair_api import (
    BetfairOrder,
    CurrentOrderSummary,
    OrderStatus,
    OrderType,
    PersistenceType,
    Side,
)
from betfairstreamer.models.betfair_api_extensions import CurrentOrderSummaryRecord
from betfairstreamer.utils import parse_betfair_date, parse_utc_timestamp


def default_str(s: Optional[str]) -> str:
    if s is None:
        return ""

    return s


def default_float(v: Optional[float]) -> float:
    if v is None:
        return 0.0

    return v


@attr.s(slots=True, auto_attribs=True)
class Order:
    bet_id: str
    market_id: str
    selection_id: int

    bsp_liability: float
    status: OrderStatus
    side: Side
    persistence_type: PersistenceType
    order_type: OrderType
    price: float
    size: float

    placed_date: datetime
    matched_date: Optional[datetime]
    lapsed_date: Optional[datetime]

    handicap: float = attr.ib(converter=default_float)

    regulator_code: str = attr.ib(converter=default_str)
    regulator_auth_code: str = attr.ib(converter=default_str)
    lapse_status_reason_code: str = attr.ib(converter=default_str)

    size_cancelled: float = attr.ib(converter=default_float)
    size_voided: float = attr.ib(converter=default_float)
    size_lapsed: float = attr.ib(converter=default_float)

    size_matched: float = attr.ib(converter=default_float)
    size_remaining: float = attr.ib(converter=default_float)
    customer_strategy_reference: str = attr.ib(converter=default_str)
    customer_order_reference: str = attr.ib(converter=default_str)
    average_price_matched: float = attr.ib(converter=default_float)

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
            handicap=0,
            price=order["p"],
            size_cancelled=order["sc"],
            regulator_code=order["rc"],
            size=order["s"],
            placed_date=parse_utc_timestamp(order["pd"]),
            regulator_auth_code=order["rac"],
            matched_date=parse_utc_timestamp(order.get("md")),
            lapsed_date=parse_utc_timestamp(order.get("ld")),
            size_lapsed=order["sl"],
            average_price_matched=order.get("avp"),
            size_matched=order["sm"],
            bet_id=order["id"],
            bsp_liability=order.get("bsp", 0),
            customer_strategy_reference=order["rfs"],
            customer_order_reference=order["rfo"],
            status=OrderStatus[order["status"]],
            size_remaining=order["sr"],
        )

    @classmethod
    def from_api_ng(cls, order: CurrentOrderSummary) -> Order:

        return cls(
            bet_id=order["betId"],
            market_id=order["marketId"],
            selection_id=order["selectionId"],
            handicap=order.get("handicap", 0),
            price=order["priceSize"]["price"],
            size=order["priceSize"]["size"],
            bsp_liability=order.get("bspLiability", 0),
            side=Side[order["side"]],
            status=OrderStatus[order["status"]],
            persistence_type=PersistenceType[order["persistenceType"]],
            order_type=OrderType[order["orderType"]],
            placed_date=parse_betfair_date(order["placedDate"]),
            matched_date=parse_betfair_date(order.get("matchedDate")),
            average_price_matched=order.get("averagePriceMatched"),
            size_matched=order["sizeMatched"],
            size_remaining=order["sizeRemaining"],
            size_lapsed=order["sizeLapsed"],
            size_cancelled=order["sizeCancelled"],
            size_voided=order["sizeVoided"],
            regulator_auth_code=order.get("regulatorAuthCode"),
            regulator_code=order.get("regulatorCode"),
            customer_order_reference=order.get("customerOrderRef"),
            customer_strategy_reference=order.get("customerStrategyRef"),
            lapsed_date=None,
            lapse_status_reason_code="",
        )

    @classmethod
    def from_record(cls, order: CurrentOrderSummaryRecord) -> Order:
        return cls(
            bet_id=order["betId"],
            market_id=order["marketId"],
            selection_id=order["selectionId"],
            handicap=order.get("handicap", 0),
            price=order["price"],
            size=order["size"],
            bsp_liability=order.get("bspLiability", 0),
            side=Side[order["side"]],
            status=OrderStatus[order["status"]],
            persistence_type=PersistenceType[order["persistenceType"]],
            order_type=OrderType[order["orderType"]],
            placed_date=parse_betfair_date(order["placedDate"]),
            matched_date=parse_betfair_date(order.get("matchedDate")),
            average_price_matched=order.get("averagePriceMatched"),
            size_matched=order["sizeMatched"],
            size_remaining=order["sizeRemaining"],
            size_lapsed=order["sizeLapsed"],
            size_cancelled=order["sizeCancelled"],
            size_voided=order["sizeVoided"],
            regulator_auth_code=order.get("regulatorAuthCode"),
            regulator_code=order.get("regulatorCode"),
            customer_order_reference=order.get("customerOrderRef"),
            customer_strategy_reference=order.get("customerStrategyRef"),
            lapsed_date=None,
            lapse_status_reason_code="",
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
