import unittest
import socket
import threading
import time
from communication import messenger, protocol, messenger_exception

TEST_HOST_CONNECT = 'localhost'
TEST_HOST_BIND = '0.0.0.0'
TEST_PORT = 0
TEST_MESSAGE = b'This is a test message.'
TRAVIS_ON = True
if TRAVIS_ON:
    WAIT_TIME = 1
else:
    WAIT_TIME = 0.1


class TestMessenger(unittest.TestCase):

    def setUpTestClient(self):
        "Sets up a client which attempts to connect to the server."
        self.client_sock = socket.socket()
        self.client_sock.connect((TEST_HOST_CONNECT, self.port))

    def setUpTestServer(self):
        "Sets up a listening test server for the messenger client to connect to."
        self.server_sock = socket.socket()
        self.server_sock.bind((TEST_HOST_BIND, TEST_PORT))
        ip, self.port = self.server_sock.getsockname()
        self.server_sock.listen(1)

        # Wait for connection from messenger
        def accept_client_conn():
            self.client_sock, addr = self.server_sock.accept()
        threading.Thread(target=accept_client_conn).start()

    def setUpMessengerClient(self):
        "Sets up a messenger client which will connect to our test server."
        self.messenger = messenger.Messenger()
        self.messenger.start(TEST_HOST_CONNECT, self.port,
                             protocol.CLIENT_ROLE)

    def setUpMessengerServer(self):
        "Sets up a messenger server to which our test client can connect"
        self.messenger = messenger.Messenger()
        self.messenger.start(TEST_HOST_BIND, TEST_PORT, protocol.SERVER_ROLE)

    def tearDown(self):
        "Closes all the open sockets and stops the running threads if there are any."
        if hasattr(self, 'port'):
            del self.port

        if hasattr(self, 'client_sock'):
            self.client_sock.close()
            del self.client_sock

        if hasattr(self, 'server_sock'):
            self.server_sock.close()
            del self.server_sock

        if hasattr(self, 'messenger'):
            self.messenger.stop()
            del self.messenger

    def test_send_success(self):
        # Setup test server and client messenger
        self.setUpTestServer()
        self.setUpMessengerClient()

        # Check send function works
        self.messenger.send(TEST_MESSAGE)
        result = self.client_sock.recv(1024)
        assert result == TEST_MESSAGE + protocol.MESSAGE_SEPARATOR

    def test_send_not_connected(self):
        # socket.setdefaulttimeout(0)
        self.messenger = messenger.Messenger()

        assert not hasattr(self, 'server_sock')
        assert not hasattr(self, 'client_sock')
        assert hasattr(self, 'messenger')
        # Check send function works
        self.assertRaises(messenger_exception.MessengerException,
                          self.messenger.send,
                          TEST_MESSAGE)

    def test_start_client_connection_success(self):
        # Setup test server and client messenger
        self.setUpTestServer()
        # Make sure we don't have a client connected already
        assert not hasattr(self, 'client_sock')
        self.setUpMessengerClient()
        assert hasattr(self, 'client_sock')

    def test_start_client_connection_no_host(self):
        self.port = 45765
        # Make sure we don't have a client connected already
        assert not hasattr(self, 'client_sock')
        self.assertRaises(messenger_exception.MessengerException,
                          self.setUpMessengerClient)

    def test_start_server_connection(self):
        threading.Thread(target=self.setUpMessengerServer).start()

        # Wait for messenger to have bound his socket and defined its port
        time.sleep(WAIT_TIME)

        ip, self.port = self.messenger.socket.getsockname()
        try:
            self.setUpTestClient()
        except ConnectionRefusedError:
            assert False, "Couldn't connect to messenger server."

    def test_recv(self):
        # Setup test server and client messenger
        self.setUpTestServer()
        self.setUpMessengerClient()

        # Successful connection
        assert hasattr(self, 'client_sock')

        # Incomplete message (no separator)
        self.client_sock.send(b'This is the start')
        assert not self.messenger.message_queue

        # Finish message and start other
        self.client_sock.send(b'. And this is the end.' +
                              protocol.MESSAGE_SEPARATOR + b'And this is another incomplete m')
        time.sleep(WAIT_TIME)
        messages = self.messenger.consume_messages()
        assert len(messages) == 1
        assert messages[0] == b'This is the start. And this is the end.'

        # Finish last message on separator
        self.client_sock.send(b'essage.' + protocol.MESSAGE_SEPARATOR)
        time.sleep(WAIT_TIME)
        messages = self.messenger.consume_messages()
        assert len(messages) == 1
        assert messages[0] == b'And this is another incomplete message.'

    def test_stop(self):
        # Setup test server and client messenger
        self.setUpTestServer()
        self.setUpMessengerClient()

        self.messenger.stop()
        self.client_sock.settimeout(1)
        try:
            assert self.client_sock.recv(1) == b''
        except:
            assert False, "Did not receive empty byte from messenger."


if __name__ == "__main__":
    unittest.main()
