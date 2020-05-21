from typing import Optional, TypedDict


class CurrentOrderSummaryRecord(TypedDict, total=False):
    betId: str
    marketId: str
    selectionId: int
    handicap: float
    price: float
    size: float
    bspLiability: float
    side: str
    status: str
    persistenceType: str
    orderType: str
    placedDate: str
    matchedDate: Optional[str]
    averagePriceMatched: Optional[float]
    sizeMatched: Optional[float]
    sizeRemaining: Optional[float]
    sizeLapsed: Optional[float]
    sizeCancelled: Optional[float]
    sizeVoided: Optional[float]
    regulatorAuthCode: Optional[str]
    regulatorCode: Optional[str]
    customerOrderRef: Optional[str]
    customerStrategyRef: Optional[str]
