from collections import defaultdict

from betfairstreamer.betfair.definitions import (
    LimitOrderDict,
    OrderChange,
    OrderChangeMessage,
    OrderDict,
    OrderRunnerChange,
    PlaceInstruction,
    PlaceInstructionDict,
)
from betfairstreamer.betfair.enums import OrderStatus, PersistenceType, Side
from betfairstreamer.cache.order_cache import OrderCache


def create_order(place_instruction: PlaceInstructionDict) -> OrderDict:
    return OrderDict(
        side=place_instruction["side"],
        sv=0,
        pt=PersistenceType.P.value,
        p=place_instruction["limitOrder"]["price"],
        sc=0,
        ot=place_instruction["orderType"],
        rc="SWE",
        s=place_instruction["limitOrder"]["size"],
        sl=0,
        sm=0,
        pd=12323,
        rfo=None,
        rac="",
        md=None,
        avp=0,
        id="123123123",
        lsrc="",
        ld=None,
        bsp=0,
        rfs="",
        status=OrderStatus.E.value,
        sr=place_instruction["limitOrder"]["size"],
    )


def create_order_runner_range(place_instruction: PlaceInstruction) -> OrderChangeMessage:
    selection_id_mapping = defaultdict(list)

    for p in place_instruction["instructions"]:
        selection_id_mapping[p["selectionId"]].append(p)

    order_changes = []

    for selection_id, instructions in selection_id_mapping.items():
        order_changes.append(
            OrderChange(
                id=place_instruction["marketId"],
                orc=[
                    OrderRunnerChange(id=selection_id, uo=[create_order(p) for p in instructions])
                ],
            )
        )

    return order_changes


def create_order_change_message(place_instruction: PlaceInstruction):
    return OrderChangeMessage(op="ocm", oc=create_order_runner_range(place_instruction))


if __name__ == "__main__":
    i = PlaceInstruction(
        marketId="1.2",
        instructions=[
            PlaceInstructionDict(
                orderType="LIMIT",
                selectionId=123,
                side="BACK",
                limitOrder=LimitOrderDict(price=1.25, size=50),
            ),
            PlaceInstructionDict(
                orderType="LIMIT",
                selectionId=123,
                side="LAY",
                limitOrder=LimitOrderDict(price=1.25, size=50),
            ),
            PlaceInstructionDict(
                orderType="LIMIT",
                selectionId=1234,
                side="LAY",
                limitOrder=LimitOrderDict(price=5.0, size=50),
            ),
        ],
    )

    oc = OrderCache()

    change_message = create_order_change_message(i)

    print(oc(change_message))
    print(oc)
    print(oc.get_size_remaining("1.2", selection_id=123, side=Side.BACK))
