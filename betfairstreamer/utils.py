from datetime import datetime, timezone
from typing import Optional, overload

import ciso8601
import pytz


@overload
def parse_betfair_date(betfair_date: None) -> None:
    ...


@overload
def parse_betfair_date(betfair_date: str) -> datetime:
    ...


def parse_betfair_date(betfair_date: Optional[str]) -> Optional[datetime]:
    if betfair_date is None:
        return None

    if betfair_date == "":
        raise ValueError("Date cannot be empty str")

    return ciso8601.parse_datetime(betfair_date)


@overload
def parse_utc_timestamp(timestamp: None) -> None:
    ...


@overload
def parse_utc_timestamp(timestamp: int) -> datetime:
    ...


def parse_utc_timestamp(timestamp: Optional[int]) -> Optional[datetime]:
    try:
        if timestamp is not None:
            return datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc)
        return None
    except Exception:
        return None


@overload
def localize_betfair_date(betfair_datetime: None) -> None:
    ...


@overload
def localize_betfair_date(betfair_datetime: datetime) -> datetime:
    ...


def localize_betfair_date(betfair_datetime: Optional[datetime]) -> Optional[datetime]:
    if betfair_datetime is None:
        return None

    try:
        return pytz.utc.localize(betfair_datetime)
    except Exception:
        return None
