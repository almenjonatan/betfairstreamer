import attr
from enum import auto
from enum import Enum
from attr import asdict
from typing import List, Dict


def to_camel(snake: str):
    components = snake.split("_")
    # We capitalize the first letter of each component except the first one
    # with the 'title' method and join them together.
    return components[0] + "".join(x.title() for x in components[1:])


def to_dict_camel(d: Dict) -> Dict:
    n = {}

    for k, v in d.items():
        if not isinstance(v, dict):
            if isinstance(v, Enum):
                n[to_camel(k)] = v.name
            else:
                n[to_camel(k)] = v
        else:
            n[to_camel(k)] = to_dict_camel(v)

    return n


class ErrorCode(Enum):
    NO_APP_KEY = auto()
    INVALID_APP_KEY = auto()
    NO_SESSION = auto()
    INVALID_SESSION_INFORMATION = auto()
    NOT_AUTHORIZED = auto()
    INVALID_INPUT = auto()
    INVALID_CLOCK = auto()
    UNEXPECTED_ERROR = auto()
    TIMEOUT = auto()
    SUBSCRIPTION_LIMIT_EXCEEDED = auto()
    INVALID_REQUEST = auto()
    CONNECTION_FAILED = auto()
    MAX_CONNECTION_LIMIT_EXCEEDED = auto()


class StatusCode(Enum):
    SUCCESS = auto()
    FAILURE = auto()


class OP(Enum):
    authentication = auto()
    mcm = auto()
    status = auto()
    connection = auto()
    marketSubscription = auto()
    orderSubscription = auto()


class BettingType(Enum):
    ODDS = auto()
    LINE = auto()
    RANGE = auto()
    ASIAN_HANDICAP_DOUBLE_LINE = auto()
    ASIAN_HANDICAP_SINGLE_LINE = auto()


class Field(Enum):
    EX_BEST_OFFERS_DISP = auto()
    EX_BEST_OFFERS = auto()
    EX_ALL_OFFERS = auto()
    EX_TRADED = auto()
    EX_TRADED_VOL = auto()
    EX_LTP = auto()
    EX_MARKET_DEF = auto()
    SP_TRADED = auto()
    SP_PROJECTED = auto()


@attr.s
class Message:
    op = attr.ib(type=OP, default=None)
    id = attr.ib(type=str, default=None)

    def to_dict(self):
        return to_dict_camel(asdict(self))


@attr.s
class AuthenticationMessage(Message):
    op = attr.ib(type=str, default=OP.authentication)
    session = attr.ib(type=str, default=None)
    app_key = attr.ib(type=str, default=None)


@attr.s
class StatusMessage(Message):
    error_message = attr.ib(type=str, default=None)
    error_code = attr.ib(type=ErrorCode, default=None)
    connection_id = attr.ib(type=str, default=None)
    connection_closed = attr.ib(type=str, default=None)
    status_code = attr.ib(type=StatusCode, default=None)

    @classmethod
    def from_stream_message(cls, msg):
        return cls(
            op=OP[msg.get("op")],
            error_code=msg.get("errorCode"),
            connection_id=msg.get("connectionId"),
            connection_closed=msg.get("connectionClosed"),
            status_code=StatusCode[msg.get("statusCode")],
        )


@attr.s
class ConnectionMessage(Message):
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
    event_type_ids = attr.ib(type=List[str], factory=list)
    event_ids = attr.ib(type=List[str], factory=list)
    bsp_market = attr.ib(type=bool, default=None)
    race_types = attr.ib(type=List[str], factory=list)


@attr.s
class MarketDataFilter:
    fields = attr.ib(type=List[Field])
    ladder_levels = attr.ib(type=int, default=3)


@attr.s
class MarketSubscriptionMessage(Message):
    op = attr.ib(type=OP, default=OP.marketSubscription)
    segmentation_enabled = attr.ib(type=bool, default=None)
    clk = attr.ib(type=str, default=None)
    heartbeat_ms = attr.ib(type=int, default=None)
    initial_clk = attr.ib(type=str, default=None)
    conflate_ms = attr.ib(type=int, default=None)
    market_filter = attr.ib(type=MarketFilter, default=None)
    market_data_filter = attr.ib(type=MarketDataFilter, default=None)
    segmentation_enabled = attr.ib(type=bool, default=True)


@attr.s
class OrderFilter:
    include_overall_position = attr.ib(type=bool, default=None)
    customer_strategy_refs = attr.ib(type=list, default=None)
    parition_matched_by_strategy_ref = attr.ib(type=bool, default=None)


@attr.s
class OrderSubscriptionMessage(Message):
    op = attr.ib(type=OP, default=OP.orderSubscription)
    segmentation_enabled = attr.ib(type=bool, default=None)
    clk = attr.ib(type=str, default=None)
    heartbeat_ms = attr.ib(type=int, default=None)
    initial_clk = attr.ib(type=str, default=None)
    conflate_ms = attr.ib(type=int, default=None)
    order_filter = attr.ib(type=OrderFilter, default=None)

