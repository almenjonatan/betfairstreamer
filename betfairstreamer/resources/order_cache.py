import datetime
import os
from collections import defaultdict
from enum import Enum
from typing import Dict, Optional, Tuple

import attr
import betfairlightweight
from betfairlightweight import APIClient

from betfairstreamer.utils import (
    parse_betfair_date,
    parse_utc_timestamp,
)


class PersistenceType(Enum):
    L = "LAPSE"
    P = "PERSIST"
    MOC = "MARKET_ON_CHANGE"
    LAPSE = "LIMIT"
    PERSIST = "PERSIST"
    MARKET_ON_CLOSE = "MARKET_ON_CHANGE"


class Side(Enum):
    B = "BACK"
    L = "LAY"
    BACK = "BACK"
    LAY = "LAY"


class OrderType(Enum):
    L = "LIMIT"
    LOC = "LIMIT_ON_CLOSE"
    MOC = "MARKET_ON_CLOSE"
    LIMIT = "LIMIT"
    LIMIT_ON_CLOSE = "LIMIT_ON_CLOSE"
    MARKET_ON_CLOSE = "MARKET_ON_CLOSE"


class Status(Enum):
    E = "EXECUTABLE"
    EC = "EXECUTION_COMPLETE"
    EXECUTABLE = "EXECUTABLE"
    EXECUTION_COMPLETE = "EXECUTION_COMPLETE"


@attr.s(slots=True, weakref_slot=False)
class Order:
    market_id = attr.ib()
    selection_id = attr.ib()
    bet_id = attr.ib()
    bsp = attr.ib()
    status = attr.ib(type=Status)
    side = attr.ib(type=Side)
    persistence_type = attr.ib(type=PersistenceType)
    order_type = attr.ib(type=OrderType)
    price = attr.ib()
    regulator_code = attr.ib()
    size = attr.ib()
    placed_date = attr.ib(type=Optional[datetime.datetime])
    matched_date = attr.ib()
    lapsed_date = attr.ib(type=datetime.datetime, default=None)
    regulator_auth_code = attr.ib(type=str, default="")
    lapse_status_reason_code = attr.ib(type=str, default="")
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
    def from_betfair_stream(cls, market_id: str, selection_id: int, stream_message):
        return cls(
            market_id=market_id,
            selection_id=selection_id,
            side=Side[stream_message.get("side")],
            size_voided=stream_message.get("sv"),
            persistence_type=PersistenceType[stream_message.get("pt")],
            order_type=OrderType[stream_message.get("ot")],
            lapse_status_reason_code=stream_message.get("lsrc"),
            price=stream_message.get("p"),
            size_cancelled=stream_message.get("sc"),
            regulator_code=stream_message.get("rc"),
            size=stream_message.get("s"),
            placed_date=parse_utc_timestamp(stream_message.get("pd")),
            regulator_auth_code=stream_message.get("rac"),
            matched_date=parse_utc_timestamp(stream_message.get("md")),
            lapsed_date=parse_utc_timestamp(stream_message.get("ld")),
            size_lapsed=stream_message.get("size_lapsed"),
            average_price_matched=stream_message.get("avp"),
            size_matched=stream_message.get("sm"),
            bet_id=int(stream_message.get("id")),
            bsp=stream_message.get("bsp"),
            customer_strategy_reference=stream_message.get("rfs"),
            customer_order_reference=stream_message.get("rfo", None),
            status=Status[stream_message.get("status")],
            size_remaining=stream_message.get("sr"),
        )

    @classmethod
    def from_betfair_rest_api(cls, order: Dict):
        return cls(
            bet_id=order.get("betId"),
            market_id=order.get("marketId"),
            selection_id=order.get("selectionId"),
            handicap=order.get("handicap"),
            price=order.get("priceSize", {})["price"],
            size=order.get("priceSize", {})["size"],
            side=Side[order.get("side", "")],
            status=Status[order.get("status", "")],
            persistence_type=PersistenceType[order.get("persistenceType", "")],
            order_type=OrderType[order.get("orderType", "")],
            bsp=order.get("bspLiability"),
            placed_date=parse_betfair_date(order.get("placedDate")),
            average_price_matched=order.get("averagePriceMatched", None),
            size_matched=order.get("sizeMatched", 0),
            size_remaining=order.get("sizeRemaining", 0),
            size_lapsed=order.get("sizeLapesed", 0),
            size_cancelled=order.get("sizeCancelled", 0),
            regulator_code=order.get("regulatorCode"),
            customer_order_reference=order.get("customerOrderRef", ""),
            customer_strategy_reference=order.get("customerStrategyRef", ""),
            matched_date=order.get("matchedDate", None),
        )


def default_d(t):
    def f():
        return defaultdict(t)

    return f


