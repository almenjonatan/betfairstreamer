from __future__ import annotations

import logging
import select
import socket
import ssl
from typing import Any, Dict, Generator, List, Type, Union

import attr
import orjson

from betfairstreamer.betfair.enums import OP
from betfairstreamer.betfair.models import (
    AuthenticationMessage,
    BetfairMessage,
    ConnectionMessage,
    MarketSubscriptionMessage,
    OrderSubscriptionMessage,
    StatusMessage,
)


def encode(msg: BetfairMessage) -> bytes:
    return orjson.dumps(msg.to_dict()) + b"\r\n"


def decode(msg: bytes) -> Any:
    return orjson.loads(msg)


def create_betfair_socket(cert_path: str) -> socket.socket:
    hostname = "stream-api.betfair.com"
    port = 443

    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH, capath=cert_path)

    betfair_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    betfair_ssl_socket = ssl_context.wrap_socket(betfair_socket)

    betfair_ssl_socket.connect((hostname, port))

    return betfair_ssl_socket


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

        messages = []

        if part[:1] == b"\n" and self.buffer[-1:] == b"\r":
            messages.append(self.buffer[:-1])
            self.buffer = b""
            part = part[1:]

        before, sep, after = part.partition(self.crlf)

        before = self.buffer + before

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
        cert_path: str = "./certs",
    ) -> BetfairConnection:

        auth_message = AuthenticationMessage(
            op=OP.authentication,
            id=subscription_message.id,
            session=session_token,
            app_key=app_key,
        )

        betfair_ssl_socket = create_betfair_socket(cert_path)

        betfair_ssl_socket.sendall(encode(auth_message))
        betfair_ssl_socket.sendall(encode(subscription_message))

        logging.info(ConnectionMessage.from_betfair(decode(betfair_ssl_socket.recv(4096))))
        logging.info(StatusMessage.from_betfair(decode(betfair_ssl_socket.recv(4096))))

        return cls(betfair_ssl_socket)


@attr.s(auto_attribs=True)
class BetfairConnectionPool:
    poller: select.poll = attr.ib(factory=select.poll)
    connections: Dict[int, BetfairConnection] = attr.ib(factory=dict)

    def add_connection(self, betfair_connection: BetfairConnection) -> None:
        self.poller.register(betfair_connection.connection, select.POLLIN)
        self.connections[betfair_connection.connection.fileno()] = betfair_connection

    def read(self) -> Generator[bytes, None, None]:
        events = self.poller.poll()

        for fd, e in events:
            for m in self.connections[fd].read():
                yield m

    def close(self) -> None:
        for k, c in self.connections.items():
            c.connection.shutdown(socket.SHUT_RDWR)
            c.connection.close()

    @classmethod
    def create_connection_pool(
        cls,
        subscription_messages: List[Union[MarketSubscriptionMessage, OrderSubscriptionMessage]],
        session_token: str,
        app_key: str,
    ) -> BetfairConnectionPool:
        connection_pool = cls()

        for subscription_message in subscription_messages:
            connection_pool.add_connection(
                BetfairConnection.create_connection(subscription_message, session_token, app_key)
            )

        return connection_pool
