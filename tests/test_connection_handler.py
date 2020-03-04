import socket
import hypothesis.strategies as st
import pytest

from hypothesis import given
from hypothesis.strategies import composite
from betfairstreamer.server import BetfairConnection, ConnectionHandler
from hypothesis import settings
import select
from tests.generators import generate_message


@given(generate_message())
def test_connection_handler(msg):

    count, byte_msg, msg = msg

    s1, s2 = socket.socketpair()
    s3, s4 = socket.socketpair()

    c1 = BetfairConnection(s1)
    c2 = BetfairConnection(s3)

    poller = select.poll()

    index = 0

    def message_handler(msg):
        assert msg is not None

    connection_handler = ConnectionHandler(
        poller=poller, message_handler=message_handler
    )

    connection_handler.add_connection(c1)
    connection_handler.add_connection(c2)

    s2.sendall(byte_msg)
    s4.sendall(byte_msg)

    r = connection_handler.read()

    connection_handler.close_all_connections()
