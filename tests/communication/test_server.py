import socket
import time
import threading
import unittest
from communication.server import Server
from communication.server_exception import ServerException
from tests.communication.server_mock import ServerMock
from tests.communication.client_mock import ClientMock

TEST_HOST_CONNECT = 'localhost'
TEST_HOST_BIND = '0.0.0.0'
TEST_PORT = 0

class TestServer(unittest.TestCase):

    def test_listen_success(self):
        self.called = False
        def must_be_called(socket, ip):
            self.called = True

        with Server(TEST_HOST_BIND, TEST_PORT) as server:
            threading.Thread(target=server.listen, args=[must_be_called]).start()
            ip, port = server.socket.getsockname()
            with ClientMock(TEST_HOST_CONNECT, port):
                time.sleep(0.1)
        assert self.called


    def test_listen_port_used(self):
        with ServerMock(TEST_HOST_BIND, TEST_PORT) as first_server:
            with Server(TEST_HOST_BIND, first_server.port) as second_server:
                self.assertRaises(ServerException,
                                  second_server.listen,
                                  lambda sock, ip: 0)
