import socket
import time
from multiprocessing.context import Process

from betfairstreamer.cache.market_cache import MarketCache
from betfairstreamer.server import BetfairConnection

s1, s2 = socket.socketpair()

connection = BetfairConnection(s2)

market_cache = MarketCache()


def start_server(stream_data):
    print("Sent bytes")

    for r in stream_data:
        s1.send(r)

    s1.shutdown(socket.SHUT_RDWR)
    s1.close()
    print("Socket closed")


def start_reader():
    count = 0

    try:
        while True:
            for m in connection.read():
                count += 1
                if count % 100000 == 0:
                    print(count)

    except ConnectionError:
        pass


if __name__ == "__main__":
    import multiprocessing

    multiprocessing.set_start_method('fork')

    f = open("data.bin", "rb")
    buffer = f.read().splitlines(keepends=True)[:-1]

    p1 = Process(target=start_server, args=(buffer,))
    p1.start()

    t0 = time.perf_counter()
    p2 = Process(target=start_reader)
    p2.start()
    p2.join()

    print(time.perf_counter() - t0)
