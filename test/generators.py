from typing import Any, Tuple

import hypothesis.strategies as st
import numpy as np
from hypothesis.strategies import composite

from betfairstreamer.betfair.definitions import MarketDefinitionDict
from betfairstreamer.betfair.enums import RunnerStatus


@composite
def generate_message(draw: Any) -> Tuple[int, bytes, str]:
    i = draw(st.integers(min_value=1, max_value=100))

    msg = ""

    for _ in range(i):
        msg += draw(st.text()) + "\r\n"

    return len(msg.split("\r\n")[:-1]), msg.encode("utf-8"), msg


@composite
def market_definition(draw) -> MarketDefinitionDict:
    number_of_runners = draw(st.integers(1, 20))

    runner_definitions = []

    for i in range(number_of_runners):
        runner_definitions.append(
            {
                "status": draw(st.sampled_from(RunnerStatus).map(lambda v: v.value)),
                "id": draw(st.integers(0, 50)),
                "sortPriority": i + 1,
            }
        )

    md = st.fixed_dictionaries(
        {
            "bspMarket": st.just(False),
            "turnInPlayEnabled": st.just(True),
            "persistenceEnabled": st.just(True),
            "marketBaseRate": st.just(5),
            "eventId": st.just("29739681"),
            "eventTypeId": st.just("1"),
            "numberOfWinners": st.just(1),
            "bettingType": st.just("ODDS"),
            "marketType": st.just("MATCH_ODDS"),
            "marketTime": st.just("2020-03-10T19:45:00.000Z"),
            "suspendTime": st.just("2020-03-10T19:45:00.000Z"),
            "bspReconciled": st.just(False),
            "complete": st.just(False),
            "inPlay": st.just(False),
            "crossMatching": st.just(True),
            "runnersVoidable": st.just(False),
            "numberOfActiveRunners": st.integers(0, number_of_runners),
            "betDelay": st.just(0),
            "status": st.just("OPEN"),
            "runners": st.just(runner_definitions),
            "regulators": st.just(["MR_INT"]),
            "countryCode": st.just("GB"),
            "discountAllowed": st.just(True),
            "timezone": st.just("GMT"),
            "openDate": st.just("2020-03-10T19:45:00.000Z"),
            "version": st.just(3212481126),
            "priceLadderDefinition": st.just({"type": "CLASSIC"}),
        }
    )

    return draw(md)


@composite
def runner_change_messages(
    draw, selection_ids, ladder_levels=3,
):

    rcs = []
    for selection_id in selection_ids:
        price = st.floats(1.01, 1000).map(lambda p: round(p, 2))
        size = st.floats(0, 100000000000).map(lambda s: round(s, 2))

        betting_types = ["batb", "batl", "bdatb", "bdatl"]
        no_betting_types = draw(st.integers(1, len(betting_types)))

        selected_betting_types = np.random.choice(
            betting_types, size=no_betting_types, replace=False
        )
        rc = {"id": selection_id}

        for t in selected_betting_types:
            no_ladder_levels = draw(st.integers(0, ladder_levels))

            price_size = draw(
                st.lists(
                    st.tuples(price, size), min_size=no_ladder_levels, max_size=no_ladder_levels
                )
            )
            rc[t] = [
                list((a,) + b)
                for a, b in zip(
                    np.random.choice(ladder_levels, size=len(price_size), replace=False),
                    price_size,
                )
            ]
        rcs.append(rc)

    return draw(st.just(rcs))


@composite
def initial_market_change_message(draw):
    mdf = draw(market_definition())

    no_markets = draw(st.integers(0, 10))

    market_updates = []

    for market_id in ["1." + str(i) for i in np.random.choice(100, size=no_markets)]:
        market_updates = [
            {
                "id": market_id,
                "marketDefinition": mdf,
                "rc": draw(runner_change_messages(selection_ids=[r["id"] for r in mdf["runners"]])),
            }
        ]

    return draw(
        st.fixed_dictionaries(
            {
                "op": st.just("mcm"),
                "pt": st.integers(0, 100),
                "mc": st.just(market_updates),
                "ct": st.just("SUB_IMAGE"),
            }
        )
    )
