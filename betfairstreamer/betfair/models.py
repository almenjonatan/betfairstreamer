from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol, Type, Union

import attr
import numpy as np
from betfairlightweight.resources.bettingresources import CurrentOrder as BetfairLightweightOrder

from betfairstreamer.betfair.definitions import (
    AuthenticationMessageDict,
    ConnectionMessageDict,
    KeyLineDefinitionDict,
    KeyLineSelectionDict,
    MarketChangeDict,
    MarketDataFilterDict,
    MarketDefinitionDict,
    MarketFilterDict,
    MarketSubscriptionMessageDict,
    OrderDict,
    OrderFilterDict,
    OrderSubscriptionMessageDict,
    PriceLadderDefinitionDict,
    RunnerChangeDict,
    RunnerDefinitionDict,
    StatusMessageDict,
)
from betfairstreamer.betfair.enums import (
    OP,
    BettingType,
    ErrorCode,
    Field,
    MarketStatus,
    OrderStatus,
    OrderType,
    PersistenceType,
    PriceLadderDefinitionType,
    RunnerStatus,
    Side,
    StatusCode,
)
from betfairstreamer.utils.converters import (
    localize_betfair_date,
    parse_betfair_date,
    parse_utc_timestamp,
)


class BetfairMessage(Protocol):
    def to_dict(
        self,
    ) -> Union[
        AuthenticationMessageDict, OrderSubscriptionMessageDict, MarketSubscriptionMessageDict
    ]:
        ...


@attr.s(slots=True, auto_attribs=True)
class AuthenticationMessage:
    id: int
    session: str
    app_key: str
    op: OP = OP.authentication

    def to_dict(self) -> AuthenticationMessageDict:
        return AuthenticationMessageDict(
            op=self.op.value, id=self.id, appKey=self.app_key, session=self.session
        )


@attr.s(slots=True, auto_attribs=True)
class StatusMessage:
    op: OP
    id: int
    status_code: StatusCode
    connections_available: Optional[int] = None
    connection_closed: Optional[bool] = None
    error_code: Optional[ErrorCode] = attr.ib(
        default=None, converter=attr.converters.optional(ErrorCode)
    )
    error_message: Optional[str] = None
    connection_id: Optional[str] = None

    @classmethod
    def from_betfair(cls: Type[StatusMessage], status_message: StatusMessageDict) -> StatusMessage:
        return cls(
            op=OP[status_message["op"]],
            id=status_message["id"],
            status_code=StatusCode[status_message["statusCode"]],
            error_message=status_message.get("errorMessage"),
            error_code=status_message.get("errorCode"),
            connection_closed=status_message.get("connectionClosed"),
            connections_available=status_message.get("connectionsAvailable"),
            connection_id=status_message.get("connectionId"),
        )


@attr.s(slots=True, auto_attribs=True)
class ConnectionMessage:
    op: OP
    connection_id: str

    @classmethod
    def from_betfair(cls, connection_message: ConnectionMessageDict) -> ConnectionMessage:
        return cls(
            op=OP[connection_message["op"]], connection_id=connection_message["connectionId"],
        )


@attr.s(slots=True, auto_attribs=True)
class MarketFilter:
    country_codes: List[str] = attr.ib(factory=list)
    betting_types: List[BettingType] = attr.ib(factory=list)
    turn_in_play_enabled: Optional[bool] = None
    market_types: List[str] = attr.ib(factory=list)
    venues: List[str] = attr.ib(factory=list)
    market_ids: List[str] = attr.ib(factory=list)
    event_type_ids: List[str] = attr.ib(factory=list)
    event_ids: List[str] = attr.ib(factory=list)
    bsp_market: Optional[bool] = None
    race_types: List[str] = attr.ib(factory=list)

    def to_dict(self) -> MarketFilterDict:
        return MarketFilterDict(
            eventIds=self.event_ids,
            countryCodes=self.country_codes,
            bettingTypes=[b.value for b in self.betting_types],
            turnInPlayEnabled=self.turn_in_play_enabled,
            marketTypes=self.market_types,
            venues=self.venues,
            marketIds=self.market_ids,
            eventTypeIds=self.event_type_ids,
            bspMarket=self.bsp_market,
            raceTypes=self.race_types,
        )


@attr.s(slots=True, auto_attribs=True)
class MarketDataFilter:
    fields: List[Field] = attr.ib(factory=list)
    ladder_levels: int = 3

    def to_dict(self) -> MarketDataFilterDict:
        return MarketDataFilterDict(
            fields=[f.value for f in self.fields], ladderLevels=self.ladder_levels
        )


@attr.s(slots=True, auto_attribs=True)
class MarketSubscriptionMessage:
    id: int
    market_filter: MarketFilter
    market_data_filter: MarketDataFilter
    op: OP = OP.marketSubscription
    segmentation_enabled: Optional[bool] = None
    clk: Optional[str] = None
    initial_clk: Optional[str] = None
    heartbeat_ms: Optional[int] = None
    conflate_ms: Optional[int] = None

    def to_dict(self) -> MarketSubscriptionMessageDict:
        return MarketSubscriptionMessageDict(
            id=self.id,
            op=self.op.value,
            segmentationEnabled=self.segmentation_enabled,
            clk=self.clk,
            initialClk=self.initial_clk,
            heartbeatMs=self.heartbeat_ms,
            conflateMs=self.conflate_ms,
            marketFilter=self.market_filter.to_dict(),
            marketDataFilter=self.market_data_filter.to_dict(),
        )


