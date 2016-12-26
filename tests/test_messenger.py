import unittest, socket, threading, time
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
	"Sets up a client which attempts to connect to the server."
	def setUpTestClient(self):
		self.clientSock = socket.socket()
		self.clientSock.connect((TEST_HOST_CONNECT, self.port))

	"Sets up a listening test server for the messenger client to connect to."
	def setUpTestServer(self):
		self.serverSock = socket.socket()
		self.serverSock.bind((TEST_HOST_BIND, TEST_PORT))
		ip, self.port = self.serverSock.getsockname()
		self.serverSock.listen(1)

		#Wait for connection from messenger
		def acceptClientConn():
			self.clientSock, addr = self.serverSock.accept()
		threading.Thread(target = acceptClientConn).start()

	"Sets up a messenger client which will connect to our test server."
	def setUpMessengerClient(self):
		self.messenger = messenger.Messenger()
		self.messenger.start(TEST_HOST_CONNECT, self.port, protocol.CLIENT_ROLE)

	"Sets up a messenger server to which our test client can connect"
	def setUpMessengerServer(self):
		self.messenger = messenger.Messenger()
		self.messenger.start(TEST_HOST_BIND, TEST_PORT, protocol.SERVER_ROLE)

	"Closes all the open sockets and stops the running threads if there are any."
	def tearDown(self):
		if hasattr(self, 'port'):
			del self.port

		if hasattr(self, 'clientSock'):
			self.clientSock.close()
			del self.clientSock

		if hasattr(self, 'serverSock'):
			self.serverSock.close()
			del self.serverSock

		if hasattr(self, 'messenger'):
			self.messenger.stop()
			del self.messenger

	def test_send_success(self):
		#Setup test server and client messenger
		self.setUpTestServer()
		self.setUpMessengerClient()

		#Check send function works
		self.messenger.send(TEST_MESSAGE)
		result = self.clientSock.recv(1024)
		assert result == TEST_MESSAGE + protocol.MESSAGE_SEPARATOR

	def test_send_not_connected(self):
		#socket.setdefaulttimeout(0)
		self.messenger = messenger.Messenger()

		assert not hasattr(self, 'serverSock')
		assert not hasattr(self, 'clientSock')
		assert hasattr(self, 'messenger')
		#Check send function works
		self.assertRaises(messenger_exception.MessengerException, self.messenger.send, TEST_MESSAGE)

	def test_start_client_connection_success(self):
		#Setup test server and client messenger
		self.setUpTestServer()
		#Make sure we don't have a client connected already
		assert not hasattr(self, 'clientSock')
		self.setUpMessengerClient()
		assert hasattr(self, 'clientSock')

	def test_start_client_connection_no_host(self):
		self.port = 45765
		#Make sure we don't have a client connected already
		assert not hasattr(self, 'clientSock')
		self.assertRaises(messenger_exception.MessengerException, self.setUpMessengerClient)

	def test_start_server_connection(self):
		threading.Thread(target = self.setUpMessengerServer).start()

		#Wait for messenger to have bound his socket and defined its port
		time.sleep(WAIT_TIME)

		ip, self.port = self.messenger.socket.getsockname()
		try:
			self.setUpTestClient()
		except ConnectionRefusedError:
			assert False, "Couldn't connect to messenger server."

	def test_recv(self):
		#Setup test server and client messenger
		self.setUpTestServer()
		self.setUpMessengerClient()

		#Successful connection
		assert hasattr(self, 'clientSock')

		#Incomplete message (no separator)
		self.clientSock.send(b'This is the start')
		assert not self.messenger.messageQueue

		#Finish message and start other
		self.clientSock.send(b'. And this is the end.' + protocol.MESSAGE_SEPARATOR + b'And this is another incomplete m')
		time.sleep(WAIT_TIME)
		messages = self.messenger.consumeMessages()
		assert len(messages) == 1
		assert messages[0] == b'This is the start. And this is the end.'

		#Finish last message on separator
		self.clientSock.send(b'essage.' + protocol.MESSAGE_SEPARATOR)
		time.sleep(WAIT_TIME)
		messages = self.messenger.consumeMessages()
		assert len(messages) == 1
		assert messages[0] == b'And this is another incomplete message.'

	def test_stop(self):
		#Setup test server and client messenger
		self.setUpTestServer()
		self.setUpMessengerClient()

		self.messenger.stop()
		self.clientSock.settimeout(1)
		try:
			assert self.clientSock.recv(1) == b''
		except:
			assert False, "Did not receive empty byte from messenger."


if __name__ == "__main__":
    unittest.main()
