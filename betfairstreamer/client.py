import attr
import orjson
import zmq

from betfairstreamer.resources.api_messages import MarketSubscriptionMessage


@attr.s
class BetfairAPIClient:

    client_socket = attr.ib()
    state_socket = attr.ib()
    sub_socket = attr.ib()

    def subscribe(self, name: str, subscription_message: MarketSubscriptionMessage):
        self.client_socket.send(
            orjson.dumps(  # pylint: disable=I1101
                {
                    "op": "subscription",
                    "name": name,
                    "subscription_message": subscription_message.to_dict(),
                }
            ),
            zmq.NOBLOCK,  # pylint: disable=no-member
        )

    def get_market_cache(self):
        self.state_socket.send(b"GIVE ME STATE")
        return self.state_socket.recv_pyobj()

    def get_sub_socket(self):
        self.sub_socket.connect("tcp://127.0.0.1:5557")
        return self.sub_socket

    @classmethod
    def create_betfair_api(cls):
        context = zmq.Context.instance()
        client_socket = context.socket(zmq.PAIR)  # pylint: disable=no-member
        client_socket.connect("tcp://127.0.0.1:5556")

        state_socket = context.socket(zmq.PAIR)  # pylint: disable=no-member
        state_socket.connect("tcp://127.0.0.1:5555")

        sub_socket = context.socket(zmq.SUB)  # pylint: disable=no-member
        sub_socket.setsockopt(zmq.SUBSCRIBE, b"")  # pylint: disable=no-member

        return cls(client_socket=client_socket, state_socket=state_socket, sub_socket=sub_socket)