@attr.s(slots=True, auto_attribs=True)
class OrderFilter:
    account_ids: Optional[List[int]] = None
    include_overall_position: Optional[bool] = None
    customer_strategy_refs: Optional[List[str]] = None
    partition_matched_by_strategy_ref: Optional[bool] = None

    def to_dict(self) -> OrderFilterDict:
        return OrderFilterDict(
            accountIds=self.account_ids,
            includeOverallPosition=self.include_overall_position,
            customerStrategyRefs=self.customer_strategy_refs,
            partitionMatchedByStrategyRef=self.partition_matched_by_strategy_ref,
        )


@attr.s(slots=True, auto_attribs=True)
class OrderSubscriptionMessage:
    id: int
    op: OP = OP.orderSubscription

    segmentation_enabled: Optional[bool] = None
    heartbeat_ms: Optional[int] = None
    initial_clk: Optional[str] = None
    clk: Optional[str] = None
    conflate_ms: Optional[int] = None
    order_filter: OrderFilter = attr.ib(factory=OrderFilter)

    def to_dict(self) -> OrderSubscriptionMessageDict:
        return {
            "op": self.op.value,
            "id": self.id,
            "segmentationEnabled": self.segmentation_enabled,
            "clk": self.clk,
            "heartbeatMs": self.heartbeat_ms,
            "initialClk": self.initial_clk,
            "conflateMs": self.conflate_ms,
            "orderFilter": self.order_filter.to_dict(),
        }


@attr.s(slots=True, auto_attribs=True)
class RunnerDefinition:
    id: int
    sort_priority: int
    status: RunnerStatus
    removal_date: Optional[datetime] = None
    adjustment_factor: Optional[float] = None
    bsp: Optional[float] = None
    hc: Optional[float] = None

    @classmethod
    def from_betfair(cls, runner_definition: RunnerDefinitionDict) -> RunnerDefinition:
        return cls(
            id=runner_definition["id"],
            sort_priority=runner_definition["sortPriority"],
            status=RunnerStatus[runner_definition["status"]],
            removal_date=parse_betfair_date(runner_definition.get("removalDate")),
            hc=runner_definition.get("hc"),
            adjustment_factor=runner_definition.get("adjustmentFactor"),
            bsp=runner_definition.get("bsp"),
        )


@attr.s(slots=True, auto_attribs=True)
class KeyLineSelection:
    id: int
    hc: float

    @classmethod
    def from_betfair(cls, key_line_selection: KeyLineSelectionDict) -> KeyLineSelection:
        return cls(id=key_line_selection["id"], hc=key_line_selection["hc"])


@attr.s(slots=True, auto_attribs=True)
class KeyLineDefinition:
    kl: List[KeyLineSelection]

    @classmethod
    def from_betfair(
        cls: Type[KeyLineDefinition], key_line_definition: Optional[KeyLineDefinitionDict]
    ) -> Optional[KeyLineDefinition]:
        if key_line_definition is None:
            return None
        else:
            return cls(
                kl=[KeyLineSelection.from_betfair(d) for d in key_line_definition.get("kl", [])]
            )


@attr.s(slots=True, auto_attribs=True)
class PriceLadderDefinition:
    type: PriceLadderDefinitionType

    @classmethod
    def from_betfair(
        cls: Type[PriceLadderDefinition], price_ladder_definition: PriceLadderDefinitionDict
    ) -> PriceLadderDefinition:
        return cls(PriceLadderDefinitionType[price_ladder_definition["type"]])


