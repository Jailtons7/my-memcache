import re
import argparse
import socket
import logging
import asyncio

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
            command = re.split(r"\s+", raw_command.strip())
            response = "END\r\n"
            if "set" in command:
                command_name = command[0]
                key = command[1]
                flags = int(command[2])
                exptime = int(command[3])
                byte_count = int(command[4])
                noreply = command[5]
                data = (await loop.sock_recv(conn, byte_count)).decode('utf-8')
                logger.info(f'Received {data.strip()} bytes from {addr}')
                cache[key] = f"VALUE {key} {flags} {byte_count}\r\n{data.strip()}"
                response = "STORED\r\n"
            elif "get" in command:
                command_name, key = command
                value = cache.get(key)
                response = f"VALUE {value}\r\nEND\r\n" or "END\r\n"
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


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int, default=11211)
    args = parser.parse_args()
    await serve_forever(port=args.port)


if __name__ == '__main__':
    asyncio.run(main())
