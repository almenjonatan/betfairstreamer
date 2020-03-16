import hypothesis.strategies as st
from hypothesis import given

from betfairstreamer.betfair.definitions import MarketDefinitionDict
from test.generators import market_definition, generate_market_definition_from_prev_version


@given(st.data(), market_definition())
def test_market_definition_generator(data, mdf: MarketDefinitionDict):
    prev_runner_sort = 0

    md2 = data.draw(generate_market_definition_from_prev_version(mdf))

    assert len(md2["runners"]) == len(mdf["runners"])

    for r in mdf["runners"]:
        assert r["sortPriority"] == prev_runner_sort + 1

        assert r["id"] is not None
        assert r["sortPriority"] is not None

        prev_runner_sort = r["sortPriority"]
