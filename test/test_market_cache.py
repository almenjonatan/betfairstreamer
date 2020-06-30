from itertools import groupby
from test.generators import generate_runner_definitions, market_definition_generator

import hypothesis.strategies as st
import numpy as np
from hypothesis import given

from betfairstreamer.models.betfair_api import (
    BetfairMarketChange,
    BetfairMarketChangeMessage,
    BetfairMarketDefinition,
    BetfairRunnerChange,
)
from betfairstreamer.models.market_cache import MarketCache


@given(st.data(), st.integers(2, 20))
def test_runner_change_generator(data, number_of_runners):
    runner_definitions = data.draw(
        generate_runner_definitions(number_of_runners=number_of_runners)
    )
    grouped_selection_ids = groupby(runner_definitions, key=lambda r: r["id"])

    # Check that each group has exactly one runner definition, uniqueness of selection id
    for k, g in grouped_selection_ids:
        assert len(list(g)) == 1


@given(st.data())
def test_market_cache_status_change(data):
    # TODO Generalise these tests. Model Based Testing!

    market_cache = MarketCache()

    mdf = data.draw(market_definition_generator())

    market_id = data.draw(st.integers(0, 10).map(lambda v: "1." + str(v)))

    status = data.draw(st.sampled_from(["SUSPENDED", "CLOSED", "OPEN"]))
    mdf["status"] = status

    market_change_message = BetfairMarketChangeMessage(
        op="mcm",
        mc=[BetfairMarketChange(id=market_id, marketDefinition=mdf, img=True)],
        pt=1,
    )

    market_cache(market_change_message)
    assert status == market_cache.market_books[market_id].market_definition["status"]


@given(st.data())
def test_runner_selection_id_change(data):
    # TODO Generalise these tests. Model Based Testing!

    mdf = data.draw(market_definition_generator())

    market_cache = MarketCache()

    mcm = BetfairMarketChangeMessage(
        op="mcm",
        mc=[BetfairMarketChange(id="1.2", marketDefinition=mdf, img=True)],
        pt=1,
    )

    market_books = market_cache(mcm)

    r1_id, r2_id = [rd["id"] for rd in market_books[0].market_definition["runners"][:2]]

    rc = [
        BetfairRunnerChange(id=r1_id, bdatb=[[0, 1.2, 24]]),
        BetfairRunnerChange(id=r2_id, bdatb=[[0, 1.4, 30]]),
    ]

    mcm = BetfairMarketChangeMessage(
        op="mcm", mc=[BetfairMarketChange(id="1.2", rc=rc,)], pt=2
    )

    market_books = market_cache(mcm)

    assert np.all(market_books[0].best_display[0, 0, 0, :] == np.array([1.2, 24]))
    assert np.all(market_books[0].best_display[1, 0, 0, :] == np.array([1.4, 30]))

    mdf = mdf.copy()

    mdf["runners"][0]["id"] = r2_id
    mdf["runners"][1]["id"] = r1_id

    mcm = BetfairMarketChangeMessage(
        op="mcm", mc=[BetfairMarketChange(id="1.2", marketDefinition=mdf)], pt=2
    )

    market_books = market_cache(mcm)

    assert np.all(market_books[0].best_display[0, 0, 0, :] == np.array([1.4, 30]))
    assert np.all(market_books[0].best_display[1, 0, 0, :] == np.array([1.2, 24]))
