from __future__ import annotations

import select
import socket
import ssl
from typing import Dict, Generator, List, Type, Union

import attr
import orjson

from betfairstreamer.betfair.enums import OP
from betfairstreamer.betfair.models import (
    AuthenticationMessage,
    BetfairMessage,
    MarketSubscriptionMessage,
    OrderSubscriptionMessage,
)


def encode(msg: BetfairMessage) -> bytes:
    return orjson.dumps(msg.to_dict()) + b"\r\n"


@attr.s(auto_attribs=True)
class BetfairConnection:

    connection: socket.socket
    buffer_size: int = 8192
    crlf: bytes = b"\r\n"
    buffer: bytes = b""

    def read(self) -> List[bytes]:

        part = self.connection.recv(self.buffer_size)

        if part == b"":
            raise ConnectionError("Socket closed!")

        self.buffer = self.buffer + part

        before, sep, after = self.buffer.partition(self.crlf)

        messages = []

        while sep == self.crlf:
            messages.append(before)

            before, sep, after = after.partition(self.crlf)

        self.buffer = before

        return messages

    def send(self, betfair_msg: BetfairMessage) -> None:
        self.connection.sendall(encode(betfair_msg))

    @classmethod
    def create_connection(
        cls: Type[BetfairConnection],
        subscription_message: Union[MarketSubscriptionMessage, OrderSubscriptionMessage],
        session_token: str,
        app_key: str,
    ) -> BetfairConnection:

        hostname = "stream-api.betfair.com"
        port = 443
        cert_path = "./certs"

        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH, capath=cert_path)

        betfair_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        betfair_ssl_socket = ssl_context.wrap_socket(betfair_socket)

        betfair_ssl_socket.connect((hostname, port))

        auth_message = AuthenticationMessage(
            op=OP.authentication,
            id=subscription_message.id,
            session=session_token,
            app_key=app_key,
        )

        betfair_ssl_socket.sendall(encode(auth_message))
        betfair_ssl_socket.sendall(encode(subscription_message))

        return cls(betfair_ssl_socket)


@attr.s(auto_attribs=True)
class BetfairConnectionPool:
    poller: select.poll = attr.ib(factory=select.poll)
    connections: Dict[int, BetfairConnection] = attr.ib(factory=dict)

    def add_connection(self, betfair_connection: BetfairConnection) -> None:
        self.poller.register(betfair_connection.connection, select.POLLIN)
        self.connections[betfair_connection.connection.fileno()] = betfair_connection

    def read(self) -> Generator[List[bytes], None, None]:
        events = self.poller.poll()

        for fd, e in events:
            yield self.connections[fd].read()


@attr.s(auto_attribs=True)
class FileStreamer:

    path: str

    def read(self) -> Generator[List[bytes], None, None]:
        pass
