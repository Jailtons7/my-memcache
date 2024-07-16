import logging
from socket import socket
from typing import List, Tuple
from contextlib import suppress
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
        return f"{value}\r\nEND\r\n" if value else "END\r\n"

    async def set(self) -> str:
        try:
            command_name = self.cmd_list[0]
            key = self.cmd_list[1]
            flags = int(self.cmd_list[2])
            exptime = int(self.cmd_list[3])
            byte_count = int(self.cmd_list[4])
        except IndexError:
            response = "the set command \r\n"
            await self.loop.sock_sendall(self.conn, bytes(response, "utf-8"))
            return ""
        noreply = ""
        with suppress(IndexError):
            noreply = self.cmd_list[5]
        data = (await self.loop.sock_recv(self.conn, byte_count)).decode('utf-8')
        logger.info(f'Received {data.strip()} bytes from {self.addr}')
        self.cache[key] = f"VALUE {key} {flags} {byte_count}\n{data.strip()}"
        return "" if noreply else "STORED\r\n"
