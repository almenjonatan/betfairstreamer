from typing import List, Optional

from betfairstreamer.models.betfair_api import (
    OP,
    BetfairMarketDataFilter,
    BetfairMarketFilter,
    BetfairMarketSubscriptionMessage,
    BetfairOrderFilter,
    BetfairOrderSubscriptionMessage,
)


def create_market_subscription(
    market_ids: Optional[List[str]] = None,
    bsp_market: Optional[bool] = None,
    betting_types: Optional[List[str]] = None,
    event_type_ids: Optional[List[str]] = None,
    event_ids: Optional[List[str]] = None,
    turn_in_play_enabled: Optional[bool] = None,
    market_types: Optional[List[str]] = None,
    venues: Optional[List[str]] = None,
    country_codes: Optional[List[str]] = None,
    race_types: Optional[List[str]] = None,
    fields: Optional[List[str]] = None,
    conflate_ms: Optional[int] = 0,
    ladder_levels: Optional[int] = 3,
    stream_id: int = 1,
    segmentation_enabled: Optional[bool] = True,
    heartbeat_ms: Optional[int] = 5000,
) -> BetfairMarketSubscriptionMessage:
    market_filter = BetfairMarketFilter()
    market_data_filter = BetfairMarketDataFilter()

    if market_ids is not None:
        assert isinstance(market_ids, list)

        for market_id in market_ids:
            assert isinstance(market_id, str), "market id should be of type " + str(str)

        market_filter["marketIds"] = market_ids

    if bsp_market is not None:
        assert isinstance(bsp_market, bool), "should be bool got, " + str(type(bsp_market))

        market_filter["bspMarket"] = bsp_market

    if betting_types is not None:

        assert isinstance(betting_types, list), "betting_types should be of instance, " + str(list)

        betting_types_entries = {"ODDS", "LINE", "RANGE", "ASIAN_HANDICAP_DOUBLE_LINE", "ASIAN_HANDICAP_SINGLE_LINE"}

        for betting_type in betting_types:
            assert isinstance(betting_type, str), "betting type should be of instance " + str(str)
            assert betting_type in betting_types_entries, (
                betting_type + " is not a valid betting type\n" + "valid betting types: " + str(betting_types_entries)
            )

        market_filter["bettingTypes"] = betting_types

    if event_type_ids is not None:

        assert isinstance(event_type_ids, list), "event_type_ids should be of instance, " + str(list)

        for event_type_id in event_type_ids:
            assert isinstance(event_type_id, str), "market id should be of type " + str(str)

        market_filter["eventTypeIds"] = event_type_ids

    if event_ids is not None:

        assert isinstance(event_ids, list), "event_ids should be of instance, " + str(list)

        for event_id in event_ids:
            assert isinstance(event_id, str), "event_ids should only contain " + str(str)

        market_filter["eventIds"] = event_ids

    if turn_in_play_enabled is not None:
        assert isinstance(turn_in_play_enabled, bool)

        market_filter["turnInPlayEnabled"] = turn_in_play_enabled

    if market_types is not None:

        assert isinstance(event_type_ids, list), "market_types should be of instance, " + str(list)

        for market_type in market_types:
            assert isinstance(market_type, str), "market_types should only contain " + str(str)

        market_filter["marketTypes"] = market_types

    if venues is not None:

        assert isinstance(venues, list), "venues should be of instance, " + str(list)

        for v in venues:
            assert isinstance(v, str), "venues should only contain " + str(str)

        market_filter["venues"] = venues

    if country_codes is not None:
        assert isinstance(country_codes, list), "country_codes should be of instance, " + str(list)

        for c in country_codes:
            assert isinstance(c, str), "country_codes should only contain " + str(str)

        market_filter["countryCodes"] = country_codes

    if race_types is not None:

        assert isinstance(venues, list), "race_types should be of instance, " + str(list)

        for r in race_types:
            assert isinstance(r, str), "race_types should only contain " + str(str)

        market_filter["raceTypes"] = race_types

    if fields is not None:
        assert isinstance(fields, list)
        valid_fields = {
            "EX_BEST_OFFERS_DISP",
            "EX_BEST_OFFERS",
            "EX_ALL_OFFERS",
            "EX_TRADED",
            "EX_TRADED_VOL",
            "EX_LTP",
            "EX_MARKET_DEF",
            "SP_TRADED",
            "SP_PROJECTED",
        }
        for f in fields:
            assert isinstance(f, str), "fields should only contain " + str(str)
            assert f in valid_fields, "field " + f + " not in valid fields\nvalid fields: " + str(valid_fields)

        market_data_filter["fields"] = fields

    if ladder_levels is not None:
        assert isinstance(ladder_levels, int)
        assert (
            0 < ladder_levels <= 10
        ), "Ladder levels are only valdid 1 - 10, if you want more use field, EX_ALL_OFFERS"

    market_data_filter["ladderLevels"] = ladder_levels

    if stream_id is not None:
        assert isinstance(stream_id, int)

    return BetfairMarketSubscriptionMessage(
        op=OP.marketSubscription.value,
        id=stream_id,
        marketFilter=market_filter,
        marketDataFilter=market_data_filter,
        conflateMs=conflate_ms,
        segmentationEnabled=segmentation_enabled,
        heartbeatMs=heartbeat_ms,
    )


def create_order_subscription(
    stream_id: int = 1,
    segmentation_enabled: bool = True,
    heartbeat_ms: int = 5000,
    conflate_ms: int = 0,
    order_filter: Optional[BetfairOrderFilter] = None,
) -> BetfairOrderSubscriptionMessage:
    return BetfairOrderSubscriptionMessage(
        id=stream_id,
        op=OP.orderSubscription.value,
        orderFilter=order_filter if order_filter else {},
        segmentationEnabled=segmentation_enabled,
        heartbeatMs=heartbeat_ms,
        conflateMs=conflate_ms,
    )
