from enum import Enum, auto
from typing import Dict, List
from enum import Enum
import attr
from attr import asdict
from betfairstreamer.utils import parse_betfair_date
from datetime import datetime
import json


def to_camel(snake: str):
    components = snake.split("_")
    # We capitalize the first letter of each component except the first one
    # with the 'title' method and join them together.
    return components[0] + "".join(x.title() for x in components[1:])


def to_dict_camel(d: Dict) -> Dict:
    l = {}

    for k, v in d.items():

        if isinstance(v, dict):
            l[to_camel(k)] = to_dict_camel(v)
        else:
            l[to_camel(k)] = v

    return l


class BetfairAPISerializer:
    def to_dict(self) -> Dict:
        return to_dict_camel(asdict(self))


class ErrorCode(Enum):
    NO_APP_KEY = "NO_APP_KEY"
    INVALID_APP_KEY = "INVALID_APP_KEY"
    NO_SESSION = "NO_SESSION"
    INVALID_SESSION_INFORMATION = "INVALID_SESSION_INFORMATION"
    NOT_AUTHORIZED = "NOT_AUTHORIZED"
    INVALID_INPUT = "INVALID_INPUT"
    INVALID_CLOCK = "INVALID_CLOCK"
    UNEXPECTED_ERROR = "UNEXPECTED_ERROR"
    TIMEOUT = "TIMEOUT"
    SUBSCRIPTION_LIMIT_EXCEEDED = "SUBSCRIPTION_LIMIT_EXCEEDED"
    INVALID_REQUEST = "INVALID_REQUEST"
    CONNECTION_FAILED = "CONNECTION_FAILED"
    MAX_CONNECTION_LIMIT_EXCEEDED = "MAX_CONNECTION_LIMIT_EXCEEDED"


