import os, time, sys
from communication import protocol, messenger, encrypted_messenger
import interface
from encryption import crypter
import keys.utils
from communication.messenger_exception import MessengerException
from encryption.crypter_exceptions import CrypterException

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

	############################
	#SETUP MESSENGER CONNECTION#
	############################

	#Check starting role argument
	if len(sys.argv) < 2:
		print("Missing role argument. Specify SERVER or CLIENT role.")
		print("CLIENT role defined as default.")
		role = protocol.CLIENT_ROLE
	else:
		role = sys.argv[1]
		if role not in [protocol.SERVER_ROLE, protocol.CLIENT_ROLE]:
			print("Unknown role. Specify SERVER or CLIENT role.")
			quit()

	if role == protocol.SERVER_ROLE:
		host = HOST
	else:
		host = HOST#input("Enter server ip: ")

	#Start messenger server/client
	print("Starting messenger, waiting for connection...")
	m = encrypted_messenger.EncryptedMessenger(verbose = True)
	try:
		m.start(host, PORT, role)
	except (MessengerException, CrypterException, ValueError, KeyboardInterrupt) as e:
		printExcAndCause(e)
		m.stop()
		quit()


	###########################
	#START MESSAGING INTERFACE#
	###########################


	#Start interface to link messenger/crypter/stdout/stdin
	def handleOutgoing(message):
		#TODO: Check if this belongs here or in messenger or in crypter
		try:
			messBytes = message.encode('utf8') + b"\x00"
		except UnicodeError:
			print("Forbidden characters. Message was not sent.")
			return

		try:
			m.send(messBytes)
		except MessengerException as e:
			printExcAndCause(e)
			print("Message was not sent.")
			i.stop()
			m.stop()
			quit()

	i = interface.Interface(m.consumeMessages, handleOutgoing)

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
