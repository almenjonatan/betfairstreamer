import json
import socket
from test.generators import generate_message

import hypothesis.strategies as st
import pytest
from hypothesis import assume, given, note

from betfairstreamer.helpers.stream_helpers import create_order_subscription
from betfairstreamer.stream.betfair_connection import BetfairConnection


def test_closed_connection():
    s1, s2 = socket.socketpair()

    connection = BetfairConnection(connection=s1, app_key="")

    s2.close()

    with pytest.raises(ConnectionError):
        connection.read()


def test_send():
    s1, s2 = socket.socketpair()

    order_subscription = create_order_subscription()

    connection = BetfairConnection(connection=s1, app_key="")

    connection.send(order_subscription)

    assert json.loads(s2.recv(8000)) == order_subscription


@given(buffer_size=st.integers(4, 100), msg=generate_message())
def test_receive(buffer_size, msg):
    count, byte_msg, str_msg = msg

    s1, s2 = socket.socketpair()

    connection = BetfairConnection(connection=s1, buffer_size=buffer_size, app_key="")

    s2.sendall(byte_msg)
    s2.close()

    msg_count = 0
    messages = []

    try:
        while True:
            msg = connection.read()

            for m in msg:
                messages.append(m)

            msg_count += len(msg)
    except ConnectionError:
        pass

    note(str_msg)
    assert messages == byte_msg.split(b"\r\n")[:-1]
    assert msg_count == count
