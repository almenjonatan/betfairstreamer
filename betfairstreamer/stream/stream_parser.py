from typing import List


class Parser:
    def __init__(self) -> None:
        self.buffer = b""
        self.crlf = b"\r\n"

    def parse_message(self, part: bytes) -> List[bytes]:
        messages = []

        if part[:1] == b"\n" and self.buffer[-1:] == b"\r":
            messages.append(self.buffer[:-1])
            self.buffer = b""
            part = part[1:]

        before, sep, after = part.partition(self.crlf)

        before = self.buffer + before

        while sep == self.crlf:
            messages.append(before)

            before, sep, after = after.partition(self.crlf)

        self.buffer = before

        return messages
