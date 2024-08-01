import asyncio
import unittest
from unittest.mock import patch, MagicMock, AsyncMock

from src.server import connection_manager, cache


async def mock_call_command(*args, **kwargs):
    if not hasattr(mock_call_command, "call_count"):
        mock_call_command.call_count = 0

    if mock_call_command.call_count == 0:
        mock_call_command.call_count += 1
        return kwargs["command"]
    elif mock_call_command.call_count == 1:
        mock_call_command.call_count += 1
        return kwargs["data"]
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


class TestCommands(unittest.TestCase):
    def setUp(self):
        setattr(mock_call_command, "call_count", 0)
        cache.clear()

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

        async def mock_sock_recv(*args, **kwargs):
            kwargs["command"] = b"set test 0 0 4\r\n"
            kwargs["data"] = b"data"
            return await mock_call_command(*args, **kwargs)

        mock_loop.sock_recv = AsyncMock(side_effect=mock_sock_recv)
        mock_loop.sock_sendall = AsyncMock()

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

        async def mock_sock_recv(*args, **kwargs):
            kwargs["command"] = b"add test 0 0 4\r\n"
            kwargs["data"] = b"data"
            return await mock_call_command(*args, **kwargs)

        mock_loop.sock_recv = AsyncMock(side_effect=mock_sock_recv)

        async def test_connection_manager():
            # trying to add non-existing key
            cache.clear()
            await connection_manager(mock_conn, mock_addr)
            self.assertEqual(cache["test"]["data"], "data")
            mock_loop.sock_sendall.assert_called_with(mock_conn, b'STORED\r\n')
            # trying to add existing key
            delattr(mock_call_command, "call_count")
            cache["test"] = {
                'flags': 0,
                'exptime': None,
                'byte_count': 4,
                'noreply': '',
                'data': 'foo'
            }
            await connection_manager(mock_conn, mock_addr)
            mock_loop.sock_sendall.assert_called_with(mock_conn, b'NOT_STORED\r\n')
            self.assertEqual(cache["test"]["data"], "foo")

        asyncio.run(test_connection_manager())

    @patch("main.asyncio.get_event_loop")
    def test_replace_command(self, mock_get_event_loop):
        mock_loop = AsyncMock()
        mock_get_event_loop.return_value = mock_loop

        mock_conn = MagicMock()
        mock_addr = ("0.0.0.0", 11211)

        async def mock_sock_recv(*args, **kwargs):
            kwargs["command"] = b"replace test 0 0 4\r\n"
            kwargs["data"] = b"data"
            return await mock_call_command(*args, **kwargs)

        mock_loop.sock_recv = AsyncMock(side_effect=mock_sock_recv)

        async def test_connection_manager():
            # trying to replace not existent key
            await connection_manager(mock_conn, mock_addr)
            mock_loop.sock_sendall.assert_called_with(mock_conn, b'NOT_STORED\r\n')
            # defining key and retrying to replace
            delattr(mock_call_command, "call_count")
            cache['test'] = {"flags": 0, "exptime": None, "byte_count": 4, "noreply": "", "data": "foo"}
            await connection_manager(mock_conn, mock_addr)
            self.assertNotEqual(cache["test"]["data"], "foo")
            self.assertEqual(cache["test"]["data"], "data")

        asyncio.run(test_connection_manager())

    @patch("main.asyncio.get_event_loop")
    def test_append_command(self, mock_get_event_loop):
        mock_loop = AsyncMock()
        mock_get_event_loop.return_value = mock_loop
        mock_conn = MagicMock()
        mock_addr = ("0.0.0.0", 11211)

        async def mock_sock_recv(*args, **kwargs):
            kwargs["command"] = b"append test 0 0 4\r\n"
            kwargs["data"] = b"data"
            return await mock_call_command(*args, **kwargs)

        mock_loop.sock_recv = AsyncMock(side_effect=mock_sock_recv)

        async def test_connection_manager():
            # trying to append data in a not existing key
            await connection_manager(mock_conn, mock_addr)
            mock_loop.sock_sendall.assert_called_with(mock_conn, b'NOT_STORED\r\n')
            self.assertRaises(KeyError)
            # trying to append data in an existing key
            cache["test"] = {
                'flags': 0,
                'exptime': None,
                'byte_count': 4,
                'noreply': '',
                'data': 'foo'
            }
            delattr(mock_call_command, "call_count")
            await connection_manager(mock_conn, mock_addr)
            mock_loop.sock_sendall.assert_called_with(mock_conn, b'STORED\r\n')
            self.assertEqual(cache["test"]["data"], "foodata")

        asyncio.run(test_connection_manager())

    @patch("main.asyncio.get_event_loop")
    def test_prepend_command(self, mock_get_event_loop):
        mock_loop = AsyncMock()
        mock_get_event_loop.return_value = mock_loop
        mock_conn = MagicMock()
        mock_addr = ("0.0.0.0", 11211)

        async def mock_sock_recv(*args, **kwargs):
            kwargs["command"] = b"prepend test 0 0 4\r\n"
            kwargs["data"] = b"data"
            return await mock_call_command(*args, **kwargs)

        mock_loop.sock_recv = AsyncMock(side_effect=mock_sock_recv)

        async def test_connection_manager():
            # trying to append data in a not existing key
            await connection_manager(mock_conn, mock_addr)
            mock_loop.sock_sendall.assert_called_with(mock_conn, b'NOT_STORED\r\n')
            self.assertRaises(KeyError)
            # trying to append data in an existing key
            cache["test"] = {
                'flags': 0,
                'exptime': None,
                'byte_count': 4,
                'noreply': '',
                'data': 'foo'
            }
            delattr(mock_call_command, "call_count")
            await connection_manager(mock_conn, mock_addr)
            mock_loop.sock_sendall.assert_called_with(mock_conn, b'STORED\r\n')
            self.assertEqual(cache["test"]["data"], "datafoo")

        asyncio.run(test_connection_manager())


if __name__ == '__main__':
    unittest.main()
