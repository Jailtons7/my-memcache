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
        if not value or self._is_expired(key=key):
            return "END\r\n"
        return f"{self._display(key)}\r\nEND\r\n"

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

    async def add(self):
        if self.cache.get(self.cmd_list[1]) is None:
            return await self.set()
        _ = (await self.loop.sock_recv(self.conn, int(self.cmd_list[4]))).decode('utf-8')
        return "NOT_STORED\r\n"

    async def replace(self):
        if self.cache.get(self.cmd_list[1]) is not None:
            return await self.set()
        _ = (await self.loop.sock_recv(self.conn, int(self.cmd_list[4]))).decode('utf-8')
        return "NOT_STORED\r\n"

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

    def _is_expired(self, key) -> bool:
        """
        Checks if the stored key is expired. If so pops the key from the cache.
        :param key:
        :return:
        """
        if self.cache[key]["exptime"] is None or self.cache[key]["exptime"] > datetime.now():
            return False

        self.cache.pop(key)
        return True
