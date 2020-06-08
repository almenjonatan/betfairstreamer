from __future__ import annotations

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

logger = logging.getLogger("BETFAIR_CONNECTION")
logger.setLevel(logging.DEBUG)

c_handler = logging.StreamHandler()
c_handler.setLevel(logging.INFO)

c_format = logging.Formatter(fmt="%(asctime)s:%(name)s:%(message)s")
c_handler.setFormatter(c_format)

logger.addHandler(c_handler)


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
    buffer_size: int = 8192
    parser: Parser = attr.Factory(Parser)
    connection: Optional[socket.socket] = None
    subscription_message: Optional[BetfairMessage] = None

    def read(self) -> List[bytes]:

        assert self.connection is not None, "Must have a socket"

        part = self.connection.recv(self.buffer_size)

        if part == b"":
            raise ConnectionError("Betfair closed connection.")

        return self.parser.parse_message(part)

    def get_socket(self) -> socket.socket:
        assert self.connection is not None, "Socket cannot be None"

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

    def connect(self, session_token: str, app_key: str, subscription_message: BetfairMessage) -> None:
        self.close()
        self.connection = create_betfair_socket()

        auth_message = create_auth_message(subscription_message["id"], session_token=session_token, app_key=app_key)

        connected_response = decode(self.read()[0])
        logger.info(f'Connected, connection id: {connected_response["connectionId"]}')

        logger.info(f"authenticating ...")
        self.send(auth_message)

        auth_response = decode(self.read()[0])

        logger.info(
            f'authentication, {auth_response["statusCode"]}, connections available: {auth_response["connectionsAvailable"]}'
        )
        logger.info("Sending subscription message ...")
        self.send(subscription_message)
        logger.info(f"Subscribed, {decode(self.read()[0])['statusCode']}")
