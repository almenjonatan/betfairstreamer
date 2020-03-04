import ciso8601

from datetime import date
from datetime import timezone
from datetime import datetime

import pytz


def parse_betfair_date(betfair_date: str):
    try:
        return ciso8601.parse_datetime(betfair_date)  # pylint: disable=I1101
    except Exception as _:
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
