from __future__ import annotations

import logging
import socket
import ssl
from typing import Any, Dict, List, Union

import attr
import orjson

from betfairstreamer.models.betfair_api import (
    OP,
    BetfairAuthenticationMessage,
    BetfairMarketSubscriptionMessage,
    BetfairOrderSubscriptionMessage,
)
from betfairstreamer.stream.stream_parser import Parser

BetfairMessage = Union[BetfairAuthenticationMessage, BetfairMarketSubscriptionMessage, BetfairOrderSubscriptionMessage]


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


@attr.s(auto_attribs=True, slots=True)
class BetfairConnection:
    connection: socket.socket
    buffer_size: int = 8192
    parser: Parser = attr.Factory(Parser)

    def read(self) -> List[bytes]:
        part = self.connection.recv(self.buffer_size)

        if part == b"":
            raise ConnectionError("Betfair closed connection.")

        return self.parser.parse_message(part)

    def send(self, betfair_msg: BetfairMessage) -> None:
        self.connection.sendall(encode(betfair_msg))

    @classmethod
    def create_connection(
        cls,
        subscription_message: Union[BetfairMarketSubscriptionMessage, BetfairOrderSubscriptionMessage],
        session_token: str,
        app_key: str,
    ) -> BetfairConnection:
        auth_message = BetfairAuthenticationMessage(
            op=OP.authentication.value, id=subscription_message["id"], session=session_token, appKey=app_key,
        )

        betfair_ssl_socket = create_betfair_socket()
        connection = cls(betfair_ssl_socket)

        logging.info(connection.read()[0])

        betfair_ssl_socket.sendall(encode(auth_message))
        logging.info(connection.read()[0])

        betfair_ssl_socket.sendall(encode(subscription_message))
        logging.info(connection.read()[0])

        return connection
