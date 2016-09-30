import os, time
import messenger, crypter, protocol, keys.utils

class EncryptedMessenger(messenger.Messenger):
	"Messenger object with cryptographic capabilities"
	def __init__(self, verbose = False):
		super().__init__()
		self.crypter = crypter.Crypter(os.urandom)
		self.verbose = verbose


	def printIfVerbose(self, *args):
		if self.verbose:
			print(*args)

	def performHandshakeAsServer(self):
		self.crypter.loadRsaKey(keys.utils.PRIVATE)
		encryptedKey = None
		while not encryptedKey:
			encryptedKey = super().consumeMessage()
			self.raiseLastErrorIfAny()
			time.sleep(1)

		self.crypter.aesKey = self.crypter.decryptKey(encryptedKey)

	def performHandshakeAsClient(self):
		self.crypter.loadRsaKey(keys.utils.PUBLIC)
		self.crypter.genAndSetAesKey()
		encryptedKey = self.crypter.encryptKey(self.crypter.aesKey)
		super().send(encryptedKey)

	def send(self, message):
		encrypted = self.crypter.encryptMessage(message)
		super().send(encrypted)

	def consumeMessage(self):
		message = super().consumeMessage()
		return self.crypter.decryptMessage(message)

	def consumeMessages(self):
		messages = super().consumeMessages()
		return [self.crypter.decryptMessage(mess) for mess in messages]

	def start(self, host, port, role):
		self.printIfVerbose("Attempting to connect with remote as " + str(role) + " ...")

		super().start(host, port, role)

		self.printIfVerbose("Succesful connection.")
		self.printIfVerbose("Attempting handshake...")

		if role == protocol.SERVER_ROLE:
			self.performHandshakeAsServer()
		elif role == protocol.CLIENT_ROLE:
			self.performHandshakeAsClient()
		else:
			raise ValueError("Wrong role.") #huehue

		self.printIfVerbose("Succesful handshake.")




