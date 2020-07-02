from typing import Any, Tuple

import hypothesis.strategies as st
from hypothesis import given
from hypothesis.strategies import composite

from betfairstreamer.models.market_book import FULL_PRICE_LADDER_INDEX, BETFAIR_TICKS

prices = list(FULL_PRICE_LADDER_INDEX.keys())


@composite
def generate_message(draw: Any) -> Tuple[int, bytes, str]:
    i = draw(st.integers(min_value=1, max_value=100))

    msg = ""

    for _ in range(i):
        msg += draw(st.text()) + "\r\n"

    return len(msg.split("\r\n")[:-1]), msg.encode("utf-8"), msg


@composite
def price_size(draw, min_price, max_price):
    min_price_index = FULL_PRICE_LADDER_INDEX[min_price]
    max_price_index = FULL_PRICE_LADDER_INDEX[max_price]

    ps = st.tuples(
        st.sampled_from(BETFAIR_TICKS[min_price_index:max_price_index]),
        st.floats(min_value=0.1, max_value=1000000).map(lambda v: round(v, 2)),
    ).map(list)

    return draw(ps)


@composite
def generate_full_price_ladder(draw):
    price_back = sorted(
        draw(st.lists(price_size(1.01, 1000), unique_by=lambda ps: ps[0])),
        key=lambda l: l[0],
        reverse=True,
    )
    price_lay = []

    if price_back:
        min_lay_price = price_back[0][0]

        if min_lay_price < 1000:
            price_lay = sorted(
                draw(
                    st.lists(
                        price_size(min_price=min_lay_price, max_price=1000),
                        unique_by=lambda ps: ps[0],
                    )
                ),
                key=lambda l: l[0],
            )

    return price_back, price_lay


@composite
def generate_index_ladder(draw):
    back, lay = draw(generate_full_price_ladder())

    back = [[i] + v for i, v in enumerate(back)]
    lay = [[i] + v for i, v in enumerate(lay)]

    return back, lay


@composite
def generate_runner(draw, sort_priority, selection_id):
    runner = st.fixed_dictionaries(
        {
            "sortPriority": st.just(sort_priority),
            "id": st.just(selection_id),
            "status": st.sampled_from(
                [
                    "ACTIVE",
                    "WINNER",
                    "LOSER",
                    "REMOVED",
                    "REMOVED_VACANT",
                    "HIDDEN",
                    "PLACED",
                    "HIDDEN",
                    "PLACED",
                ]
            ),
        },
        optional={
            "removalDate": st.datetimes().map(lambda d: d.isoformat()),
            "adjustmentFactor": st.floats(0, 10).map(lambda v: round(v, 2)),
            "bsp": st.floats(0, 10).map(lambda v: round(v, 2)),
        },
    )

    return draw(runner)


@composite
def generate_runners(draw):
    number_of_runners = draw(st.integers(min_value=2, max_value=20))

    sort_priorities = range(number_of_runners)
    selection_ids = draw(
        st.lists(
            st.integers(min_value=1, max_value=1000000),
            min_size=number_of_runners,
            max_size=number_of_runners,
        )
    )

    runners = []

    for sort_priority, selection_id in zip(sort_priorities, selection_ids):
        runners.append(draw(generate_runner(sort_priority, selection_id)))

    return runners

@composite
def generate_market_definition(draw):

    market_definition = st.fixed_dictionaries({
        "eventId": st.integers(min_value=10000, max_value=10000000),
        "runners": generate_runners()
    })

    return draw(market_definition)

@composite
def generate_runner_changes(draw, selection_id):

    runner_changes = st.fixed_dictionaries({
        "id": st.just(selection_id),
    }, optional={
        **{}
    })

    return draw(runner_changes)

@composite
def generate_market_change_image(draw):

    market_definition = draw(generate_market_definition())

    market_change = st.fixed_dictionaries({
        "id": st.integers(min_value=0, max_value=10).map(lambda v: "1." + str(v)),
        "marketDefinition": st.just(market_definition),
        "rc": generate_runner_changes(1),
        "img": st.just(True)
    })

    return draw(market_change)


@given(generate_index_ladder(), generate_market_change_image())
def test_something(price_sizes, market_definition):
    back, lay = price_sizes

    print("BACK, ", back)
    print("LAY , ", lay)
    print(market_definition)
