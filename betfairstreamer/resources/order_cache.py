import attr
import os
import betfairlightweight

from betfairlightweight import APIClient
from enum import Enum, auto
from typing import Dict, Tuple
from collections import defaultdict
from betfairstreamer.utils import parse_betfair_date

USERNAME: str = os.environ["USERNAME"]
PASSWORD: str = os.environ["PASSWORD"]
APP_KEY: str = os.environ["APP_KEY"]


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
    order_reference = attr.ib(type=float)
    bet_id = attr.ib(type=str)
    bsp = attr.ib(type=float)
    strategy_reference = attr.ib(type=str)
    status = attr.ib(type=Status)
    side = attr.ib(type=Side)
    persistence_type = attr.ib(type=PersistenceType)
    order_type = attr.ib(type=OrderType)
    price = attr.ib(type=float)
    lapse_status_reason_code = attr.ib(type=str)
    regulator_code = attr.ib(type=float)
    size = attr.ib(type=float)
    placed_date = attr.ib(type=int)
    regulator_auth_code = attr.ib(type=str)
    matched_date = attr.ib(type=int)
    lapsed_date = attr.ib(type=int)
    size_cancelled = attr.ib(type=float, default=0)
    size_voided = attr.ib(type=float, default=0)
    size_lapsed = attr.ib(type=float, default=0)
    average_price_matched = attr.ib(type=float, default=0)
    size_matched = attr.ib(type=float, default=0)
    size_remaining = attr.ib(type=float, default=0)

    @classmethod
    def from_betfair_stream(cls, stream_message):
        return cls(
            side=Side[stream_message.get("side")],
            size_voided=stream_message.get("sv"),
            persistence_type=PersistenceType[stream_message.get("pt")],
            order_type=OrderType[stream_message.get("ot")],
            lapse_status_reason_code=stream_message.get("lsrc"),
            price=stream_message.get("p"),
            size_cancelled=stream_message.get("sc"),
            regulator_code=stream_message.get("rc"),
            size=stream_message.get("s"),
            placed_date=parse_betfair_date(stream_message.get("pd")),
            regulator_auth_code=stream_message.get("rac"),
            matched_date=parse_betfair_date(stream_message.get("md")),
            lapsed_date=parse_betfair_date(stream_message.get("ld")),
            size_lapsed=stream_message.get("size_lapsed"),
            average_price_matched=stream_message.get("avp"),
            size_matched=stream_message.get("sm"),
            order_reference=stream_message.get("rfo"),
            bet_id=stream_message.get("id"),
            bsp=stream_message.get("bsp"),
            strategy_reference=stream_message.get("rfs"),
            status=Status[stream_message.get("status")],
            size_remaining=stream_message.get("sr"),
        )


def default_d(t):
    def f():
        return defaultdict(t)

    return f


