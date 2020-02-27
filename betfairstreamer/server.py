""""Server for Betfair Exchange Stream API, receives and publishes messages from Betfair."""

import json
import logging
import os
import socket
import ssl
import threading
from typing import Dict, List

import attr
import orjson
import zmq
from betfairlightweight import APIClient

from betfairstreamer.resources.api_messages import (
    AuthenticationMessage,
    ConnectionMessage,
    StatusCode,
    StatusMessage,
)
from betfairstreamer.resources.market_cache import MarketCache
import time

context = zmq.Context()
poller = zmq.Poller()

logging.basicConfig(level=logging.INFO)


USERNAME: str = os.environ["USERNAME"]
PASSWORD: str = os.environ["PASSWORD"]
APP_KEY: str = os.environ["APP_KEY"]

trading: APIClient = APIClient(USERNAME, PASSWORD, APP_KEY, locale="sweden")


@attr.s
class BetfairConnection:
    """
    Interface to an underlying betfair connection. Handles correct formatting for recieving and
    sending messages to betfair exchange stream API.
    """

    id = attr.ib(type=int, default=1)
    cert_path = attr.ib(type=str, default=os.environ["CERT_PATH"])
    hostname = attr.ib(type=str, default="stream-api.betfair.com")
    port = attr.ib(type=int, default=443)
    socket = attr.ib(default=None)
    crlf = attr.ib(type=bytes, default=b"\r\n")
    connection_id = attr.ib(type=str, default=None)
    buffer = attr.ib(type=bytes, default=b"")

    def connect(self, buffer_size=33554432):
        """
        Create a SSLSocket, connects to betfair
        """

        ssl_context = ssl.create_default_context(
            ssl.Purpose.CLIENT_AUTH, capath=self.cert_path
        )

        betfair_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        betfair_ssl_socket = ssl_context.wrap_socket(betfair_socket)

        betfair_ssl_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, buffer_size)
        betfair_ssl_socket.connect((self.hostname, self.port))

        self.socket = betfair_ssl_socket

        byte_message = self.recieve()
        json_message = orjson.loads(byte_message[0])  # pylint: disable=I1101

        connection_message = ConnectionMessage.from_stream_message(json_message)
        self.connection_id = connection_message.connection_id

        logging.info(connection_message)

    def close(self) -> None:
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()

    def send(self, msg):
        if not isinstance(msg, dict):
            msg = msg.to_dict()

        msg["id"] = self.id
        self.id += 1

        byte_msg = json.dumps(msg).encode("utf-8") + self.crlf

        self.socket.send(byte_msg)

    def recieve(self) -> List[bytes]:
        """
        Called when there are bytes to be read from socket.

        If separator ( b'\r\n' ) is found, append to previously incomplete cached message and add to updated list,
        continue to parse rest of bytes to see if there are any other messages.

        If separator is not found then all messages have been parsed, save the reminder past the last \r\n as incomplete message.\
        Returns: list of ResponseMessages byte encoded.
        """

        part = self.socket.recv(4096)

        if part == b"":
            raise ConnectionError()

        before, sep, after = part.partition(self.crlf)

        messages = []

        while sep == self.crlf:
            self.buffer += before
            messages.append(self.buffer)

            self.buffer = b""

            before, sep, after = after.partition(self.crlf)

        self.buffer += before

        return messages

    @classmethod
    def create_connection(cls):
        """Create BetfairConnection instance, connect it to betfair, needs to be authenticated to be able to send,
        subscription messages and receive stream updates.

        Returns: BetfairConnection (socket connected to Betfair)
        """

        connection = cls()
        connection.connect()
        return authenticate_connection(connection)


def authenticate_connection(connection: BetfairConnection) -> BetfairConnection:
    """ Authenticate BetfairConnection instance to betfair.
    Example:
    connection = AuthenticationProvider.create_authentication_provider().authenticate(connection)

    Returns: BetfairConnection, authneticated with Betfair.
    """

    if trading.session_expired:
        trading.login()

    auth_message = AuthenticationMessage(
        id=1, session=trading.session_token, app_key=trading.app_key,
    )

    logging.info(auth_message)

    connection.send(auth_message.to_dict())

    status_msg = orjson.loads(connection.recieve()[0])  # pylint: disable=I1101
    status_msg = StatusMessage.from_stream_message(status_msg)

    logging.info(status_msg)

    return connection


@attr.s
class ConnectionHandler:
    connections = attr.ib(type=Dict[int, BetfairConnection], factory=dict)

    poller = attr.ib(type=zmq.Poller, factory=zmq.Poller)

    connection_messages = attr.ib(type=List[Dict], factory=list)

    def create_connections(self, subscription_messages: Dict):
        self.connection_messages = []

        for subscription_message in subscription_messages:
            self.connection_messages.append(subscription_message)

            connection = BetfairConnection.create_connection()
            connection.send(subscription_message)

            logging.info(
                StatusMessage.from_stream_message(orjson.loads(connection.recieve()[0]))
            )

            self.connections[connection.socket.fileno()] = connection
            self.poller.register(connection.socket, zmq.POLLIN)

    def close_all_connections(self):

        for k, v in self.connections.items():
            self.poller.unregister(v.socket)
            v.socket.shutdown(socket.SHUT_RDWR)
            v.socket.close()

    def get_connection(self, fd: int):
        return self.connections[fd]


@attr.s
class APIServer:

    pub_socket = attr.ib(type=zmq.Socket, default=None)
    api_socket = attr.ib(type=zmq.Socket, default=None)

    read_loop_thread = attr.ib(type=threading.Thread, default=None)

    connection_handler = attr.ib(type=ConnectionHandler, factory=ConnectionHandler)

    running = attr.ib(type=bool, default=False)

    def read_loop(self):
        while self.running:
            for fd, _ in self.connection_handler.poller.poll():
                for m in self.connection_handler.get_connection(fd).recieve():
                    self.pub_socket.send(m)

        self.connection_handler.close_all_connections()

    def start(self):
        logging.info("WAITING FOR SUBSCRIPTIONS")
        while True:
            msg = orjson.loads(self.api_socket.recv())

            if msg["op"] == "subscription":
                self.start_everything(msg)

            if msg["op"] == "unsubscribe":
                self.close_everything()

            if msg["op"] == "list":
                self.api_socket.send(
                    orjson.dumps(self.connection_handler.connection_messages)
                )

    def start_everything(self, msg):
        if self.running:
            self.close_everything()

        self.running = True
        self.connection_handler.create_connections(msg["subscription_messages"])
        self.read_loop_thread = threading.Thread(target=self.read_loop)
        self.read_loop_thread.start()

    def close_everything(self):
        logging.info("STOPPING ALL STREAMS ...")

        if self.running:
            self.running = False
            self.read_loop_thread.join()

            logging.info("SUCCESSFULLY CLOSED ALL STREAMS! ")

    @classmethod
    def create_api_server(cls):
        context = zmq.Context.instance()

        api_socket = context.socket(zmq.PAIR)
        api_socket.bind("tcp://127.0.0.1:5556")

        pub_socket = context.socket(zmq.PUB)
        pub_socket.bind("tcp://127.0.0.1:5557")

        threading.Thread(
            target=cls(api_socket=api_socket, pub_socket=pub_socket).start
        ).start()


if __name__ == "__main__":
    api_server = APIServer.create_api_server()
