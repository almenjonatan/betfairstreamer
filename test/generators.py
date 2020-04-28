from typing import Any, Tuple, List

import hypothesis.strategies as st
import numpy as np
from hypothesis.strategies import composite

from betfairstreamer.models.betfair_api import RunnerStatus, BetfairMarketDefinition


@composite
def generate_message(draw: Any) -> Tuple[int, bytes, str]:
    i = draw(st.integers(min_value=1, max_value=100))

    msg = ""

    for _ in range(i):
        msg += draw(st.text()) + "\r\n"

    return len(msg.split("\r\n")[:-1]), msg.encode("utf-8"), msg


@composite
def generate_runner_definitions(draw, number_of_runners):
    runner_definitions = []

    for i in range(number_of_runners):
        runner_definitions.append(
            draw(st.fixed_dictionaries({
                "status": st.sampled_from(RunnerStatus).map(lambda v: v.value),
                "id": st.integers(0, 50),
                "sortPriority": st.just(i + 1),
            }))
        )

    return runner_definitions


@composite
def generate_market_definition_from_prev_version(draw, mdf: BetfairMarketDefinition):
    return draw(st.fixed_dictionaries({
        "bspMarket": st.just(mdf["bspMarket"]),
        "turnInPlayEnabled": st.just(mdf["turnInPlayEnabled"]),
        "persistenceEnabled": st.just(mdf["persistenceEnabled"]),
        "marketBaseRate": st.just(mdf["marketBaseRate"]),
        "eventId": st.just(mdf["eventId"]),
        "eventTypeId": st.just(mdf["eventTypeId"]),
        "numberOfWinners": st.just(mdf["numberOfWinners"]),
        "bettingType": st.just(mdf["bettingType"]),
        "marketType": st.just(mdf["marketType"]),
        "marketTime": st.just(mdf["marketTime"]),
        "suspendTime": st.just(mdf["suspendTime"]),
        "bspReconciled": st.just(mdf["bspReconciled"]),
        "complete": st.just(mdf["complete"]),
        "inPlay": st.just(mdf["inPlay"]),
        "crossMatching": st.just(mdf["crossMatching"]),
        "runnersVoidable": st.just(mdf["runnersVoidable"]),
        "numberOfActiveRunners": st.just(mdf["numberOfActiveRunners"]),
        "betDelay": st.just(mdf["betDelay"]),
        "status": st.just(mdf["status"]),
        "runners": generate_runner_definitions(len(mdf["runners"])),
        "regulators": st.just(mdf["regulators"]),
        "countryCode": st.just(mdf["countryCode"]),
        "discountAllowed": st.just(mdf["discountAllowed"]),
        "timezone": st.just(mdf["timezone"]),
        "openDate": st.just(mdf["openDate"]),
        "version": st.just(mdf["version"]),
        "priceLadderDefinition": st.just(mdf["priceLadderDefinition"])
    }))


@composite
def market_definition(draw) -> BetfairMarketDefinition:
    number_of_runners = draw(st.integers(1, 20))

    runner_definitions = draw(generate_runner_definitions(number_of_runners))

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
def generate_single_market_update(draw, market_id: str, prev_market_definition: BetfairMarketDefinition):
    market_update = draw(st.fixed_dictionaries({
        "id": st.just(market_id),
        "marketDefinition": st.one_of(st.none(), generate_market_definition_from_prev_version(prev_market_definition))
    }))

    return draw(st.fixed_dictionaries({
        "op": st.just("mcm"),
        "pt": st.just(10000000001),
        "mc": st.just([market_update]),
    }))


@composite
def generate_initial_image(draw, market_ids: List[str]):
    market_update = draw(st.fixed_dictionaries({
        "id": st.just(market_ids[0]),
        "marketDefinition": market_definition()
    }))

    return draw(st.fixed_dictionaries({
        "op": st.just("mcm"),
        "pt": st.just(10000000000),
        "mc": st.just([market_update]),
        "img": st.just(True)
    }))


@composite
def generate_price_size(draw, ladders: int):
    price = st.floats(1.01, 1000).map(lambda p: round(p, 2))
    size = st.floats(0, 100000000000).map(lambda s: round(s, 2))

    price_sizes = draw(st.lists(st.tuples(price, size).map(list), max_size=ladders, unique_by=lambda u: u[0]))
    return sorted(price_sizes, key=lambda u: u[0])


@composite
def generate_runner_change(draw, selection_id):
    return draw(st.fixed_dictionaries({
        "id": st.just(selection_id)
    }, optional={
        "batb": st.one_of(st.none(), st.just([]), generate_price_size(3)),
    }))


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
                "rc": draw(generate_runner_change(selection_ids=[r["id"] for r in mdf["runners"]])),
            }
        ]

    return draw(
        st.fixed_dictionaries(
            {
                "op": st.just("mcm"),
                "pt": st.integers(0, 100),
                "mc": st.just(market_updates),
                "ct": st.just("SUB_IMAGE"),
                "img": st.just(True)
            }
        )
    )
