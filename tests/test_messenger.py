import unittest
import socket
import threading
import time
from communication.messenger import Messenger
from communication import messenger_exception
from communication import protocol

TEST_HOST_CONNECT = 'localhost'
TEST_HOST_BIND = '0.0.0.0'
TEST_PORT = 0
TEST_MESSAGE = b'This is a test message.'
TRAVIS_ON = True
if TRAVIS_ON:
    WAIT_TIME = 1
else:
    WAIT_TIME = 0.1


class ServerMock():

    def __init__(self, host, port):
        self.host, self.port = host, port
        self.connected = False

    def __enter__(self):
        self.socket = socket.socket()
        self.socket.bind((self.host, self.port))
        ip, self.port = self.socket.getsockname()
        self.socket.listen(1)

        # Wait for connection from messenger
        def accept_client_conn():
            self.client_socket, addr = self.socket.accept()
            self.connected = True
        threading.Thread(target=accept_client_conn).start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connected:
            self.client_socket.close()
        self.socket.close()


class ClientMock():

    def __init__(self, host, port):
        self.host, self.port = host, port
        self.connected = False

    def __enter__(self):
        self.client_socket = socket.socket()
        self.client_socket.connect((self.host, self.port))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client_socket.close()


class TestMessenger(unittest.TestCase):

    def setUpTestClient(self):
        "Sets up a client which attempts to connect to the server."
        self.client_sock = socket.socket()
        self.client_sock.connect((TEST_HOST_CONNECT, self.port))

    def test_send_success(self):
        with ServerMock(TEST_HOST_BIND, TEST_PORT) as server:
            with Messenger(protocol.CLIENT_ROLE, TEST_HOST_CONNECT, server.port) as messenger:
                messenger.send(TEST_MESSAGE)
                result = server.client_socket.recv(1024)
                assert result == TEST_MESSAGE + protocol.MESSAGE_SEPARATOR

    def test_send_not_connected(self):
        messenger = Messenger(protocol.CLIENT_ROLE, TEST_HOST_CONNECT, port=45765)
        self.assertRaises(messenger_exception.MessengerException,
                          messenger.send,
                          TEST_MESSAGE)

    def test_enter_client_connection_success(self):
        with ServerMock(TEST_HOST_BIND, TEST_PORT) as server:
            with Messenger(protocol.CLIENT_ROLE, TEST_HOST_CONNECT, server.port) as messenger:
                assert server.connected

    def test_start_client_connection_no_host(self):
        self.port = 45765
        messenger = Messenger(protocol.CLIENT_ROLE,
                              TEST_HOST_CONNECT, port=45765)
        self.assertRaises(messenger_exception.MessengerException,
                          messenger.__enter__)

    def test_start_server_connection(self):

        def try_to_connect():
            # Wait for messenger to have bound his socket and defined its port
            time.sleep(WAIT_TIME)
            #ip, port = self.messenger.socket.getsockname()
            try:
                with ClientMock(TEST_HOST_CONNECT, port=45765):
                    pass
            except ConnectionRefusedError:
                assert False, "Couldn't connect to messenger server."

        threading.Thread(target=try_to_connect).start()


        with Messenger(protocol.SERVER_ROLE, TEST_HOST_BIND, port=45765) as self.messenger:
            pass

    def test_recv(self):
        with ServerMock(TEST_HOST_BIND, TEST_PORT) as server:
            with Messenger(protocol.CLIENT_ROLE, TEST_HOST_CONNECT, server.port) as messenger:
                assert server.connected

                # Incomplete message (no separator)
                server.client_socket.send(b'This is the start')
                assert not messenger.message_queue

                # Finish message and start other
                message_cont = b'. And this is the end.' + protocol.MESSAGE_SEPARATOR + b'And this is another incomplete m'
                server.client_socket.send(message_cont)
                time.sleep(WAIT_TIME)
                messages = messenger.consume_messages()
                assert len(messages) == 1
                assert messages[0] == b'This is the start. And this is the end.'

                # Finish last message on separator
                server.client_socket.send(b'essage.' + protocol.MESSAGE_SEPARATOR)
                time.sleep(WAIT_TIME)
                messages = messenger.consume_messages()
                assert len(messages) == 1
                assert messages[0] == b'And this is another incomplete message.'

    def test_exit(self):
        with ServerMock(TEST_HOST_BIND, TEST_PORT) as server:
            with Messenger(protocol.CLIENT_ROLE, TEST_HOST_CONNECT, server.port) as messenger:
                assert server.connected
            server.client_socket.settimeout(1)
            try:
                assert server.client_socket.recv(1) == b''
            except:
                assert False, "Did not receive empty byte from messenger."


if __name__ == "__main__":
    unittest.main()
