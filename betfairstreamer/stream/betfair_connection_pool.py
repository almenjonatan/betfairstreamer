from __future__ import annotations

import os
import select
import socket
from typing import Dict, Generator, List, Union

import attr
from betfairlightweight import APIClient

from betfairstreamer.models.betfair_api import BetfairMarketSubscriptionMessage, BetfairOrderSubscriptionMessage
from betfairstreamer.stream.betfair_connection import BetfairConnection


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


def create_connection_pool(
    subscription_messages: List[Union[BetfairOrderSubscriptionMessage, BetfairMarketSubscriptionMessage]]
) -> BetfairConnectionPool:
    username, password, app_key, cert_path = (
        os.environ["USERNAME"],
        os.environ["PASSWORD"],
        os.environ["APP_KEY"],
        os.environ["CERT_PATH"],
    )

    cert_path = os.path.abspath(cert_path)

    trading: APIClient = APIClient(username, password, app_key, certs=cert_path, locale=os.environ["LOCALE"])

    trading.login()

    app_key, session_token = trading.app_key, trading.session_token

    connection_pool = BetfairConnectionPool.create_connection_pool(
        subscription_messages=subscription_messages, session_token=session_token, app_key=app_key,
    )

    return connection_pool
