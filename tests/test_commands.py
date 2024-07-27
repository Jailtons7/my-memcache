import asyncio
import unittest
from unittest.mock import patch, MagicMock, AsyncMock

from src.server import connection_manager, cache


class TestCommands(unittest.TestCase):
    @patch("main.asyncio.get_event_loop")
    def test_get(self, mock_get_event_loop):
        ...

    @patch("main.asyncio.get_event_loop")
    def test_set_command(self, mock_get_event_loop):
        mock_loop = AsyncMock()
        mock_get_event_loop.return_value = mock_loop

        mock_conn = MagicMock()
        mock_addr = ("0.0.0.0", 11211)

        # Simulate receiving set commands
        async def mock_client(m_, n_):
            if not hasattr(mock_client, "call_count"):
                mock_client.call_count = 0

            if mock_client.call_count == 0:
                mock_client.call_count += 1
                return b"set test 0 0 4\r\n"
            elif mock_client.call_count == 1:
                mock_client.call_count += 1
                return b"data"
            else:
                return b""

        mock_loop.sock_recv = mock_client

        async def test_connection_manager():
            await connection_manager(mock_conn, mock_addr)
            self.assertEqual(cache["test"]["data"], "data")
            mock_loop.sock_sendall.assert_called_with(mock_conn, b'STORED\r\n')

        asyncio.run(test_connection_manager())


if __name__ == '__main__':
    unittest.main()
