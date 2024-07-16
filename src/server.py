import re
import socket
import logging
import asyncio

from src.commands import Commands


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


cache = dict()


async def manage_connection(conn, addr):
    try:
        loop = asyncio.get_event_loop()

        while True:
            raw_command = (await loop.sock_recv(conn, 1024)).decode('utf-8')
            if not raw_command:
                logger.info('Client disconnected')
                break

            logger.info(f'Received {raw_command.strip()} bytes from {addr}')
            response = "END\r\n"
            cmd_list = re.split(r"\s+", raw_command.strip())
            cmd = Commands(conn=conn, addr=addr, loop=loop, cmd_list=cmd_list, cache=cache)
            if cmd_list[0] == "set":
                response = await cmd.set()
            elif cmd_list[0] == "get":
                response = await cmd.get()
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
        loop.create_task(manage_connection(conn, addr))
