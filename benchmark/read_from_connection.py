import socket
import time
from multiprocessing.context import Process

import orjson

from betfairstreamer.cache import MarketCache
from betfairstreamer.stream.stream import BetfairConnection, BetfairConnectionPool


def sender():
    s1.sendall(stream_data)

    s1.shutdown(socket.SHUT_RDWR)
    s1.close()


def reader():
    count = 0

    try:
        for m in connection_pool.read():
            market_cache(orjson.loads(m))
            count += 1
            if count % 100000 == 0:
                print(count)

    except ConnectionError:
        pass


if __name__ == "__main__":
    import multiprocessing

    multiprocessing.set_start_method('fork')

    s1, s2 = socket.socketpair()

    connection = BetfairConnection(s2)
    connection_pool = BetfairConnectionPool()
    connection_pool.add_connection(connection)

    stream_data = open("stream_data.bin", "rb").read()

    market_cache = MarketCache()

    p1 = Process(target=sender)
    p1.start()

    t0 = time.perf_counter()

    p2 = Process(target=reader)
    p2.start()
    p2.join()

    print(time.perf_counter() - t0)