@attr.s(slots=True, auto_attribs=True)
class MarketDefinition:
    timezone: str
    regulators: List[str]
    market_type: str
    market_base_rate: float
    number_of_winners: float

    in_play: bool
    bet_delay: int
    bsp_market: bool
    betting_type: BettingType
    number_of_active_runners: int
    event_id: str
    cross_matching: bool
    runner_voidable: bool
    turn_in_play_enabled: bool
    discount_allowed: bool
    persistence_enabled: bool
    runners: List[RunnerDefinition]
    version: int
    event_type_id: str
    complete: bool
    open_date: datetime
    bsp_reconciled: bool
    status: MarketStatus
    price_ladder_definition: Optional[PriceLadderDefinition] = attr.ib(converter=attr.converters.optional(PriceLadderDefinition.from_betfair))  # type: ignore
    country_code: Optional[str] = None
    market_time: Optional[datetime] = None
    suspend_time: Optional[datetime] = None
    key_line_definition: Optional[KeyLineDefinition] = None
    line_interval: Optional[float] = None
    line_min_unit: Optional[float] = None
    line_max_unit: Optional[float] = None
    each_way_divisor: Optional[float] = None
    venue: Optional[str] = None
    race_type: Optional[str] = None
    settled_time: Optional[datetime] = None

    @classmethod
    def from_betfair(
        cls: Type[MarketDefinition], market_definition_dict: MarketDefinitionDict
    ) -> MarketDefinition:
        return cls(
            venue=market_definition_dict.get("venue"),
            race_type=market_definition_dict.get("raceType"),
            settled_time=parse_betfair_date(market_definition_dict.get("settledTime")),
            timezone=market_definition_dict["timezone"],
            each_way_divisor=market_definition_dict.get("eachWayDivisor"),
            regulators=market_definition_dict["regulators"],
            market_type=market_definition_dict["marketType"],
            market_base_rate=market_definition_dict["marketBaseRate"],
            number_of_winners=market_definition_dict["numberOfWinners"],
            country_code=market_definition_dict.get("countryCode"),
            line_max_unit=market_definition_dict.get("lineMaxUnit"),
            in_play=market_definition_dict["inPlay"],
            bet_delay=market_definition_dict["betDelay"],
            bsp_market=market_definition_dict["bspMarket"],
            betting_type=BettingType[market_definition_dict["bettingType"]],
            number_of_active_runners=market_definition_dict["numberOfActiveRunners"],
            line_min_unit=market_definition_dict.get("lineMinUnit"),
            event_id=market_definition_dict["eventId"],
            cross_matching=market_definition_dict["crossMatching"],
            runner_voidable=market_definition_dict["runnersVoidable"],
            turn_in_play_enabled=market_definition_dict["turnInPlayEnabled"],
            price_ladder_definition=market_definition_dict.get("priceLadderDefinition"),
            key_line_definition=KeyLineDefinition.from_betfair(
                market_definition_dict.get("keyLineDefinition")
            ),
            suspend_time=parse_betfair_date(market_definition_dict["suspendTime"]),
            discount_allowed=market_definition_dict["discountAllowed"],
            persistence_enabled=market_definition_dict["persistenceEnabled"],
            runners=[RunnerDefinition.from_betfair(r) for r in market_definition_dict["runners"]],
            version=market_definition_dict["version"],
            event_type_id=market_definition_dict["eventTypeId"],
            complete=market_definition_dict["complete"],
            open_date=parse_betfair_date(market_definition_dict["openDate"]),
            market_time=parse_betfair_date(market_definition_dict.get("marketTime", "")),
            bsp_reconciled=market_definition_dict["bspReconciled"],
            line_interval=market_definition_dict.get("lineInterval"),
            status=MarketStatus[market_definition_dict["status"]],
        )


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


def create_sort_priority_mapping(market_definition: MarketDefinition) -> Dict[int, int]:
    return {r.id: r.sort_priority for r in market_definition.runners}


@attr.s(slots=True)
class RunnerBook:
    metadata = attr.ib(type=np.array)
    sort_priority_mapping = attr.ib(type=Dict[int, int])
    best_display = attr.ib(type=np.array, default=None)
    best_offers = attr.ib(type=np.array, default=None)

    def update(self, runner_change: List[RunnerChangeDict]) -> None:

        for r in runner_change:
            sort_priority = self.sort_priority_mapping[r["id"]] - 1

            bdatb = r.get("bdatb", [])
            bdatl = r.get("bdatl", [])

            batb = r.get("batb", [])
            batl = r.get("batl", [])

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

            if "ltp" in r:
                self.metadata[sort_priority, 0] = r.get("ltp")
            if "tv" in r:
                self.metadata[sort_priority, 1] = r.get("tv")

    @classmethod
    def from_betfair(cls, market_definition: MarketDefinition) -> RunnerBook:

        number_of_runners = len(market_definition.runners)

        best_display = -1 * np.ones(shape=(number_of_runners, 2, 3, 2))
        best_offers = -1 * np.ones(shape=(number_of_runners, 2, 3, 2))

        metadata = np.zeros(shape=(number_of_runners, 2))

        sort_priority_mapping = create_sort_priority_mapping(market_definition)

        return cls(
            best_display=best_display,
            best_offers=best_offers,
            metadata=metadata,
            sort_priority_mapping=sort_priority_mapping,
        )


@attr.s(slots=True)
class MarketBook:
    market_id = attr.ib(type=str)
    market_definition = attr.ib(type=MarketDefinition)
    runner_book = attr.ib(type=RunnerBook)

    def update(self, market_book: MarketChangeDict) -> None:

        if market_book.get("marketDefinition") is not None:
            self.market_definition = MarketDefinition.from_betfair(market_book["marketDefinition"])

            if market_book.get("img", False):
                self.runner_book = RunnerBook.from_betfair(self.market_definition)

            self.runner_book.sort_priority_mapping = create_sort_priority_mapping(
                self.market_definition
            )

        self.runner_book.update(market_book.get("rc", []))

    @classmethod
    def from_betfair(cls, market_book: MarketChangeDict) -> MarketBook:

        market_definition = MarketDefinition.from_betfair(market_book["marketDefinition"])
        runner_book = RunnerBook.from_betfair(market_definition)

        return cls(
            market_id=market_book["id"],
            market_definition=market_definition,
            runner_book=runner_book,
        )
