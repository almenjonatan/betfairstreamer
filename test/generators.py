from typing import Any, Tuple

import hypothesis.strategies as st
from hypothesis.strategies import composite

from betfairstreamer.models.betfair_api import (
    BetfairMarketChangeMessage,
    BetfairMarketDefinition,
    RunnerStatus,
)


@composite
def generate_message(draw: Any) -> Tuple[int, bytes, str]:
    i = draw(st.integers(min_value=1, max_value=100))

    msg = ""

    for _ in range(i):
        msg += draw(st.text()) + "\r\n"

    return len(msg.split("\r\n")[:-1]), msg.encode("utf-8"), msg


@composite
def generate_runner_definitions(draw, number_of_runners):

    assert number_of_runners <= 20

    runner_definitions = []

    selection_ids = draw(
        st.lists(st.integers(1, 1000), min_size=2, max_size=20, unique=True)
    )

    for index, selection_id in enumerate(selection_ids):
        runner_definitions.append(
            draw(
                st.fixed_dictionaries(
                    {
                        "status": st.sampled_from(RunnerStatus).map(lambda v: v.value),
                        "id": st.just(selection_id),
                        "sortPriority": st.just(index + 1),
                    }
                )
            )
        )

    return runner_definitions


@composite
def generate_market_definition_from_prev_version(draw, mdf: BetfairMarketDefinition):
    return draw(
        st.fixed_dictionaries(
            {
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
                "priceLadderDefinition": st.just(mdf["priceLadderDefinition"]),
            }
        )
    )


@composite
def market_definition_generator(draw) -> BetfairMarketDefinition:
    number_of_runners = draw(st.integers(2, 20))

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
            "numberOfActiveRunners": st.integers(2, number_of_runners),
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
def market_update_generator(draw):
    return draw(
        st.builds(
            BetfairMarketChangeMessage,
            op=st.just("mcm"),
            pt=st.integers(0, 100),
            mc=st.just([]),
        )
    )
