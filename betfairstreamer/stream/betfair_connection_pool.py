from __future__ import annotations

import os
import select
import socket
from typing import Dict, Generator, List, Union

import attr
import zmq

from betfairstreamer.models.betfair_api import BetfairMarketSubscriptionMessage, BetfairOrderSubscriptionMessage
from betfairstreamer.stream.betfair_connection import BetfairConnection
from betfairstreamer.stream.protocols import Connection


@attr.s(auto_attribs=True)
class BetfairConnectionPool:
    poller: zmq.Poller = attr.ib(factory=zmq.Poller)
    connections: Dict[Union[int, zmq.Socket], Connection] = attr.ib(factory=dict)

    def add_connection(self, connection: Connection) -> None:
        self.poller.register(connection.get_socket(), select.POLLIN)

        if isinstance(connection.get_socket(), socket.socket):
            self.connections[connection.get_socket().fileno()] = connection

        if isinstance(connection.get_socket(), zmq.Socket):
            self.connections[connection.get_socket()] = connection

        # print(self.connections)

    def read(self) -> Generator[bytes, None, None]:
        while True:
            events = self.poller.poll()

            for fd, e in events:
                for m in self.connections[fd].read():
                    yield m

    def close(self) -> None:
        for k, c in self.connections.items():
            c.get_socket().shutdown(socket.SHUT_RDWR)
            c.get_socket().close()

    @classmethod
    def create_connection_pool(
        cls,
        subscription_messages: List[Union[BetfairMarketSubscriptionMessage, BetfairOrderSubscriptionMessage]],
        session_token: str,
        app_key: str,
    ) -> BetfairConnectionPool:
        connection_pool = cls()

        for subscription_message in subscription_messages:
            connection_pool.add_connection(
                BetfairConnection.create_connection(subscription_message, session_token, app_key)
            )

        return connection_pool
