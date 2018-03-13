import socket
import time
import unittest
from communication.client import Client
from communication.exceptions import ClientException
from tests.communication.server_mock import ServerMock

TEST_HOST_CONNECT = 'localhost'
TEST_HOST_BIND = '0.0.0.0'
TEST_PORT = 0

class TestClient(unittest.TestCase):

    def test_connect_success(self):
        with ServerMock(TEST_HOST_BIND, TEST_PORT) as server:
            with Client(TEST_HOST_CONNECT, server.port) as client:
                client.connect()
                time.sleep(0.2)
                assert server.connected

    def test_connect_no_server(self):
        with Client(TEST_HOST_CONNECT, 35665) as client:
            self.assertRaises(ClientException, client.connect)
