""""Server for Betfair Exchange Stream API, receives and publishes messages from Betfair."""

import json
import logging
import os
import select
import socket
import ssl
from typing import Dict, List, Union

import attr
import orjson
from betfairlightweight import APIClient

from betfairstreamer.resources.api_messages import (
    MarketSubscriptionMessage,
    OrderSubscriptionMessage,
    AuthenticationMessage,
    ConnectionMessage,
    StatusMessage,
)

logging.basicConfig(level=logging.INFO)


def create_socket(hostname: str, port: int, cert_path: str) -> socket.socket:
    """Create a SSLSocket, connects to betfair"""

    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH, capath=cert_path)

    betfair_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    betfair_ssl_socket = ssl_context.wrap_socket(betfair_socket)

    betfair_ssl_socket.connect((hostname, port))

    return betfair_ssl_socket


def decode_message(msg: bytes) -> Dict:
    return orjson.loads(msg)


def encode_message(msg: Dict) -> bytes:
    return json.dumps(msg).encode("utf-8") + b"\r\n"


@attr.s
class BetfairConnection:
    """
    Interface to an underlying betfair connection. Handles correct formatting for recieving and
    sending messages to betfair exchange stream API.
    """

    socket = attr.ib()
    crlf = attr.ib(type=bytes, default=b"\r\n")
    buffer = attr.ib(type=bytes, default=b"")
    read_buffer_size = attr.ib(type=int, default=4096)

    def close(self) -> None:
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()

    def send(self, msg: Dict):
        self.socket.send(encode_message(msg))

    def receive(self) -> List[bytes]:
        """
        Called when there are bytes to be read from socket.

        If separator ( b'\r\n' ) is found, append to previously incomplete cached message and add to updated list,
        continue to parse rest of bytes to see if there are any other messages.

        If separator is not found then all messages have been parsed, save the reminder past the last \r\n as incomplete message.\
        Returns: list of ResponseMessages byte encoded.
        """

        # Should only timeout if not using a poller
        try:
            part = self.socket.recv(self.read_buffer_size)
        except socket.timeout:
            raise

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

    @classmethod
    def create_betfair_connection(cls):
        s = create_socket("stream-api.betfair.com", 443, "./certs")
        connection = cls(s)
        return authenticate_connection(connection)


@attr.s
class ConnectionHandler:

    poller = attr.ib(factory=select.poll)

    connections = attr.ib(type=Dict[int, BetfairConnection], factory=dict)
    message_handler = attr.ib(default=lambda m: print(m))

    def subscribe(
        self,
        subscription_messages: List[Union[MarketSubscriptionMessage, OrderSubscriptionMessage]],
    ) -> None:

        for subscription_message in subscription_messages:

            connection = BetfairConnection.create_betfair_connection()
            connection.send(subscription_message.to_dict())

            logging.info(StatusMessage.from_stream_message(orjson.loads(connection.receive()[0])))

            self.add_connection(connection)

        self.read_loop()

    def add_connection(self, connection: BetfairConnection) -> None:
        self.poller.register(connection.socket, select.POLLIN)
        self.connections[connection.socket.fileno()] = connection

    def read_loop(self) -> None:
        while True:
            for fd, event in self.poller.poll(1):
                for m in self.connections[fd].receive():
                    self.message_handler(m)


def authenticate_connection(connection: BetfairConnection) -> BetfairConnection:
    """ Authenticate BetfairConnection instance to betfair.
    Example:
    connection = AuthenticationProvider.create_authentication_provider().authenticate(connection)

    Returns: BetfairConnection, authneticated with Betfair.
    """

    username: str = os.environ["USERNAME"]
    password: str = os.environ["PASSWORD"]
    app_key: str = os.environ["APP_KEY"]
    cert_path: str = os.environ["CERT_PATH"]

    trading: APIClient = APIClient(username, password, app_key, locale="sweden", certs=cert_path)

    trading.login()

    auth_message = AuthenticationMessage(
        id=1, session=trading.session_token, app_key=trading.app_key,
    )

    logging.info(auth_message)

    connection.send(auth_message.to_dict())

    logging.info(ConnectionMessage.from_stream_message(orjson.loads(connection.receive()[0])))

    logging.info(StatusMessage.from_stream_message(orjson.loads(connection.receive()[0])))

    return connection
