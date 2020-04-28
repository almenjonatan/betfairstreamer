from datetime import datetime, timezone
from typing import List, Optional, Union, overload

import betfairlightweight
import ciso8601
import pytz
from betfairlightweight import APIClient

from betfairstreamer.models.betfair_api import (
    OP,
    BetfairMarketDataFilter,
    BetfairMarketFilter,
    BetfairMarketSubscriptionMessage,
    BetfairOrderFilter,
    BetfairOrderSubscriptionMessage,
)


def fetch_market_ids(trading: APIClient, competition_ids: List[int], market_types: List[str]) -> List[List[str]]:
    f = betfairlightweight.filters.market_filter(competition_ids=competition_ids, market_type_codes=market_types)

    market_catalogues = [m.market_id for m in trading.betting.list_market_catalogue(filter=f, max_results=1000)]

    return [market_catalogues[i : i + 200] for i in range(0, len(market_catalogues), 200)]


def create_subscriptions(
    market_ids: List[List[str]],
) -> List[Union[BetfairMarketSubscriptionMessage, BetfairOrderSubscriptionMessage]]:
    subs: List[Union[BetfairMarketSubscriptionMessage, BetfairOrderSubscriptionMessage]] = []

    for m in market_ids:
        market_filter = BetfairMarketFilter(marketIds=m)

        market_data_filter = BetfairMarketDataFilter(
            ladderLevels=3,
            fields=["EX_LTP", "EX_MARKET_DEF", "EX_BEST_OFFERS_DISP", "EX_BEST_OFFERS", "EX_TRADED_VOL",],
        )

        subs.append(
            BetfairMarketSubscriptionMessage(
                id=1, op=OP.marketSubscription.value, marketFilter=market_filter, marketDataFilter=market_data_filter,
            )
        )

    return subs


@overload
def parse_betfair_date(betfair_date: None) -> None:
    ...


@overload
def parse_betfair_date(betfair_date: str) -> datetime:
    ...


def parse_betfair_date(betfair_date: Optional[str]) -> Optional[datetime]:
    if betfair_date is None:
        return None

    if betfair_date == "":
        raise ValueError("Date cannot be empty str")

    return ciso8601.parse_datetime(betfair_date)


@overload
def parse_utc_timestamp(timestamp: None) -> None:
    ...


@overload
def parse_utc_timestamp(timestamp: int) -> datetime:
    ...


def parse_utc_timestamp(timestamp: Optional[int]) -> Optional[datetime]:
    try:
        if timestamp is not None:
            return datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc)
        return None
    except Exception:
        return None


@overload
def localize_betfair_date(betfair_datetime: None) -> None:
    ...


@overload
def localize_betfair_date(betfair_datetime: datetime) -> datetime:
    ...


def localize_betfair_date(betfair_datetime: Optional[datetime]) -> Optional[datetime]:
    if betfair_datetime is None:
        return None

    try:
        return pytz.utc.localize(betfair_datetime)
    except Exception:
        return None


def create_market_subscription(
    id: int = 1,
    market_filter: Optional[BetfairMarketFilter] = None,
    market_data_filter: Optional[BetfairMarketDataFilter] = None,
    segmentation_enabled: bool = True,
    heartbeat_ms: int = 5000,
    conflate_ms: int = 0,
) -> BetfairMarketSubscriptionMessage:
    return BetfairMarketSubscriptionMessage(
        id=id,
        op=OP.marketSubscription.value,
        marketFilter=market_filter if market_filter else {},
        marketDataFilter=market_data_filter if market_data_filter else {},
        segmentationEnabled=segmentation_enabled,
        heartbeatMs=heartbeat_ms,
        conflateMs=conflate_ms,
    )


def create_order_subscription(
    id: int = 1,
    segmentation_enabled: bool = True,
    heartbeat_ms: int = 5000,
    conflate_ms: int = 0,
    order_filter: Optional[BetfairOrderFilter] = None,
) -> BetfairOrderSubscriptionMessage:
    return BetfairOrderSubscriptionMessage(
        id=id,
        op=OP.orderSubscription.value,
        orderFilter=order_filter if order_filter else {},
        segmentationEnabled=segmentation_enabled,
        heartbeatMs=heartbeat_ms,
        conflateMs=conflate_ms,
    )
