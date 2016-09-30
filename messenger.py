import socket, threading
import protocol
from messenger_exception import MessengerException

class Messenger(object):
	"Messenger object that handles socket logic to communicate to and fro two PCs."
	def __init__(self):
		"Creates a messenger object."
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
		self.messageQueue = []
		self.running = False
		self.role = None
		self.lastError = None

	def listen(self, host, port):
		"Binds a socket to the given address and listens and accepts one incoming connection."
		try:
			self.socket.bind((host, port))
		except socket.error as e:
			raise MessengerException("Other program already using port.") from e
		self.host, self.port = self.socket.getsockname() #For testing purposes... It's not great
		self.socket.listen(1)
		clientSock, addr = self.socket.accept()
		self.serverSocket = self.socket
		self.socket = clientSock

	def connect(self, host, port):
		"Connects the Messenger's socket to the given address."
		try:
			self.socket.connect((host, port))
		except ConnectionRefusedError as e:
			raise MessengerException("No host listening.") from e

	def recv(self):
		"Handles the reception of the messages from a remote Messenger object and adds them to the message queue."
		buffer = b''
		while self.running:
			try:
				buffer += self.socket.recv(1024)
			except socket.error as e:
				lastError = e
				self.stop()
				return
			#Parse messages from buffer
			messages = buffer.split(protocol.MESSAGE_SEPARATOR)
			buffer = messages.pop() #Set buffer to last incomplete message or '' if ending on a separator
			self.messageQueue += messages

	def send(self, message):
		"Sends the given message to the remote Messenger to which this one is currently connected."
		formMessage = message + protocol.MESSAGE_SEPARATOR
		sent = 0
		while sent < len(formMessage):
			try:
				sent += self.socket.send(formMessage[sent:])
			except socket.error as e:
				raise MessengerException("Socket not connected.") from e

	def start(self, host, port, role):
		"Starts the Messenger and binds/connects to the given address depending on given CLIENT/SERVER role."
		self.role = role
		if role == protocol.CLIENT_ROLE:
			self.connect(host, port)
		else:
			self.listen(host, port)
		t = threading.Thread(target = self.recv)
		self.running = True
		t.start()

	def stop(self):
		"Closes the open sockets and set shutdown flag for running threads."
		self.running = False
		try:
			self.socket.shutdown(socket.SHUT_RDWR)
		except OSError: #Was never connected or already closed
			pass
		self.socket.close()
		if self.role == protocol.SERVER_ROLE:
			self.serverSocket.close()

	def consumeMessage(self):
		"Returns the content of the first message and removes it from the queue."
		if len(self.messageQueue) > 0:
			message = self.messageQueue[0]
			self.messageQueue = self.messageQueue[1:]
			return message
		return None

	def consumeMessages(self):
		"Returns the content of the message queue and empties it."
		messages = self.messageQueue
		self.messageQueue = []
		return messages

	def raiseLastErrorIfAny(self):
		"Raises the last error that might have occured in the remote thread that deals with reception."
		if self.lastError:
			raise MessengerException("Connection closed.") from self.lastError
