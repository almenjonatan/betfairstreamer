from typing import List, Union

import betfairlightweight
from betfairlightweight import APIClient

from betfairstreamer.betfair.enums import Field
from betfairstreamer.betfair.models import (
    MarketDataFilter,
    MarketFilter,
    MarketSubscriptionMessage,
    OrderSubscriptionMessage,
)


def fetch_market_ids(
    trading: APIClient, competition_ids: List[int], market_types: List[str]
) -> List[List[str]]:
    f = betfairlightweight.filters.market_filter(
        competition_ids=competition_ids, market_type_codes=market_types,
    )

    market_catalogues = [
        m.market_id for m in trading.betting.list_market_catalogue(filter=f, max_results=1000)
    ]

    return [market_catalogues[i : i + 200] for i in range(0, len(market_catalogues), 200)]


def create_subscriptions(
    market_ids: List[List[str]],
) -> List[Union[MarketSubscriptionMessage, OrderSubscriptionMessage]]:

    subs: List[Union[MarketSubscriptionMessage, OrderSubscriptionMessage]] = []

    for m in market_ids:
        market_filter = MarketFilter(market_ids=m)

        market_data_filter = MarketDataFilter(
            ladder_levels=3,
            fields=[
                Field.EX_LTP,
                Field.EX_MARKET_DEF,
                Field.EX_BEST_OFFERS_DISP,
                Field.EX_BEST_OFFERS,
                Field.EX_TRADED_VOL,
            ],
        )

        subs.append(
            MarketSubscriptionMessage(
                id=1, market_filter=market_filter, market_data_filter=market_data_filter
            )
        )

    return subs
