import os, time, sys
import protocol, messenger, interface, crypter, keys.utils
from messenger_exception import MessengerException
from crypter_exceptions import CrypterException

HOST = 'localhost'
PORT = 4664

def hideCryptographyExit():
    sys.stderr.flush()
    newstderr = os.dup(2)
    devnull = os.open(os.devnull, os.O_WRONLY)
    os.dup2(devnull, 2)
    os.close(devnull)
    sys.stderr = os.fdopen(newstderr, 'w')

def printExcAndCause(exc):
	if hasattr(exc, '__cause__'):
		print(exc, ":", exc.__cause__)
	else:
		print(exc)

def quit():
	print("Aborting execution.")
	input("Press any key to exit...")
	sys.exit()

if __name__ == '__main__':
	#Check starting role argument
	if len(sys.argv) < 2:
		print("Missing role argument. Specify SERVER or CLIENT role.")
		quit()

	role = sys.argv[1]
	if role not in [protocol.SERVER_ROLE, protocol.CLIENT_ROLE]:
		print("Unknown role. Specify SERVER or CLIENT role.")
		quit()

	if role == protocol.SERVER_ROLE:
		host = HOST
	else:
		host = input("Enter server ip: ")

	#Start messenger server/client
	print("Starting messenger, waiting for connection...")
	m = messenger.Messenger()
	try:
		m.start(host, PORT, role)
	except MessengerException as e:
		printExcAndCause(e)
		m.stop()
		quit()

	#Start crypter and load/gen/send/recv necessary keys
	c = crypter.Crypter(os.urandom)
	#If we're the server load the private key and wait for the AES key
	try:
		if role == protocol.SERVER_ROLE:
			c.loadRsaKey(keys.utils.PRIVATE)
			print("Waiting for AES key.")
			while len(m.messageQueue) == 0:
				m.raiseLastErrorIfAny()
				time.sleep(1)
			encryptedKey = m.messageQueue[0]
			m.messageQueue = m.messageQueue[1:]
			key = c.decryptKey(encryptedKey)
			c.aesKey = key
		#If we're the client load the public key and gen and send AES key
		else:
			c.loadRsaKey(keys.utils.PUBLIC)
			c.genAndSetAesKey()
			encryptedKey = c.encryptKey(c.aesKey)
			m.send(encryptedKey)
	except (MessengerException, CrypterException) as e:
		printExcAndCause(e)
		m.stop()
		quit()


	#Start interface to link messenger/crypter/stdout/stdin
	def handleOutgoing(message):
		try:
			messBytes = message.encode('utf8') + b"\x00"
		except UnicodeError:
			print("Forbidden characters. Message was not sent.")
			return
		encrypted = c.encryptMessage(messBytes)
		try:
			m.send(encrypted)
		except MessengerException as e:
			printExcAndCause(e)
			print("Message was not sent.")
			i.stop()
			m.stop()
			quit()

	def handleIncoming():
		encMessages = m.consumeMessages()
		messages = [c.decryptMessage(mess) for mess in encMessages]
		return messages

	i = interface.Interface(handleIncoming, handleOutgoing)

	print("Starting messaging session. Press Ctrl+C to quit at any time.")
	try:
		i.start()
	except KeyboardInterrupt:
		print("") #Get over input line
		print("Closing messaging session.")

	#Clean it all and exit
	i.stop()
	m.stop()
	input("Press any key to exit...")
	hideCryptographyExit()
