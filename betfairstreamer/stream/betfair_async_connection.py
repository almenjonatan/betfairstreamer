from __future__ import annotations

import asyncio
import ssl
from asyncio import StreamReader, StreamWriter
from typing import Any, Dict, List, Tuple, Union

import attr

from betfairstreamer.models.betfair_api import (
    OP,
    BetfairAuthenticationMessage,
    BetfairMarketSubscriptionMessage,
    BetfairOrderSubscriptionMessage,
)
from betfairstreamer.models.betfair_api_extensions import BetfairMessage
from betfairstreamer.stream.stream_parser import Parser
from betfairstreamer.utils import encode


async def create_async_socket() -> Tuple[StreamReader, StreamWriter]:
    hostname = "stream-api.betfair.com"
    port = 443

    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.check_hostname = False

    return await asyncio.open_connection(*(hostname, port), ssl=ssl_context)


@attr.s(auto_attribs=True, slots=True)
class BetfairAsyncConnection:
    reader: StreamReader
    writer: StreamWriter
    parser: Parser = attr.Factory(Parser)

    async def read(self) -> List[bytes]:
        part = await self.reader.read(8192)

        if part == b"":
            raise ConnectionError("Betfair closed connection.")

        return self.parser.parse_message(part)

    async def send(self, msg: BetfairMessage) -> None:
        self.writer.write(encode(msg))
        await self.writer.drain()

    @classmethod
    async def create_connection(
        cls, subscription_message: BetfairMessage, session_token: str, app_key: str
    ) -> BetfairAsyncConnection:
        reader, writer = await create_async_socket()
        connection = cls(reader=reader, writer=writer)

        print(await connection.read())

        auth_message = BetfairAuthenticationMessage(
            op=OP.authentication.value, id=subscription_message["id"], session=session_token, appKey=app_key,
        )

        await connection.send(auth_message)
        print(await connection.read())

        await connection.send(subscription_message)
        print(await reader.readuntil(b"\r\n"))

        return connection
