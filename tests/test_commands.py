import asyncio
import unittest
from unittest.mock import patch, MagicMock, AsyncMock

from src.server import connection_manager, cache


async def mock_set_key(*args, **kwargs):
    if not hasattr(mock_set_key, "call_count"):
        mock_set_key.call_count = 0

    if mock_set_key.call_count == 0:
        mock_set_key.call_count += 1
        return b"set test 0 0 4\r\n"
    elif mock_set_key.call_count == 1:
        mock_set_key.call_count += 1
        return b"data"
    else:
        return b""


async def mock_get_key(*args, **kwargs):
    if not hasattr(mock_get_key, "call_count"):
        mock_get_key.call_count = 0

    if mock_get_key.call_count == 0:
        mock_get_key.call_count += 1
        return b"get test"
    else:
        return b""


async def mock_add_key(*args, **kwargs):
    if not hasattr(mock_add_key, "call_count"):
        mock_add_key.call_count = 0

    if mock_add_key.call_count == 0:
        mock_add_key.call_count += 1
        return b"add test 0 0 4"
    elif mock_add_key.call_count == 1:
        mock_add_key.call_count += 1
        return b"data"
    else:
        return b""


async def mock_replace_key(*args, **kwargs):
    if not hasattr(mock_replace_key, "call_count"):
        mock_replace_key.call_count = 0

    if mock_replace_key.call_count == 0:
        mock_replace_key.call_count += 1
        return b"replace test 0 0 4"
    elif mock_replace_key.call_count == 1:
        mock_replace_key.call_count += 1
        return b"data"
    else:
        return b""


class TestCommands(unittest.TestCase):
    @patch("main.asyncio.get_event_loop")
    def test_get(self, mock_get_event_loop):
        mock_loop = AsyncMock()
        mock_get_event_loop.return_value = mock_loop

        mock_conn = MagicMock()
        mock_addr = ("0.0.0.0", 11211)
        cache['test'] = {
            'flags': 0,
            'exptime': None,
            'byte_count': 4,
            'noreply': '',
            'data': 'data'
        }

        mock_loop.sock_recv = AsyncMock(side_effect=mock_get_key)
        mock_loop.sock_sendall = AsyncMock()

        async def test_connection_manager():
            await connection_manager(conn=mock_conn, addr=mock_addr)
            expected_response = b'VALUE test 0 4\r\ndata\r\nEND\r\n'
            mock_loop.sock_sendall.assert_called_with(mock_conn, expected_response)

        asyncio.run(test_connection_manager())

    @patch("main.asyncio.get_event_loop")
    def test_set_command(self, mock_get_event_loop):
        mock_loop = AsyncMock()
        mock_get_event_loop.return_value = mock_loop

        mock_conn = MagicMock()
        mock_addr = ("0.0.0.0", 11211)

        mock_loop.sock_recv = AsyncMock(side_effect=mock_set_key)

        async def test_connection_manager():
            await connection_manager(mock_conn, mock_addr)
            self.assertEqual(cache["test"]["data"], "data")
            mock_loop.sock_sendall.assert_called_with(mock_conn, b'STORED\r\n')

        asyncio.run(test_connection_manager())

    @patch("main.asyncio.get_event_loop")
    def test_add_command(self, mock_get_event_loop):
        mock_loop = AsyncMock()
        mock_get_event_loop.return_value = mock_loop
        mock_conn = MagicMock()
        mock_addr = ("0.0.0.0", 11211)
        mock_loop.sock_recv = AsyncMock(side_effect=mock_add_key)

        cache.clear()

        async def test_connection_manager():
            await connection_manager(mock_conn, mock_addr)
            self.assertEqual(cache["test"]["data"], "data")
            mock_loop.sock_sendall.assert_called_with(mock_conn, b'STORED\r\n')

        asyncio.run(test_connection_manager())

    @patch("main.asyncio.get_event_loop")
    def test_replace_command(self, mock_get_event_loop):
        mock_loop = AsyncMock()
        mock_get_event_loop.return_value = mock_loop

        mock_conn = MagicMock()
        mock_addr = ("0.0.0.0", 11211)

        cache.clear()
        mock_loop.sock_recv = AsyncMock(side_effect=mock_replace_key)

        async def test_connection_manager():
            await connection_manager(mock_conn, mock_addr)
            mock_loop.sock_sendall.assert_called_with(mock_conn, b'NOT_STORED\r\n')
            cache['test'] = {"flags": 0, "exptime": None, "byte_count": 4, "noreply": "", "data": "foo"}
            delattr(mock_replace_key, "call_count")
            await connection_manager(mock_conn, mock_addr)
            self.assertNotEqual(cache["test"]["data"], "foo")
            self.assertEqual(cache["test"]["data"], "data")

        asyncio.run(test_connection_manager())


if __name__ == '__main__':
    unittest.main()
