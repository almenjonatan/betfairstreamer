import socket
from typing import List, Protocol, Union

import zmq


class Connection(Protocol):
    def read(self) -> List[bytes]:
        ...

    def get_socket(self) -> Union[zmq.Socket, socket.socket]:
        ...
