from __future__ import annotations

import json
import logging
import socket
import ssl
from typing import List, Optional

import attr

from betfairstreamer.models.betfair_api import OP, BetfairAuthenticationMessage
from betfairstreamer.models.betfair_api_extensions import BetfairMessage
from betfairstreamer.stream.protocols import Connection
from betfairstreamer.stream.stream_parser import Parser
from betfairstreamer.utils import decode, encode

logger = logging.getLogger("betfair_connection")


def create_auth_message(auth_id: int, session_token: str, app_key: str) -> BetfairAuthenticationMessage:
    auth_message = BetfairAuthenticationMessage(
        op=OP.authentication.value, id=auth_id, session=session_token, appKey=app_key,
    )

    return auth_message


def create_betfair_socket() -> socket.socket:
    hostname = "stream-api.betfair.com"
    port = 443

    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)

    betfair_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    betfair_ssl_socket = ssl_context.wrap_socket(betfair_socket)

    betfair_ssl_socket.connect((hostname, port))

    return betfair_ssl_socket


@attr.s(auto_attribs=True, slots=True)
class BetfairConnection(Connection):
    app_key: str
    buffer_size: int = 8192
    parser: Parser = attr.Factory(Parser)
    connection: Optional[socket.socket] = None
    subscription_message: Optional[BetfairMessage] = None

    def read(self) -> List[bytes]:

        part = self.connection.recv(self.buffer_size)

        if part == b"":
            raise ConnectionError("Betfair closed connection.")

        return self.parser.parse_message(part)

    def get_socket(self) -> socket.socket:
        return self.connection

    def send(self, betfair_msg: BetfairMessage) -> None:
        assert self.connection is not None, "Socket cannot be None"
        self.connection.sendall(encode(betfair_msg))

    def close(self) -> None:
        if self.connection is not None and self.connection.fileno() != -1:
            self.connection.shutdown(socket.SHUT_RDWR)
            self.connection.close()
        else:
            self.connection = None

    def connect(self, session_token: str, subscription_message: BetfairMessage) -> None:
        self.close()
        self.connection = create_betfair_socket()

        self.subscription_message = subscription_message

        auth_message = create_auth_message(
            subscription_message["id"], session_token=session_token, app_key=self.app_key
        )

        connected_response = decode(self.read()[0])

        logger.info(connected_response)

        self.send(auth_message)

        auth_response = decode(self.read()[0])

        logger.info(auth_response)

        if auth_response["statusCode"] == "FAILURE":
            raise ConnectionError(auth_response["errorCode"])

        logger.debug(json.dumps(subscription_message))

        self.send(subscription_message)
        logger.info(f"Subscription, {decode(self.read()[0])['statusCode']}")
