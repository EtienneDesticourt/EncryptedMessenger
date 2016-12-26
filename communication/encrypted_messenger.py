import os, time
from communication import messenger, protocol
from encryption import crypter
import keys.utils

class EncryptedMessenger(messenger.Messenger):
	"Messenger object with cryptographic capabilities"
	def __init__(self, verbose = False):
		super().__init__()
		self.crypter = crypter.Crypter(os.urandom)
		self.verbose = verbose


	def printIfVerbose(self, *args):
		if self.verbose:
			print(*args)

	def waitForNextMessage(self):
		message = None
		while not message:
			message = super().consumeMessage()
			self.raiseLastErrorIfAny()
			time.sleep(1)
		return message

	def performHandshakeAsServer(self):
		#TODO: Uncomment and add auth
		#self.crypter.loadRsaKey(keys.utils.PRIVATE)

		self.printIfVerbose("Generating new RSA key and sending to client.")
		self.crypter.genAndSetRsaKey()
		publicRsaKey = self.crypter.getPublicKeyPem()
		super().send(publicRsaKey)

		self.printIfVerbose("Waiting for AES key from client.")
		encryptedAesKey = self.waitForNextMessage()

		self.crypter.aesKey = self.crypter.decryptKey(encryptedAesKey)

	def performHandshakeAsClient(self):
		#TODO: Uncomment and add auth
		#self.crypter.loadRsaKey(keys.utils.PUBLIC)

		self.printIfVerbose("Waiting for ephemeral RSA key from server.")
		publicKeyPem = self.waitForNextMessage()
		self.crypter.setPublicKeyFromPem(publicKeyPem)

		self.printIfVerbose("Generating new AES key and sending to server.")
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

		self.printIfVerbose("Succesful connection.\n")
		self.printIfVerbose("Attempting handshake...")

		if role == protocol.SERVER_ROLE:
			self.performHandshakeAsServer()
		elif role == protocol.CLIENT_ROLE:
			self.performHandshakeAsClient()
		else:
			raise ValueError("Wrong role.") #huehue

		self.printIfVerbose("Succesful handshake.\n")




