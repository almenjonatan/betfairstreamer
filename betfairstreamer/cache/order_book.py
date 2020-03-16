from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

import attr
from betfairlightweight.resources.bettingresources import CurrentOrder as BetfairLightweightOrder

from betfairstreamer.betfair.definitions import OrderDict
from betfairstreamer.betfair.enums import OrderStatus, OrderType, PersistenceType, Side
from betfairstreamer.utils import localize_betfair_date, parse_utc_timestamp


@attr.s(slots=True)
class Order:
    market_id = attr.ib(type=str)
    selection_id = attr.ib(type=int)
    bet_id = attr.ib(type=str)
    bsp_liability = attr.ib(type=float)
    status = attr.ib(type=OrderStatus)
    side = attr.ib(type=Side)
    persistence_type = attr.ib(type=PersistenceType)
    order_type = attr.ib(type=OrderType)
    price = attr.ib(type=float)
    regulator_code = attr.ib(type=str)
    size = attr.ib(type=float)
    placed_date = attr.ib(type=Optional[datetime])
    matched_date = attr.ib(type=Optional[datetime], default=None)
    lapsed_date = attr.ib(type=Optional[datetime], default=None)
    regulator_auth_code = attr.ib(type=str, default="")
    lapse_status_reason_code = attr.ib(type=Optional[str], default=None)
    handicap = attr.ib(type=Optional[float], default=0)
    size_cancelled = attr.ib(type=float, default=0)
    size_voided = attr.ib(type=float, default=0)
    size_lapsed = attr.ib(type=float, default=0)
    average_price_matched = attr.ib(type=float, default=0)
    size_matched = attr.ib(type=float, default=0)
    size_remaining = attr.ib(type=float, default=0)
    customer_strategy_reference = attr.ib(type=str, default="")
    customer_order_reference = attr.ib(type=str, default=None)

    @classmethod
    def from_betfair_stream_api(cls, market_id: str, selection_id: int, order: OrderDict) -> Order:
        return cls(
            market_id=market_id,
            selection_id=selection_id,
            side=Side[order["side"]],
            size_voided=order["sv"],
            persistence_type=PersistenceType[str(order.get("pt"))],
            order_type=OrderType[order["ot"]],
            lapse_status_reason_code=order.get("lsrc"),
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
    def from_betfair_rest_api(cls, order: BetfairLightweightOrder) -> Order:
        return cls(
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
        )

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        for k, v in attr.asdict(self).items():
            if isinstance(v, Enum):
                d[k] = v.value
            elif isinstance(v, datetime):
                d[k] = v.isoformat()
            else:
                d[k] = v

        return d
