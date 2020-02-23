import ciso8601


def parse_betfair_date(betfair_date: str):
    try:
        return ciso8601.parse_datetime(betfair_date)  # pylint: disable=I1101
    except Exception as _:
        return None