@attr.s(slots=True, weakref_slot=False)
class OrderCache:
    orders = attr.ib(type=Dict[str, Order], factory=dict)
    size_matched = attr.ib(type=Dict[Tuple[str, int, str], float], factory=default_d(float))
    size_cancelled = attr.ib(type=Dict[Tuple[str, int, str], float], factory=default_d(float))
    size_voided = attr.ib(type=Dict[Tuple[str, int, str], float], factory=default_d(float))
    size_remaining = attr.ib(type=Dict[Tuple[str, int, str], float], factory=default_d(float))
    market_orders = attr.ib(
        type=Dict[Tuple[str, int, str], Dict[str, Order]], factory=default_d(dict)
    )

    latest_order = attr.ib(type=Dict[Tuple[str, int, str], Order], factory=dict)

    def update(self, stream_message):
        for m in stream_message.get("oc", []):
            for s in m.get("orc"):
                for o in s.get("uo"):
                    self.update_order(m["id"], s["id"], Order.from_betfair_stream(o))

    def update_order(self, market_id: str, selection_id: int, order: Order):

        cached_order = self.orders.get(order.bet_id, {})
        key = (market_id, selection_id, order.side)

        if cached_order:
            self.size_matched[key] += order.size_matched - cached_order.size_matched

            self.size_cancelled[key] += order.size_cancelled - cached_order.size_cancelled

            self.size_voided[key] += order.size_voided - cached_order.size_voided

            self.size_remaining[key] -= cached_order.size_remaining - order.size_remaining

        else:
            self.size_matched[key] += order.size_matched
            self.size_cancelled[key] += order.size_cancelled
            self.size_voided[key] += order.size_voided
            self.size_remaining[key] += order.size_remaining

        self.orders[order.bet_id] = order

    def get_latest_order(self, market_id, selection_id, side) -> Order:
        return self.latest_order.get((market_id, selection_id, side))

    def get_size_matched(self, market_id, selection_id, side) -> float:
        return self.size_matched.get((market_id, selection_id, side), 0)

    def get_size_remaining(self, market_id, selection_id, side) -> float:
        return self.size_remaining.get((market_id, selection_id, side), 0)

    def get_size_cancelled(self, market_id, selection_id, side) -> float:
        return self.size_cancelled.get((market_id, selection_id, side), 0)

    def get_size_voided(self, market_id, selection_id, side) -> float:
        return self.size_voided((market_id, selection_id, side))

    def get_size_matched_equal(self, market_id, selection_id) -> bool:
        return self.get_size_matched(market_id, selection_id, Side.BACK) == self.get_size_matched(
            market_id, selection_id, Side.LAY
        )

    def get_size_matched_balance(self, market_id, selection_id):
        return self.get_size_matched(market_id, selection_id, Side.BACK) - self.get_size_matched(
            market_id, selection_id, Side.LAY
        )

    def get_trade_balance(self, market_id, selection_id):
        back_bets_size_matched = self.get_size_matched(market_id, selection_id, Side.BACK)
        lay_bets_size_matched = self.get_size_matched(market_id, selection_id, Side.LAY)

        back_bets_size_remaining = self.get_size_remaining(market_id, selection_id, Side.BACK)
        lay_bets_size_remaining = self.get_size_remaining(market_id, selection_id, Side.LAY)

        return round(
            back_bets_size_matched
            + back_bets_size_remaining
            - lay_bets_size_remaining
            - lay_bets_size_matched
        )

    def get_matched_balanced(self, market_id, selection_id):
        back_bets = self.get_size_matched(market_id, selection_id, "BACK")
        lay_bets = self.get_size_matched(market_id, selection_id, "LAY")

        return round(back_bets - lay_bets)

    def __call__(self, stream_update):
        if stream_update.get("op", "") == "ocm":
            return self.update(stream_update)

    @classmethod
    def from_betfair_api(cls):

        trading: APIClient = betfairlightweight.APIClient(
            username=USERNAME, password=PASSWORD, app_key=APP_KEY, locale="sweden"
        )

        trading.login()

        current_orders = trading.betting.list_current_orders(lightweight=False)

        mc = cls()
        for o in current_orders.orders:

            mc.update_order(
                o.market_id,
                o.selection_id,
                Order(
                    bet_id=o.bet_id,
                    price=o.price_size.price,
                    size=o.price_size.size,
                    bsp=o.bsp_liability,
                    side=Side[o.side],
                    status=Status[o.status],
                    persistence_type=PersistenceType[o.persistence_type],
                    order_type=OrderType[o.order_type],
                    placed_date=o.placed_date,
                    matched_date=o.matched_date,
                    average_price_matched=o.average_price_matched,
                    size_matched=o.size_matched,
                    size_remaining=o.size_remaining,
                    size_lapsed=o.size_lapsed,
                    size_cancelled=o.size_cancelled,
                    size_voided=o.size_voided,
                    regulator_code=o.regulator_code,
                    regulator_auth_code=o.regulator_code,
                    order_reference=o.customer_order_ref,
                    strategy_reference=o.customer_strategy_ref,
                    lapse_status_reason_code=None,
                    lapsed_date=None,
                ),
            )

        return mc
