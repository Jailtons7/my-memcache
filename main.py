import argparse
import asyncio

from server import serve_forever


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int, default=11211)
    args = parser.parse_args()
    await serve_forever(port=args.port)


if __name__ == '__main__':
    asyncio.run(main())
