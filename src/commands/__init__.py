import logging
from datetime import datetime, timedelta
from socket import socket
from typing import List, Tuple, Union
from asyncio import AbstractEventLoop


logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)


class Commands:

    def __init__(
            self,
            conn: socket,
            addr: Tuple[str, int],
            loop: AbstractEventLoop,
            cmd_list: List[str],
            cache: dict,
    ):
        self.conn = conn
        self.addr = addr
        self.loop = loop
        self.cmd_list = cmd_list
        self.cache = cache

    async def get(self) -> str:
        command_name, key = self.cmd_list
        value = self.cache.get(key)
        if value and (value["exptime"] is None or value["exptime"] >= datetime.now()):
            return f"{self._display(key)}\r\nEND\r\n"
        return "END\r\n"

    async def set(self) -> str:
        try:
            key = self.cmd_list[1]
            flags = int(self.cmd_list[2])
            exptime = int(self.cmd_list[3])
            byte_count = int(self.cmd_list[4])
        except IndexError:
            response = "the set command \r\n"
            await self.loop.sock_sendall(self.conn, bytes(response, "utf-8"))
            return ""
        try:
            noreply = self.cmd_list[5]
        except IndexError:
            noreply = ""
        data = (await self.loop.sock_recv(self.conn, byte_count)).decode('utf-8')
        logger.info(f'Received {data.strip()} bytes from {self.addr}')
        self.cache[key] = {
            "flags": flags,
            "exptime": self._set_expiration(exptime),
            "byte_count": byte_count,
            "noreply": noreply,
            "data": data,
        }
        logger.info(f"Stored cache:\r\n{self.cache}")
        return "" if noreply else "STORED\r\n"

    def _display(self, key):
        return (
            f"VALUE {key} {self.cache[key]['flags']} {self.cache[key]['byte_count']}\r\n"
            f"{self.cache[key]['data'].strip()}"
        )

    @staticmethod
    def _set_expiration(expiration: int) -> Union[datetime, None]:
        if expiration == 0:
            return None
        return datetime.now() + timedelta(seconds=expiration)
