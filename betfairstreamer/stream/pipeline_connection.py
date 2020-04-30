from __future__ import annotations

from typing import List

import attr
import zmq

from betfairstreamer.stream.protocols import Connection


@attr.s(auto_attribs=True, slots=True)
class PipeLineConnection(Connection):

    connection: zmq.Socket

    def read(self) -> List[bytes]:
        return [self.connection.recv()]

    def get_socket(self) -> zmq.Socket:
        return self.connection

    @classmethod
    def create_pull_connection(cls, context: zmq.Context, url: str) -> PipeLineConnection:
        s = context.socket(zmq.PULL)
        s.bind(url)

        return cls(connection=s)
