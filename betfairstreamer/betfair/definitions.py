from typing import List, Optional, TypedDict, Union


class LimitOrderDict(TypedDict, total=False):
    size: float
    price: float
    persistenceType: str
    timeInForce: Optional[str]
    minFillSize: Optional[float]
    betTargetType: Optional[str]
    betTargetSize: Optional[float]


class PlaceInstructionDict(TypedDict, total=False):
    orderType: str
    selectionId: int
    side: str

    handicap: Optional[float]
    limitOrder: Optional[LimitOrderDict]
    customerOrderRef: Optional[str]


class PlaceInstruction(TypedDict):
    marketId: str
    instructions: List[PlaceInstructionDict]


class ResponseMessageDict(TypedDict):
    op: str
    id: int


class RequestMessageDict(TypedDict):
    op: str
    id: int


class ConnectionMessageDict(ResponseMessageDict):
    connectionId: str


class StatusMessageDict(ResponseMessageDict, total=False):
    connectionsAvailable: int
    errorMessage: str
    errorCode: str
    connectionId: str
    connectionClosed: bool
    statusCode: str


class AuthenticationMessageDict(RequestMessageDict):
    session: str
    appKey: str


class OrderFilterDict(TypedDict):
    includeOverallPosition: Optional[bool]
    accountIds: Optional[List[int]]
    customerStrategyRefs: Optional[List[str]]
    partitionMatchedByStrategyRef: Optional[bool]


class OrderSubscriptionMessageDict(RequestMessageDict):
    segmentationEnabled: Optional[bool]
    clk: Optional[str]
    heartbeatMs: Optional[int]
    initialClk: Optional[str]
    conflateMs: Optional[int]
    orderFilter: OrderFilterDict


class MarketFilterDict(TypedDict):
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


class MarketDataFilterDict(TypedDict):
    ladderLevels: Optional[int]
    fields: Optional[List[str]]


class MarketSubscriptionMessageDict(RequestMessageDict):
    segmentationEnabled: Optional[bool]
    clk: Optional[str]
    heartbeatMs: Optional[int]
    initialClk: Optional[str]
    marketFilter: MarketFilterDict
    conflateMs: Optional[int]
    marketDataFilter: MarketDataFilterDict


class RunnerChangeDict(TypedDict, total=False):
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


class KeyLineSelectionDict(TypedDict):
    id: int
    hc: Union[int, float]


class KeyLineDefinitionDict(TypedDict):
    kl: List[KeyLineSelectionDict]


class RunnerDefinitionDict(TypedDict, total=False):
    sortPriority: int
    removalDate: str
    id: int
    hc: Union[int, float]
    adjustmentFactor: Union[int, float]
    bsp: float
    status: str


class PriceLadderDefinitionDict(TypedDict):
    type: str


class MarketDefinitionDict(TypedDict, total=False):
    venue: str
    raceType: str
    settledTime: str
    timezone: str
    eachWayDivisor: Union[int, float]
    regulators: List[str]
    marketType: str
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
    priceLadderDefinition: PriceLadderDefinitionDict
    keyLineDefinition: KeyLineDefinitionDict
    suspendTime: str
    discountAllowed: bool
    persistenceEnabled: bool
    runners: List[RunnerDefinitionDict]
    version: int
    eventTypeId: str
    complete: bool
    openDate: str
    marketTime: str
    bspReconciled: bool
    lineInterval: Union[int, float]
    status: str


class MarketChangeDict(TypedDict, total=False):
    rc: List[RunnerChangeDict]
    img: bool
    tv: float
    con: bool
    marketDefinition: MarketDefinitionDict
    id: str


class MarketChangeMessageDict(TypedDict, total=False):
    op: str
    id: int
    ct: str
    clk: str
    heartbeatMs: int
    pt: int
    initialClk: str
    mc: List[MarketChangeDict]
    con: int
    segmentType: str
    status: int


class OrderDict(TypedDict):
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


class OrderRunnerChange(TypedDict, total=False):
    mb: List[List[float]]
    smc: object
    uo: List[OrderDict]
    id: int
    hc: Union[int, float]
    fullImage: bool
    ml: List[List[float]]


class OrderChange(TypedDict, total=False):
    accountId: int
    orc: List[OrderRunnerChange]
    closed: bool
    id: str


class OrderChangeMessage(TypedDict, total=False):
    op: str
    id: int
    ct: str
    clk: str
    heartbeatMs: int
    pt: int
    oc: List[OrderChange]
    initialClk: str
    conflateMs: int
    segmentType: str
    status: int
