import hypothesis.strategies as st
from hypothesis.strategies import composite


@composite
def generate_message(draw):
    i = draw(st.integers(min_value=1, max_value=100))

    msg = ""

    for _ in range(i):
        msg += draw(st.text()) + "\r\n"

    return len(msg.split("\r\n")[:-1]), msg.encode("utf-8"), msg
