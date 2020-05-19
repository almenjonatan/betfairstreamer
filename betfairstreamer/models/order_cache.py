from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Optional, Tuple

import attr

from betfairstreamer.models.betfair_api import BetfairOrderChangeMessage, Side, CurrentOrderSummary
from betfairstreamer.models.order_book import Order


@attr.s(auto_attribs=True, slots=True, weakref_slot=False)
class OrderCache:
    orders: Dict[str, Order] = attr.Factory(dict)

    size_matched: Dict[Tuple[str, int, Side], float] = attr.Factory(lambda: defaultdict(float))
    size_cancelled: Dict[Tuple[str, int, Side], float] = attr.Factory(lambda: defaultdict(float))
    size_voided: Dict[Tuple[str, int, Side], float] = attr.Factory(lambda: defaultdict(float))
    size_remaining: Dict[Tuple[str, int, Side], float] = attr.Factory(lambda: defaultdict(float))
    market_orders: Dict[Tuple[str, int, Side], Dict[str, Order]] = attr.Factory(lambda: defaultdict(dict))

    orders_on_selection: Dict[Tuple[str, int, Side], Dict[str, Order]] = attr.Factory(lambda: defaultdict(dict))

    latest_order: Dict[Tuple[str, int, Side], Order] = attr.Factory(dict)

    def update(self, order_change_message: BetfairOrderChangeMessage) -> List[Order]:
        updated_orders = []

        for m in order_change_message.get("oc", []):
            for s in m.get("orc", []):
                for o in s.get("uo", []):
                    updated_orders.append(self.update_order(Order.from_stream(m["id"], s["id"], o)))

        return updated_orders

    def update_order(self, order: Order) -> Order:

        cached_order: Optional[Order] = self.orders.get(order.bet_id)

        key = (order.market_id, order.selection_id, order.side)

        if cached_order:
            if order.size_remaining - cached_order.size_remaining < 0:
                self.size_matched[key] += order.size_matched - cached_order.size_matched
                self.size_cancelled[key] += order.size_cancelled - cached_order.size_cancelled
                self.size_voided[key] += order.size_voided - cached_order.size_voided
                self.size_remaining[key] += order.size_remaining - cached_order.size_remaining

                self.orders[order.bet_id] = order
                self.orders_on_selection[key][order.bet_id] = order

        else:
            self.size_matched[key] += order.size_matched
            self.size_cancelled[key] += order.size_cancelled
            self.size_voided[key] += order.size_voided
            self.size_remaining[key] += order.size_remaining

            self.orders[order.bet_id] = order
            self.orders_on_selection[key][order.bet_id] = order

        return order

    def get_orders_on_selection(self, market_id: str, selection_id: int, side: Side) -> Dict[str, Order]:
        return self.orders_on_selection[(market_id, selection_id, side)]

    def get_size_matched(self, market_id: str, selection_id: int, side: Side) -> float:
        return self.size_matched.get((market_id, selection_id, side), 0)

    def get_size_remaining(self, market_id: str, selection_id: int, side: Side) -> float:
        return self.size_remaining.get((market_id, selection_id, side), 0)

    def get_size_cancelled(self, market_id: str, selection_id: int, side: Side) -> float:
        return self.size_cancelled.get((market_id, selection_id, side), 0)

    def get_size_voided(self, market_id: str, selection_id: int, side: Side) -> float:
        return self.size_voided.get((market_id, selection_id, side), 0)

    def get_size_matched_equal(self, market_id: str, selection_id: int) -> bool:
        return self.get_size_matched(market_id, selection_id, Side.BACK) == self.get_size_matched(
            market_id, selection_id, Side.LAY
        )

    def get_size_matched_balance(self, market_id: str, selection_id: int) -> float:
        return self.get_size_matched(market_id, selection_id, Side.BACK) - self.get_size_matched(
            market_id, selection_id, Side.LAY
        )

    def get_trade_balance(self, market_id: str, selection_id: int) -> float:
        back_bets_size_matched = self.get_size_matched(market_id, selection_id, Side.BACK)
        lay_bets_size_matched = self.get_size_matched(market_id, selection_id, Side.LAY)

        back_bets_size_remaining = self.get_size_remaining(market_id, selection_id, Side.BACK)
        lay_bets_size_remaining = self.get_size_remaining(market_id, selection_id, Side.LAY)

        return round(
            back_bets_size_matched + back_bets_size_remaining - lay_bets_size_remaining - lay_bets_size_matched
        )

    def get_matched_balanced(self, market_id: str, selection_id: int) -> float:
        back_bets = self.get_size_matched(market_id, selection_id, Side.BACK)
        lay_bets = self.get_size_matched(market_id, selection_id, Side.LAY)

        return round(back_bets - lay_bets)

    def __call__(self, order_change_message: BetfairOrderChangeMessage) -> List[Order]:
        return self.update(order_change_message)

    @classmethod
    def from_api_ng(cls, current_orders: List[CurrentOrderSummary]) -> OrderCache:
        oc = cls()

        for o in current_orders:
            oc.update_order(Order.from_api_ng(o))

        return oc
