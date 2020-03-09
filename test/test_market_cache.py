from hypothesis import given

from betfairstreamer.betfair.models import MarketDefinition
from betfairstreamer.cache.market_cache import MarketCache
from test.generators import market_definition, initial_market_change_message


@given(market_definition())
def test_insert_market_definition(md):
    mdf = MarketDefinition.from_betfair(md)

    assert md["bspMarket"] == mdf.bsp_market
    assert md["status"] == mdf.status.value


@given(initial_market_change_message())
def test_initial_sub_image(initial_sub_image):
    mc = MarketCache()

    mc(initial_sub_image)
    assert len(mc.market_books) == len(initial_sub_image["mc"])

    mc(initial_sub_image)
    assert len(mc.market_books) == len(initial_sub_image["mc"])
