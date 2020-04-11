from __future__ import annotations

import asyncio
import logging
import select
import socket
import ssl
from asyncio import StreamReader, StreamWriter
from typing import Any, Dict, Generator, List, Tuple, Union

import attr
import orjson

from betfairstreamer.betfair_api import (
    OP,
    BetfairAuthenticationMessage,
    BetfairMarketSubscriptionMessage,
    BetfairOrderSubscriptionMessage,
)

BetfairMessage = Union[
    BetfairAuthenticationMessage, BetfairMarketSubscriptionMessage, BetfairOrderSubscriptionMessage,
]


def encode(msg: BetfairMessage) -> bytes:
    return orjson.dumps(msg) + b"\r\n"


def decode(msg: bytes) -> Dict[Any, Any]:
    return orjson.loads(msg)


def create_betfair_socket() -> socket.socket:
    hostname = "stream-api.betfair.com"
    port = 443

    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)

    betfair_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    betfair_ssl_socket = ssl_context.wrap_socket(betfair_socket)

    betfair_ssl_socket.connect((hostname, port))

    return betfair_ssl_socket


async def create_async_socket() -> Tuple[StreamReader, StreamWriter]:
    hostname = "stream-api.betfair.com"
    port = 443

    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.check_hostname = False

    return await asyncio.open_connection(*(hostname, port), ssl=ssl_context)


class Parser:
    def __init__(self) -> None:
        self.buffer = b""
        self.crlf = b"\r\n"

    def parse_message(self, part: bytes) -> List[bytes]:
        messages = []

        if part == b"":
            raise ConnectionError("Betfair closed connection.")

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


@attr.s(auto_attribs=True, slots=True)
class BetfairAsyncConnection:
    reader: StreamReader
    writer: StreamWriter
    parser: Parser = attr.Factory(Parser)

    async def read(self) -> List[bytes]:
        part = await self.reader.read(8192)
        return self.parser.parse_message(part)

    async def send(self, msg: BetfairMessage) -> None:
        self.writer.write(encode(msg))
        await self.writer.drain()

    @classmethod
    async def create_connection(
        cls, subscription_message: BetfairMessage, session_token: str, app_key: str
    ) -> BetfairAsyncConnection:
        reader, writer = await create_async_socket()
        connection = cls(reader=reader, writer=writer)

        print(await connection.read())

        auth_message = BetfairAuthenticationMessage(
            op=OP.authentication.value,
            id=subscription_message["id"],
            session=session_token,
            appKey=app_key,
        )

        await connection.send(auth_message)
        print(await connection.read())

        await connection.send(subscription_message)
        print(await reader.readuntil(b"\r\n"))

        return connection


@attr.s(auto_attribs=True, slots=True)
class BetfairConnection:
    connection: socket.socket
    buffer_size: int = 8192
    parser: Parser = attr.Factory(Parser)

    def read(self) -> List[bytes]:
        part = self.connection.recv(self.buffer_size)
        return self.parser.parse_message(part)

    def send(self, betfair_msg: BetfairMessage) -> None:
        self.connection.sendall(encode(betfair_msg))

    @classmethod
    def create_connection(
        cls,
        subscription_message: Union[
            BetfairMarketSubscriptionMessage, BetfairOrderSubscriptionMessage
        ],
        session_token: str,
        app_key: str,
    ) -> BetfairConnection:
        auth_message = BetfairAuthenticationMessage(
            op=OP.authentication.value,
            id=subscription_message["id"],
            session=session_token,
            appKey=app_key,
        )

        betfair_ssl_socket = create_betfair_socket()
        connection = cls(betfair_ssl_socket)

        logging.info(connection.read()[0])

        betfair_ssl_socket.sendall(encode(auth_message))
        logging.info(connection.read()[0])

        betfair_ssl_socket.sendall(encode(subscription_message))
        logging.info(connection.read()[0])

        return connection


@attr.s(auto_attribs=True)
class BetfairConnectionPool:
    poller: select.poll = attr.ib(factory=select.poll)
    connections: Dict[int, BetfairConnection] = attr.ib(factory=dict)

    def add_connection(self, betfair_connection: BetfairConnection) -> None:
        self.poller.register(betfair_connection.connection, select.POLLIN)
        self.connections[betfair_connection.connection.fileno()] = betfair_connection

    def read(self) -> Generator[bytes, None, None]:
        while True:
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
        subscription_messages: List[
            Union[BetfairMarketSubscriptionMessage, BetfairOrderSubscriptionMessage]
        ],
        session_token: str,
        app_key: str,
    ) -> BetfairConnectionPool:
        connection_pool = cls()

        for subscription_message in subscription_messages:
            connection_pool.add_connection(
                BetfairConnection.create_connection(subscription_message, session_token, app_key)
            )

        return connection_pool
