import attr
import zmq
import json
import orjson
from typing import List, Union

from betfairstreamer.resources.api_messages import (
    MarketSubscriptionMessage,
    OrderSubscriptionMessage,
)


@attr.s
class BetfairAPIClient:

    api_socket = attr.ib()
    sub_socket = attr.ib()

    def subscribe(
        self,
        subscription_messages: List[
            Union[MarketSubscriptionMessage, OrderSubscriptionMessage]
        ],
    ):
        self.api_socket.send(
            json.dumps(  # pylint: disable=I1101
                {
                    "op": "subscription",
                    "subscription_messages": [
                        s.to_dict() for s in subscription_messages
                    ],
                }
            ).encode("utf-8")
        )

        return self.sub_socket

    def unsubscribe(self):
        self.api_socket.send(
            json.dumps({"op": "unsubscribe"}).encode("utf-8")  # pylint: disable=I1101
        )

    def list_streams(self):
        self.api_socket.send(orjson.dumps({"op": "list"}))

        print(json.dumps(json.loads(self.api_socket.recv()), indent=4))

    @classmethod
    def create_betfair_api(cls):
        context = zmq.Context.instance()

        api_socket = context.socket(zmq.PAIR)  # pylint: disable=no-member
        api_socket.connect("tcp://127.0.0.1:5556")

        sub_socket = context.socket(zmq.SUB)  # pylint: disable=no-member
        sub_socket.setsockopt(zmq.SUBSCRIBE, b"")
        sub_socket.connect("tcp://127.0.0.1:5557")

        return cls(api_socket=api_socket, sub_socket=sub_socket)
