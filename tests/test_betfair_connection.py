import socket
import hypothesis.strategies as st
import pytest

from hypothesis import given
from hypothesis.strategies import composite
from betfairstreamer.server import BetfairConnection
from hypothesis import settings

from tests.generators import generate_message


def test_closed_connection():
    s1, s2 = socket.socketpair()
    connection = BetfairConnection(s1)

    s2.close()

    with pytest.raises(ConnectionError):
        connection.recieve()


@given(msg=generate_message())
def test_recieve(msg):
    count, byte_msg, str_msg = msg

    s1, s2 = socket.socketpair()

    connection = BetfairConnection(s1, read_buffer_size=4)

    s1.settimeout(0.01)
    s2.sendall(byte_msg)

    msg_count = 0

    try:
        while True:
            msg = connection.recieve()
            msg_count += len(msg)
    except socket.timeout:
        pass

    assert msg_count == count