@attr.s(slots=True, weakref_slot=False)
class OrderCache:
    orders = attr.ib(type=Dict[str, Order], factory=dict)
    size_matched = attr.ib(
        type=Dict[Tuple[str, int, Side], float], factory=default_d(float)
    )
    size_cancelled = attr.ib(
        type=Dict[Tuple[str, int, Side], float], factory=default_d(float)
    )
    size_voided = attr.ib(
        type=Dict[Tuple[str, int, Side], float], factory=default_d(float)
    )
    size_remaining = attr.ib(
        type=Dict[Tuple[str, int, Side], float], factory=default_d(float)
    )
    market_orders = attr.ib(
        type=Dict[Tuple[str, int, Side], Dict[str, Order]], factory=default_d(dict)
    )

    latest_order = attr.ib(type=Dict[Tuple[str, int, Side], Order], factory=dict)

    def update(self, stream_message):
        updated_orders = []

        for m in stream_message.get("oc", []):
            for s in m.get("orc", []):
                for o in s.get("uo", []):
                    updated_orders.append(
                        self.update_order(
                            Order.from_betfair_stream(m["id"], s["id"], o)
                        )
                    )

        return updated_orders

    def update_order(self, order: Order):

        cached_order: Optional[Order] = self.orders.get(order.bet_id)

        key = (order.market_id, order.selection_id, order.side)

        if cached_order:
            self.size_matched[key] += order.size_matched - cached_order.size_matched

            self.size_cancelled[key] += (
                order.size_cancelled - cached_order.size_cancelled
            )

            self.size_voided[key] += order.size_voided - cached_order.size_voided

            self.size_remaining[key] -= (
                cached_order.size_remaining - order.size_remaining
            )

        else:
            self.size_matched[key] += order.size_matched
            self.size_cancelled[key] += order.size_cancelled
            self.size_voided[key] += order.size_voided
            self.size_remaining[key] += order.size_remaining

        self.orders[order.bet_id] = order

        latest_order = self.get_latest_order(
            order.market_id, order.selection_id, order.side
        )

        if latest_order is None:
            self.latest_order[(order.market_id, order.selection_id, order.side)] = order
        elif (
            order.placed_date is not None
            and latest_order.placed_date is not None
            and order.placed_date >= latest_order.placed_date
        ):
            self.latest_order[(order.market_id, order.selection_id, order.side)] = order

        return order

    def get_latest_order(self, market_id, selection_id, side) -> Optional[Order]:
        return self.latest_order.get((market_id, selection_id, side))

    def get_size_matched(self, market_id, selection_id, side) -> Optional[float]:
        return self.size_matched.get((market_id, selection_id, side), 0)

    def get_size_remaining(self, market_id, selection_id, side) -> Optional[float]:
        return self.size_remaining.get((market_id, selection_id, side), 0)

    def get_size_cancelled(self, market_id, selection_id, side) -> Optional[float]:
        return self.size_cancelled.get((market_id, selection_id, side), 0)

    def get_size_voided(self, market_id, selection_id, side) -> Optional[float]:
        return self.size_voided.get((market_id, selection_id, side))

    def get_size_matched_equal(self, market_id, selection_id) -> bool:
        return self.get_size_matched(
            market_id, selection_id, Side.BACK
        ) == self.get_size_matched(market_id, selection_id, Side.LAY)

    def get_size_matched_balance(self, market_id, selection_id):
        return self.get_size_matched(
            market_id, selection_id, Side.BACK
        ) - self.get_size_matched(market_id, selection_id, Side.LAY)

    def get_trade_balance(self, market_id, selection_id):
        back_bets_size_matched = self.get_size_matched(
            market_id, selection_id, Side.BACK
        )
        lay_bets_size_matched = self.get_size_matched(market_id, selection_id, Side.LAY)

        back_bets_size_remaining = self.get_size_remaining(
            market_id, selection_id, Side.BACK
        )
        lay_bets_size_remaining = self.get_size_remaining(
            market_id, selection_id, Side.LAY
        )

        return round(
            back_bets_size_matched
            + back_bets_size_remaining
            - lay_bets_size_remaining
            - lay_bets_size_matched
        )

    def get_matched_balanced(self, market_id, selection_id):
        back_bets = self.get_size_matched(market_id, selection_id, Side.BACK)
        lay_bets = self.get_size_matched(market_id, selection_id, Side.LAY)

        return round(back_bets - lay_bets)

    def __call__(self, stream_update):
        if stream_update.get("op", "") == "ocm":
            return self.update(stream_update)

        return []

    @classmethod
    def from_betfair(cls):

        trading: APIClient = betfairlightweight.APIClient(
            username=os.environ["USERNAME"],
            password=os.environ["PASSWORD"],
            app_key=os.environ["APP_KEY"],
            certs=os.environ["CERT_PATH"],
            locale="sweden",
        )

        trading.login()

        current_orders = trading.betting.list_current_orders(lightweight=True)

        oc = cls()

        for o in current_orders["currentOrders"]:
            oc.update_order(Order.from_betfair_rest_api(o))

        return oc
