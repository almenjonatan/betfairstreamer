""""Server for Betfair Exchange Stream API, receives and publishes messages from Betfair."""

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
import json

zmq.Context()
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

    name = attr.ib(type=str)
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
    def create_connection(cls, name):
        """Create BetfairConnection instance, connect it to betfair, needs to be authenticated to be able to send,
        subscription messages and receive stream updates.

        Returns: BetfairConnection (socket connected to Betfair)
        """

        connection = cls(name=name)
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


def state_manager():
    """
    Keeping track of updates from betfair. Handles new clients joining late sends a snapshot
    of the current market_cache state.
    """

    context = zmq.Context.instance()
    peer_socket = context.socket(zmq.PAIR)  # pylint: disable=no-member
    peer_socket.connect("inproc://statemanager")

    client_socket = context.socket(zmq.PAIR)  # pylint: disable=no-member
    client_socket.bind("tcp://127.0.0.1:5555")

    poller = zmq.Poller()

    poller.register(peer_socket, zmq.POLLIN)
    poller.register(client_socket, zmq.POLLIN)

    market_cache = MarketCache()
    logging.info("StateManager started")

    while True:
        events = dict(poller.poll())

        if peer_socket in events:
            market_cache(orjson.loads(peer_socket.recv()))  # pylint: disable=I1101

        if client_socket in events:
            client_socket.send_pyobj(market_cache)


@attr.s
class Network:
    """
    Handles all connections made to betfair. Publishes new messages to subscribed clients.
    open/closes BetfairConnections to betfair.
    """

    peer_socket = attr.ib(type=zmq.Socket, default=None)
    pub_socket = attr.ib(type=zmq.Socket, default=None)
    client_socket = attr.ib(type=zmq.Socket, default=None)
    api_socket = attr.ib(type=zmq.Socket, default=None)

    poller = attr.ib(type=zmq.Poller, factory=zmq.Poller)
    connections = attr.ib(type=Dict[int, BetfairConnection], factory=dict)
    message_handler = attr.ib(type=list, factory=list)

    def read_loop(self):
        """
        Reads messages from BetfairConnections and publish them to statemanager and subscribed clients.
        Reads client request that wants open/close new streams to betfair.
        """

        self.connect()
        logging.info("Initialization done! Server ready for subscriptions.")

        while True:
            events = self.poller.poll()

            for fd, _ in events:
                if fd == self.api_socket:
                    message = orjson.loads(fd.recv())  # pylint: disable=I1101

                    if message["op"] == "subscription":
                        self.subscribe(message["name"], message["subscription_message"])
                else:
                    messages = self.connections[fd].recieve()

                    for message in messages:
                        self.peer_socket.send(
                            message, zmq.NOBLOCK  # pylint: disable=no-member
                        )
                        self.pub_socket.send(
                            message, zmq.NOBLOCK  # pylint: disable=no-member
                        )

    def register_connection(self, connection: BetfairConnection):
        self.connections[connection.socket.fileno()] = connection
        self.poller.register(connection.socket, zmq.POLLIN)
        return connection

    def subscribe(self, stream_name: str, subscription_message: Dict):
        """
        Used internally by Network(), creates a new connection to betfair and tries to subscribe to the markets supplied.

        NOTE: Subscribing to new markets might slow down publishing new messages while connecting to new streams, connect if you cant handle
        a little delay on published messages.

        DO NOT USE DIRECTLY! Use the provided client to make request.
        """
        connection = authenticate_connection(
            BetfairConnection.create_connection(name=stream_name)
        )

        connection.send(subscription_message)

        status_message = StatusMessage.from_stream_message(
            orjson.loads(connection.recieve()[0])  # pylint: disable=I1101
        )

        if status_message.status_code == StatusCode.FAILURE:
            logging.warning(status_message)
        else:
            logging.info("Stream: %s, status: %s", stream_name, status_message)
            self.register_connection(connection)

    def connect(self):
        context = zmq.Context.instance()
        self.peer_socket = context.socket(zmq.PAIR)  # pylint: disable=no-member
        self.peer_socket.bind("inproc://statemanager")
        self.poller.register(self.peer_socket, zmq.POLLIN)

        threading.Thread(target=state_manager, daemon=True).start()

        self.api_socket = context.socket(zmq.PAIR)  # pylint: disable=no-member
        self.api_socket.bind("tcp://127.0.0.1:5556")
        self.poller.register(self.api_socket, zmq.POLLIN)

        self.pub_socket = context.socket(zmq.PUB)  # pylint: disable=no-member
        self.pub_socket.bind("tcp://127.0.0.1:5557")

    @classmethod
    def create_betfair_server(cls):
        server = cls()
        threading.Thread(target=server.read_loop).start()

        return server
