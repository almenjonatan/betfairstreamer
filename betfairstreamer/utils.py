from datetime import datetime
from datetime import timezone
from typing import Optional

import ciso8601
import pytz


def parse_betfair_date(betfair_date: Optional[str]) -> Optional[datetime]:
    if betfair_date is not None:
        return ciso8601.parse_datetime(betfair_date)

    return None


def parse_utc_timestamp(timestamp: int):
    try:
        return datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc)
    except Exception as e:
        return


def localize_betfair(betfair_datetime: datetime):
    try:
        return pytz.utc.localize(betfair_datetime)
    except Exception as e:
        return
