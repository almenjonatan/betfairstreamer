from __future__ import annotations

from datetime import datetime
from typing import Optional, Protocol, List, Union, Type

import attr

from betfairstreamer.betfair.definitions import (
    AuthenticationMessageDict,
    StatusMessageDict,
    ConnectionMessageDict,
    OrderFilterDict,
    OrderSubscriptionMessageDict,
    MarketSubscriptionMessageDict,
    MarketDataFilterDict,
    MarketFilterDict,
    RunnerDefinitionDict,
    KeyLineSelectionDict,
    KeyLineDefinitionDict,
    MarketDefinitionDict,
    PriceLadderDefinitionDict,
)
from betfairstreamer.betfair.enums import (
    OP,
    StatusCode,
    ErrorCode,
    BettingType,
    Field,
    RunnerStatus,
    MarketStatus,
    PriceLadderDefinitionType,
)
from betfairstreamer.utils import parse_betfair_date


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
    id: int
    connection_id: str

    @classmethod
    def from_betfair(cls, connection_message: ConnectionMessageDict) -> ConnectionMessage:
        return cls(
            op=OP[connection_message["op"]],
            id=connection_message["id"],
            connection_id=connection_message["connectionId"],
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
    price_ladder_definition: PriceLadderDefinition
    discount_allowed: bool
    persistence_enabled: bool
    runners: List[RunnerDefinition]
    version: int
    event_type_id: str
    complete: bool
    open_date: datetime
    bsp_reconciled: bool
    status: MarketStatus

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
            price_ladder_definition=PriceLadderDefinition.from_betfair(
                market_definition_dict["priceLadderDefinition"]
            ),
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
