import re
import socket
import logging
import asyncio
import typing

from src.commands import Commands
from src.commands.exceptions import CommandError

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


cache = dict()


async def default_response():
    return "END\r\n"


async def connection_manager(conn: socket, addr: typing.Tuple[str, int]):
    try:
        loop = asyncio.get_event_loop()

        while True:
            raw_command = (await loop.sock_recv(conn, 1024)).decode('utf-8')
            if not raw_command:
                logger.info('Client disconnected')
                break

            logger.info(f'Received {raw_command.strip()} bytes from {addr}')
            cmd_list = re.split(r"\s+", raw_command.strip())
            cmd = Commands(conn=conn, addr=addr, loop=loop, cmd_list=cmd_list, cache=cache)
            commands_mapping = {
                "set": cmd.set,
                "get": cmd.get,
                "add": cmd.add,
                "replace": cmd.replace,
                "append": cmd.append,
                "prepend": cmd.prepend,
            }
            try:
                response = await commands_mapping.get(cmd_list[0], default_response)()
            except CommandError as e:
                response = str(e)
            logger.info(f"Stored cache:\r\n{cache}")
            await loop.sock_sendall(conn, bytes(response, "utf-8"))
    finally:
        conn.close()


async def serve_forever(port=11211):
    loop = asyncio.get_event_loop()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    logger.info('Starting server on port %d', port)
    s.bind(("0.0.0.0", port))
    s.listen(socket.SOMAXCONN)
    s.setblocking(False)
    while True:
        conn, addr = await loop.sock_accept(s)
        loop.create_task(connection_manager(conn, addr))
