import hypothesis.strategies as st
from hypothesis.strategies import composite
import numpy as np


@composite
def price_size(draw):

    number_of_levels = draw(st.integers(min_value=0, max_value=3))

    levels = np.random.choice([0, 1, 2], size=number_of_levels, replace=False)

    price_size = []

    for l in levels:
        price_size.append(
            draw(
                st.tuples(
                    st.just(l),
                    st.floats(1.01, 1000).map(lambda i: round(i, 2)),
                    st.floats(0.0, 100000).map(lambda i: round(i, 2)),
                ).map(list)
            )
        )

    return price_size


@composite
def runner_change(draw, selection_id):

    return draw(
        st.fixed_dictionaries(
            {"id": st.just(selection_id), "batb": price_size(), "batl": price_size()}
        )
    )


@composite
def generate_market_definition(draw):

    number_of_runners = draw(st.integers(min_value=1, max_value=3))
    sort_priorities = range(1, number_of_runners + 1)

    selection_ids = np.random.choice(1000, size=len(sort_priorities), replace=False)

    return draw(
        st.fixed_dictionaries(
            {
                "status": st.sampled_from(["OPEN", "CLOSED", "SUSPENDED", "INACTIVE"]),
                "runners": st.just(
                    [
                        {"sortPriority": sp, "id": sid}
                        for sp, sid in zip(sort_priorities, selection_ids)
                    ]
                ),
            }
        )
    )


@composite
def generate_market_changes(draw, market_id, selection_ids):

    m = {
        "id": st.just(market_id),
    }

    size = draw(st.integers(0, len(selection_ids)))
    sels = list(np.random.choice(selection_ids, replace=False, size=size))

    rcs = []

    for i in sels:
        rcs.append(draw(runner_change(i)))

    if rcs:
        m["rc"] = st.just(rcs)

    return draw(st.fixed_dictionaries(m))


@composite
def generate_market_change_with_market_definition(draw):

    market_id = draw(st.integers(0, 10).map(lambda i: str("1." + str(i))))

    market_definition = draw(generate_market_definition())

    selection_ids = [r["id"] for r in market_definition["runners"]]

    m = {
        "id": st.just(market_id),
        "marketDefinition": st.just(market_definition),
        "img": st.just(True),
    }

    size = draw(st.integers(0, len(selection_ids)))
    sels = list(np.random.choice(selection_ids, replace=False, size=size))

    rcs = []

    for i in sels:
        rcs.append(draw(runner_change(i)))

    if rcs:
        m["rc"] = st.just(rcs)

    return draw(st.fixed_dictionaries(m))


@composite
def generate_sub_image(draw):

    return draw(
        st.fixed_dictionaries(
            {
                "op": st.just("mcm"),
                "ct": st.just("SUB_IMAGE"),
                "mc": st.lists(generate_market_change_with_market_definition(), min_size=0).map(
                    lambda ms: list({m["id"]: m for m in ms}.values())
                ),
            },
        )
    )
