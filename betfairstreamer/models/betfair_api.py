from __future__ import annotations

from enum import Enum
from typing import List, Optional, TypedDict, Union


class PersistenceType(Enum):
    L = "LAPSE"
    P = "PERSIST"
    MOC = "MARKET_ON_CHANGE"
    LAPSE = "LAPSE"
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


class OrderStatus(Enum):
    E = "EXECUTABLE"
    EC = "EXECUTION_COMPLETE"
    EXECUTABLE = "EXECUTABLE"
    EXECUTION_COMPLETE = "EXECUTION_COMPLETE"


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
    TOO_MANY_REQUESTS = "TOO_MANY_REQUESTS"


class StatusCode(Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


class OP(Enum):
    authentication = "authentication"
    mcm = "mcm"
    status = "status"
    connection = "connection"
    marketSubscription = "marketSubscription"
    orderSubscription = "orderSubscription"


class BettingType(Enum):
    ODDS = "ODDS"
    LINE = "LINE"
    RANGE = "RANGE"
    ASIAN_HANDICAP_DOUBLE_LINE = "ASIAN_HANDICAP_DOUBLE_LINE"
    ASIAN_HANDICAP_SINGLE_LINE = "ASIAN_HANDICAP_SINGLE_LINE"


class Field(Enum):
    EX_BEST_OFFERS_DISP = "EX_BEST_OFFERS_DISP"
    EX_BEST_OFFERS = "EX_BEST_OFFERS"
    EX_ALL_OFFERS = "EX_ALL_OFFERS"
    EX_TRADED = "EX_TRADED"
    EX_TRADED_VOL = "EX_TRADED_VOL"
    EX_LTP = "EX_LTP"
    EX_MARKET_DEF = "EX_MARKET_DEF"
    SP_TRADED = "SP_TRADED"
    SP_PROJECTED = "SP_PROJECTED"


class MarketStatus(Enum):
    INACTIVE = "INACTIVE"
    OPEN = "OPEN"
    SUSPENDED = "SUSPENDED"
    CLOSED = "CLOSED"


class PriceLadderDefinitionType(Enum):
    CLASSIC = "CLASSIC"
    FINEST = "FINEST"
    LINE_RANGE = "LINE_RANGE"


class RunnerStatus(Enum):
    ACTIVE = "ACTIVE"
    WINNER = "WINNER"
    LOSER = "LOSER"
    REMOVED = "REMOVED"
    REMOVED_VACANT = "REMOVED_VACANT"
    HIDDEN = "HIDDEN"
    PLACED = "PLACED"


class BetfairLimitOrder(TypedDict, total=False):
    size: float
    price: float
    persistenceType: str
    timeInForce: Optional[str]
    minFillSize: Optional[float]
    betTargetType: Optional[str]
    betTargetSize: Optional[float]


class BetfairPlaceInstruction(TypedDict, total=False):
    orderType: str
    selectionId: int
    side: str

    handicap: Optional[float]
    limitOrder: Optional[BetfairLimitOrder]
    customerOrderRef: Optional[str]


class BetfairPlaceOrder(TypedDict, total=False):
    marketId: str
    instructions: List[BetfairPlaceInstruction]
    customerRef: str
    marketVersion: float
    customerStrategyRef: str
    asynchronous: bool


class BetfairCancelInstruction(TypedDict):
    betId: str
    sizeReduction: float


class BetfairCancelOrder(TypedDict, total=False):
    marketId: str
    instructions: List[BetfairCancelInstruction]
    customerRef: str


class BetfairResponseMessage(TypedDict):
    op: str
    id: int


class BetfairRequestMessage(TypedDict):
    op: str
    id: int


class BetfairConnectionMessage(BetfairResponseMessage):
    connectionId: str


class BetfairStatusMessage(BetfairResponseMessage, total=False):
    connectionsAvailable: int
    errorMessage: str
    errorCode: str
    connectionId: str
    connectionClosed: bool
    statusCode: str


class BetfairAuthenticationMessage(BetfairRequestMessage):
    session: str
    appKey: str


class BetfairOrderFilter(TypedDict, total=False):
    includeOverallPosition: Optional[bool]
    accountIds: Optional[List[int]]
    customerStrategyRefs: Optional[List[str]]
    partitionMatchedByStrategyRef: Optional[bool]


class BetfairOrderSubscriptionMessage(BetfairRequestMessage, total=False):
    segmentationEnabled: Optional[bool]
    clk: Optional[str]
    heartbeatMs: Optional[int]
    initialClk: Optional[str]
    conflateMs: Optional[int]
    orderFilter: BetfairOrderFilter


class BetfairMarketFilter(TypedDict, total=False):
    countryCodes: List[str]
    bettingTypes: List[str]
    turnInPlayEnabled: Optional[bool]
    marketTypes: List[str]
    venues: List[str]
    marketIds: List[str]
    eventTypeIds: List[str]
    eventIds: List[str]
    bspMarket: Optional[bool]
    raceTypes: List[str]


class BetfairMarketDataFilter(TypedDict, total=False):
    ladderLevels: Optional[int]
    fields: Optional[List[str]]


class BetfairMarketSubscriptionMessage(BetfairRequestMessage, total=False):
    segmentationEnabled: Optional[bool]
    clk: Optional[str]
    heartbeatMs: Optional[int]
    initialClk: Optional[str]
    marketFilter: BetfairMarketFilter
    conflateMs: Optional[int]
    marketDataFilter: BetfairMarketDataFilter


class BetfairRunnerChange(TypedDict, total=False):
    tv: Union[int, float]
    batb: List[List[Union[int, float]]]
    spb: List[List[Union[float]]]
    bdatl: List[List[Union[int, float]]]
    trd: List[List[Union[int, float]]]
    spf: Union[int, float]
    ltp: Union[int, float]
    atb: List[List[Union[int, float]]]
    spl: List[List[Union[int, float]]]
    spn: Union[int, float]
    atl: List[List[Union[int, float]]]
    batl: List[List[Union[int, float]]]
    id: int
    hc: Union[int, float]
    bdatb: List[List[Union[int, float]]]


class BetfairKeyLineSelection(TypedDict):
    id: int
    hc: Union[int, float]


class BetfairKeyLineDefinition(TypedDict):
    kl: List[BetfairKeyLineSelection]


class BetfairRunnerDefinition(TypedDict, total=False):
    sortPriority: int
    removalDate: str
    id: int
    hc: Union[int, float]
    adjustmentFactor: Union[int, float]
    bsp: float
    status: str


class BetfairPriceLadderDefinition(TypedDict):
    type: str


class BetfairMarketDefinition(TypedDict, total=False):
    venue: str
    raceType: str
    settledTime: str
    timezone: str
    eachWayDivisor: Union[int, float]
    regulators: List[str]
    marketType: str
    eventName: str
    marketBaseRate: Union[int, float]
    numberOfWinners: int
    countryCode: str
    lineMaxUnit: Union[int, float]
    inPlay: bool
    betDelay: int
    bspMarket: bool
    bettingType: str
    numberOfActiveRunners: int
    lineMinUnit: Union[int, float]
    eventId: str
    crossMatching: bool
    runnersVoidable: bool
    turnInPlayEnabled: bool
    priceLadderDefinition: BetfairPriceLadderDefinition
    keyLineDefinition: BetfairKeyLineDefinition
    suspendTime: str
    discountAllowed: bool
    persistenceEnabled: bool
    runners: List[BetfairRunnerDefinition]
    version: int
    eventTypeId: str
    complete: bool
    openDate: str
    marketTime: str
    bspReconciled: bool
    lineInterval: Union[int, float]
    status: str


class BetfairMarketChange(TypedDict, total=False):
    rc: List[BetfairRunnerChange]
    img: bool
    tv: float
    con: bool
    marketDefinition: BetfairMarketDefinition
    id: str


class BetfairMarketChangeMessage(TypedDict, total=False):
    op: str
    id: int
    ct: str
    clk: str
    heartbeatMs: int
    pt: int
    initialClk: str
    mc: List[BetfairMarketChange]
    con: int
    segmentType: str
    status: int


class BetfairOrder(TypedDict):
    side: str
    sv: Union[int, float]
    pt: str
    ot: str
    lsrc: str
    p: Union[int, float]
    sc: Union[int, float]
    rc: str
    s: Union[int, float]
    pd: int
    rac: str
    md: int
    ld: int
    sl: Union[int, float]
    avp: Union[int, float]
    sm: Union[int, float]
    rfo: str
    id: str
    bsp: Union[int, float]
    rfs: str
    status: str
    sr: Union[int, float]


class BetfairOrderRunnerChange(TypedDict, total=False):
    mb: List[List[float]]
    smc: object
    uo: List[BetfairOrder]
    id: int
    hc: Union[int, float]
    fullImage: bool
    ml: List[List[float]]


class BetfairOrderMarketChange(TypedDict, total=False):
    accountId: int
    orc: List[BetfairOrderRunnerChange]
    closed: bool
    id: str


class BetfairOrderChangeMessage(TypedDict, total=False):
    op: str
    id: int
    ct: str
    clk: str
    heartbeatMs: int
    pt: int
    oc: List[BetfairOrderMarketChange]
    initialClk: str
    conflateMs: int
    segmentType: str
    status: int
