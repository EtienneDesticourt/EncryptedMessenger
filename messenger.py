import socket, threading
import protocol
from messenger_exception import MessengerException

class Messenger(object):
	def __init__(self):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
		self.messageQueue = []
		self.running = False
		self.role = None
		self.lastError = None

	def listen(self, host, port):
		self.socket.bind((host, port))
		self.host, self.port = self.socket.getsockname() #For testing purposes... It's not great
		self.socket.listen(1)
		clientSock, addr = self.socket.accept()
		self.serverSocket = self.socket
		self.socket = clientSock

	def connect(self, host, port):
		self.socket.connect((host, port))

	def recv(self):
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
		formMessage = message + protocol.MESSAGE_SEPARATOR
		sent = 0
		while sent < len(formMessage):
			try:
				sent += self.socket.send(formMessage[sent:])
			except socket.error as e:
				raise MessengerException("Socket not connected.") from e

	def start(self, host, port, role):
		self.role = role
		if role == protocol.CLIENT_ROLE:
			self.connect(host, port)
		else:
			self.listen(host, port)
		t = threading.Thread(target = self.recv)
		self.running = True
		t.start()

	def stop(self):
		self.running = False
		try:
			self.socket.shutdown(socket.SHUT_RDWR)
		except OSError: #Was never connected or already closed
			pass
		self.socket.close()
		if self.role == protocol.SERVER_ROLE:
			self.serverSocket.close()

	def consumeMessages(self):
		messages = self.messageQueue
		self.messageQueue = []
		return messages

	def raiseLastError(self):
		raise MessengerException("Connection closed.") from self.lastError

