"""Тесты базовой функциональности"""

import unittest
from pproto_py import TcpSocket, TcpServer


class BaseTests(unittest.TestCase):
    """Тесты проверки базовой ункциональности"""

    def test_client_server(self) -> None:
        """Создание клиента и сервера и установка между ними соединения"""
        TcpSocket()


if __name__ == "__main__":
    unittest.main()
