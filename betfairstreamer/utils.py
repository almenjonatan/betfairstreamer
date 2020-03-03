import ciso8601
import datetime
from datetime import timezone


def parse_betfair_date(betfair_date: str):
    try:
        return ciso8601.parse_datetime(betfair_date)  # pylint: disable=I1101
    except Exception as _:
        return None


def parse_utc_timestamp(timestamp: int):
    try:
        return datetime.datetime.fromtimestamp(timestamp, tz=timezone.utc)
    except Exception:
        return
