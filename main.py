import os
import time
import sys
from communication import protocol
from communication import messenger
from communication.encrypted_messenger import EncryptedMessenger
from communication.messenger_exception import MessengerException
from encryption import crypter
from encryption.crypter_exceptions import CrypterException
import interface
import keys.utils

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

    # Check starting role argument
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
        host = HOST  # input("Enter server ip: ")

    def gen_messenger_handle(messenger):
        def handle_outgoing(message):
            # TODO: Check if this belongs here or in messenger or in
            # crypter
            try:
                mess_bytes = message.encode('utf8') + b"\x00"
            except UnicodeError:
                print("Forbidden characters. Message was not sent.")
                return

            try:
                messenger.send(mess_bytes)
            except MessengerException as e:
                printExcAndCause(e)
                print("Message was not sent.")
                i.stop()
                quit()
        return handle_outgoing

    # Start messenger server/client
    print("Starting messenger, waiting for connection...")

    try:
        with EncryptedMessenger(role, host, PORT, verbose=True) as messenger:
            handle_outgoing = gen_messenger_handle(messenger)
            # Start interface to link messenger/crypter/stdout/stdin
            i = interface.Interface(messenger.consume_messages, handle_outgoing)
            print("Starting messaging session. Press Ctrl+C to quit at any time.")
            try:
                i.run()
            except KeyboardInterrupt as e:
                i.stop()
    except (MessengerException, CrypterException, ValueError, KeyboardInterrupt) as e:
        printExcAndCause(e)

    print("")  # Get over input line
    print("Closing messaging session.")
    input("Press any key to exit...")
    hideCryptographyExit()
