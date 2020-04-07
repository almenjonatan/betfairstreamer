import bz2

from pathlib import Path

events = Path("ADVANCED/2020/Feb/1/")

f = open("stream_data.bin", "ab")

for event_dir in events.iterdir():
    data = b""
    for market_file in event_dir.iterdir():
        data += bz2.open(market_file).read().replace(b"\n", b"\r\n")

    f.write(data)



