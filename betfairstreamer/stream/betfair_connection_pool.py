from __future__ import annotations

import select
import socket
from typing import Dict, Generator, List, Optional, Union

import attr
import zmq

from betfairstreamer.models.betfair_api import BetfairMarketSubscriptionMessage, BetfairOrderSubscriptionMessage
from betfairstreamer.stream.betfair_connection import BetfairConnection
from betfairstreamer.stream.protocols import Connection


@attr.s(auto_attribs=True)
class BetfairConnectionPool:
    poller: zmq.Poller = attr.ib(factory=zmq.Poller)
    connections: Dict[Union[int, zmq.Socket], Connection] = attr.ib(factory=dict)
    timeout: Optional[int] = None

    def add_connection(self, connection: Connection) -> None:
        self.poller.register(connection.get_socket(), select.POLLIN)

        if isinstance(connection.get_socket(), socket.socket):
            self.connections[connection.get_socket().fileno()] = connection

        if isinstance(connection.get_socket(), zmq.Socket):
            self.connections[connection.get_socket()] = connection

    def remove_connection(self, fd: Union[socket.socket, zmq.Socket]) -> None:
        self.poller.unregister(fd)

    def read(self) -> Generator[Union[bytes, Connection], None, None]:

        while True:
            events = self.poller.poll(self.timeout)

            if not events:
                self.close()
                raise TimeoutError

            for fd, e in events:
                for m in self.connections[fd].read():
                    yield m

    def close(self) -> None:
        for k, c in self.connections.items():
            c.close()

    @classmethod
    def create_connection_pool(
        cls,
        subscription_messages: List[Union[BetfairMarketSubscriptionMessage, BetfairOrderSubscriptionMessage]],
        session_token: str,
        app_key: str,
        timeout: Optional[int] = None,
    ) -> BetfairConnectionPool:
        connection_pool = cls(timeout=timeout)

        for subscription_message in subscription_messages:
            connection = BetfairConnection()
            connection.connect(session_token, app_key, subscription_message)

            connection_pool.add_connection(connection)

        return connection_pool
