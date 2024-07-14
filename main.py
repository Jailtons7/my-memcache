import re
import argparse
import socket
import logging
import asyncio

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


async def manage_connection(conn, addr):
    try:
        loop = asyncio.get_event_loop()

        while True:
            raw_command = (await loop.sock_recv(conn, 1024)).decode('utf-8')
            if not raw_command:
                logger.info('Client disconnected')
                break

            logger.info(f'Received {raw_command.strip()} bytes from {addr}')
            command = re.split(r"\s+", raw_command.strip())
            if "set" in command:
                command_name, key, flags, exptime, byte_count, *noreply = command[0:2] + list(map(int, command[2:5]))
                data = (await loop.sock_recv(conn, byte_count)).decode('utf-8')
                logger.info(f'Received {data.strip()} bytes from {addr}')
            elif "get" in command:
                command_name, key = command
            await loop.sock_sendall(conn, bytes("END\r\n", "utf-8"))
    finally:
        await conn.close()


async def serve_forever(port=11211):
    loop = asyncio.get_event_loop()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    logger.info('Starting server on port %d', port)
    s.bind(("0.0.0.0", port))
    s.listen(8)
    s.setblocking(False)
    while True:
        conn, addr = await loop.sock_accept(s)
        await loop.create_task(manage_connection(conn, addr))


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int, default=11211)
    args = parser.parse_args()
    await serve_forever(port=args.port)


if __name__ == '__main__':
    asyncio.run(main())
