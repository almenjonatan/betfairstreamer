import socket
import time
from multiprocessing.context import Process

import ujson

from betfairstreamer.cache.market_cache import MarketCache

s1, s2 = socket.socketpair()

market_cache = MarketCache()


def market_cache_read(d):
    count = 0

    for r in d:
        market_cache(ujson.loads(r))
        count += 1
        if count % 100000 == 0:
            print(count)


def s():
    t0 = time.perf_counter()

    p2 = Process(target=market_cache_read, args=(buffer,))
    p2.start()
    p2.join()

    print(time.perf_counter() - t0)


if __name__ == "__main__":
    import multiprocessing

    multiprocessing.set_start_method('fork')

    f = open("data.bin", "rb")
    buffer = f.read().splitlines(keepends=True)[:-1]

    s()