class StatusCode(str, Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


class OP(str, Enum):
    authentication = "authentication"
    mcm = "mcm"
    status = "status"
    connection = "connection"
    marketSubscription = "marketSubscription"
    orderSubscription = "orderSubscription"


class BettingType(str, Enum):
    ODDS = "ODDS"
    LINE = "LINE"
    RANGE = "RANGE"
    ASIAN_HANDICAP_DOUBLE_LINE = "ASIAN_HANDICAP_DOUBLE_LINE"
    ASIAN_HANDICAP_SINGLE_LINE = "ASIAN_HANDICAP_SINGLE_LINE"


class Field(str, Enum):
    EX_BEST_OFFERS_DISP = "EX_BEST_OFFERS_DISP"
    EX_BEST_OFFERS = "EX_BEST_OFFERS"
    EX_ALL_OFFERS = "EX_ALL_OFFERS"
    EX_TRADED = "EX_TRADED"
    EX_TRADED_VOL = "EX_TRADED_VOL"
    EX_LTP = "EX_LTP"
    EX_MARKET_DEF = "EX_MARKET_DEF"
    SP_TRADED = "SP_TRADED"
    SP_PROJECTED = "SP_PROJECTED"


class Status(str, Enum):
    INACTIVE = "INACTIVE"
    OPEN = "OPEN"
    SUSPENDED = "SUSPENDED"
    CLOSED = "CLOSED"


class PriceLadderType(str, Enum):
    CLASSIC = "CLASSIC"
    FINEST = "FINEST"
    LINE_RANGE = "LINE_RANGE"


class RunnerStatus(str, Enum):
    ACTIVE = "ACTIVE"
    WINNER = "WINNER"
    LOSER = "LOSER"
    REMOVED = "REMOVED"
    REMOVED_VACANT = "REMOVED_VACANT"
    HIDDEN = "HIDDEN"
    PLACED = "PLACED"


@attr.s
class AuthenticationMessage(BetfairAPISerializer):
    session = attr.ib(type=str)
    app_key = attr.ib(type=str)
    op = attr.ib(type=OP, default=OP.authentication)
    id = attr.ib(type=int, default=None)


@attr.s
class StatusMessage:
    op = attr.ib(type=OP)
    id = attr.ib(type=int)
    connections_available = attr.ib(type=int)
    status_code = attr.ib(type=StatusCode, default=None)
    connection_closed = attr.ib(type=str, default=None)
    error_code = attr.ib(type=ErrorCode, default=None)
    error_message = attr.ib(type=str, default=None)

    @classmethod
    def from_stream_message(cls, msg):
        return cls(
            op=OP[msg.get("op")],
            id=msg.get("id"),
            error_code=msg.get("errorCode"),
            connection_closed=msg.get("connectionClosed"),
            status_code=StatusCode[msg.get("statusCode")],
            connections_available=msg.get("connectionsAvailable"),
        )


@attr.s
class ConnectionMessage:
    op = attr.ib(type=OP)
    connection_id = attr.ib(type=str, default=None)

    @classmethod
    def from_stream_message(cls, msg):
        return cls(op=OP[msg["op"]], connection_id=msg["connectionId"])


@attr.s
class MarketFilter:
    country_codes = attr.ib(type=List[str], factory=list)
    betting_types = attr.ib(type=List[BettingType], factory=list)
    turn_in_play_enabled = attr.ib(type=bool, default=None)
    market_types = attr.ib(type=List[str], factory=list)
    venues = attr.ib(type=List[str], factory=list)
    market_ids = attr.ib(type=List[str], factory=list)
    event_type_ids = attr.ib(type=List[int], factory=list)
    event_ids = attr.ib(type=List[str], factory=list)
    bsp_market = attr.ib(type=bool, default=None)
    race_types = attr.ib(type=List[str], factory=list)


@attr.s
class MarketDataFilter:
    fields = attr.ib(type=List[Field])
    ladder_levels = attr.ib(type=int, default=3)


@attr.s
class MarketSubscriptionMessage(BetfairAPISerializer):
    id = attr.ib(type=int, default=None)
    op = attr.ib(type=OP, default=OP.marketSubscription)
    segmentation_enabled = attr.ib(type=bool, default=True)
    clk = attr.ib(type=str, default=None)
    heartbeat_ms = attr.ib(type=int, default=None)
    initial_clk = attr.ib(type=str, default=None)
    conflate_ms = attr.ib(type=int, default=None)
    market_filter = attr.ib(type=MarketFilter, default=None)
    market_data_filter = attr.ib(type=MarketDataFilter, default=None)


@attr.s
class OrderFilter:
    include_overall_position = attr.ib(type=bool, default=None)
    customer_strategy_refs = attr.ib(type=list, default=None)
    parition_matched_by_strategy_ref = attr.ib(type=bool, default=None)


@attr.s
class OrderSubscriptionMessage(BetfairAPISerializer):
    op = attr.ib(type=OP, default=OP.orderSubscription)
    id = attr.ib(type=int, default=None)
    segmentation_enabled = attr.ib(type=bool, default=None)
    clk = attr.ib(type=str, default=None)
    heartbeat_ms = attr.ib(type=int, default=None)
    initial_clk = attr.ib(type=str, default=None)
    conflate_ms = attr.ib(type=int, default=None)
    order_filter = attr.ib(type=OrderFilter, default=None)


@attr.s(slots=True, weakref_slot=False)
class PriceLadderDefinition:
    type = attr.ib(type=PriceLadderType)

    @classmethod
    def from_betfair_dict(cls, betfair_dict):
        return cls(type=betfair_dict.get("type", None))


@attr.s(slots=True, weakref_slot=False)
class KeyLineSelection:
    id = attr.ib(type=int)
    hc = attr.ib(type=float)

    @classmethod
    def from_betfair_dict(cls, betfair_dict):
        return cls(id=betfair_dict.get("id", None), hc=betfair_dict.get("hc", None))


@attr.s(slots=True, weakref_slot=False)
class KeyLineDefinition:
    kl = attr.ib(type=List[KeyLineSelection])

    @classmethod
    def from_betfair_dict(cls, betfair_dict):
        return cls(
            kl=[
                KeyLineSelection.from_betfair_dict(d)
                for d in betfair_dict.get("kl", [])
            ]
        )


@attr.s(slots=True, weakref_slot=False)
class RunnerDefinition:
    id = attr.ib(type=int)
    sort_priority = attr.ib(type=int)
    removal_date = attr.ib(type=datetime)
    hc = attr.ib(type=float)
    adjustment_factor = attr.ib(type=float)
    bsp = attr.ib(type=float)
    status = attr.ib(type=RunnerStatus)
    price_ladder_definition = attr.ib(type=PriceLadderDefinition)
    key_line_definition = attr.ib(type=KeyLineDefinition)
    hc = attr.ib(type=float)

    @classmethod
    def from_betfair_dict(cls, betfair_dict):
        return cls(
            id=betfair_dict.get("id", None),
            sort_priority=betfair_dict.get("sortPriority", None),
            removal_date=parse_betfair_date(betfair_dict.get("removalDate", None)),
            hc=betfair_dict.get("hc", None),
            adjustment_factor=betfair_dict.get("adjustmentFactor", None),
            bsp=betfair_dict.get("bsp", None),
            status=RunnerStatus[betfair_dict.get("status", "REMOVED")],
            price_ladder_definition=PriceLadderDefinition.from_betfair_dict(
                betfair_dict.get("priceLadderDefinition", {})
            ),
            key_line_definition=KeyLineDefinition.from_betfair_dict(
                betfair_dict.get("keylineDefinition", {})
            ),
        )


@attr.s(slots=True, weakref_slot=False)
class MarketDefinition:

    venue = attr.ib(type=str)
    race_type = attr.ib(type=str)
    settled_time = attr.ib(type=datetime)
    timezone = attr.ib(type=str)
    each_way_divisor = attr.ib(type=str)
    regulators = attr.ib(type=float)
    market_type = attr.ib(type=str)
    market_base_rate = attr.ib(type=float)
    number_of_winners = attr.ib(type=float)
    country_code = attr.ib(type=str)
    line_max_unit = attr.ib(type=float)
    in_play = attr.ib(type=bool)
    bet_delay = attr.ib(type=int)
    bsp_market = attr.ib(type=bool)
    betting_type = attr.ib(type=BettingType)
    number_of_active_runners = attr.ib(type=int)
    line_min_unit = attr.ib(type=float)
    event_id = attr.ib(type=str)
    cross_matching = attr.ib(type=bool)
    runner_voidable = attr.ib(type=bool)
    turn_in_play_enabled = attr.ib(type=bool)
    price_ladder_definition = attr.ib(type=PriceLadderDefinition)
    keyline_definition = attr.ib(type=KeyLineDefinition)
    suspend_time = attr.ib(type=datetime)
    discount_allowed = attr.ib(type=bool)
    persistence_enabled = attr.ib(type=bool)
    runners = attr.ib(type=List[RunnerDefinition])
    version = attr.ib(type=int)
    event_type_id = attr.ib(type=int)
    complete = attr.ib(type=bool)
    open_date = attr.ib(type=datetime)
    market_time = attr.ib(type=datetime)
    bsp_reconciled = attr.ib(type=bool)
    line_interval = attr.ib(type=float)
    status = attr.ib(type=Status)

    @classmethod
    def from_betfair_dict(cls, betfair_dict: Dict):
        return cls(
            venue=betfair_dict.get("venue", None),
            race_type=betfair_dict.get("raceType", None),
            settled_time=betfair_dict.get("settledTime", None),
            timezone=betfair_dict.get("timezone", None),
            each_way_divisor=betfair_dict.get("eachWayDivisor", None),
            regulators=betfair_dict.get("regulators", None),
            market_type=betfair_dict.get("marketType", None),
            market_base_rate=betfair_dict.get("marketBaseRate", None),
            number_of_winners=betfair_dict.get("numberOfWinners", None),
            country_code=betfair_dict.get("countryCode", None),
            line_max_unit=betfair_dict.get("lineMaxUnit", None),
            in_play=betfair_dict.get("inPlay", None),
            bet_delay=betfair_dict.get("betDelay", None),
            bsp_market=betfair_dict.get("bspMarket", None),
            betting_type=BettingType[betfair_dict.get("bettingType", None)],
            number_of_active_runners=betfair_dict["numberOfActiveRunners"],
            line_min_unit=betfair_dict.get("lineMinUnit", None),
            event_id=betfair_dict.get("eventId", None),
            cross_matching=betfair_dict.get("crossMatching", None),
            runner_voidable=betfair_dict.get("runnerVoidAble", None),
            turn_in_play_enabled=betfair_dict["turnInPlayEnabled"],
            price_ladder_definition=PriceLadderDefinition.from_betfair_dict(
                betfair_dict.get("priceLadderDefinition", {})
            ),
            keyline_definition=KeyLineDefinition.from_betfair_dict(
                betfair_dict.get("keylineDefinition", {})
            ),
            suspend_time=parse_betfair_date(betfair_dict.get("suspend_time", "")),
            discount_allowed=betfair_dict.get("discount_allowed", None),
            persistence_enabled=betfair_dict.get("persistenceEnabled", None),
            runners=[
                RunnerDefinition.from_betfair_dict(r)
                for r in betfair_dict.get("runners", [])
            ],
            version=betfair_dict.get("version", None),
            event_type_id=betfair_dict.get("eventTypeId", None),
            complete=betfair_dict.get("complete", None),
            open_date=parse_betfair_date(betfair_dict.get("openDate", None)),
            market_time=parse_betfair_date(betfair_dict.get("marketTime", None)),
            bsp_reconciled=betfair_dict.get("bspReconciled", None),
            line_interval=betfair_dict.get("lineInterval", None),
            status=Status[betfair_dict.get("status", None)],
        )
