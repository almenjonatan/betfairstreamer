import ciso8601

from itertools import chain
from betfairlightweight.filters import market_filter


def parse_betfair_date(betfair_date: str):
    try:
        return ciso8601.parse_datetime(betfair_date)
    except Exception as _:
        return None


def fetch_new_market_ids(trading, competition_ids, market_types):
    trading.login()
    # List of lists, calculate how many markets you can retrieve up

    market_ids = []

    for ids in competition_ids:
        events = trading.betting.list_events(
            filter=market_filter(competition_ids=[ids],), lightweight=True
        )

        event_ids = [e["event"]["id"] for e in events]

        markets = trading.betting.list_market_catalogue(
            filter=market_filter(event_ids=event_ids, market_type_codes=market_types,),
            max_results=200,
            lightweight=True,
        )

        market_ids.append([m["marketId"] for m in markets])

    # Pack as many markets you can in each stream
    market_ids = list(chain(*market_ids))

    step = 200

    ms = [market_ids[i : i + step] for i in range(0, len(market_ids), step)]

    return ms
