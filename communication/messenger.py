import socket
import threading
import logging
from communication import protocol
from communication.messenger_exception import MessengerException


class Messenger(object):
    "Messenger object that handles socket logic to communicate to and fro two PCs."

    def __init__(self, socket):
        "Creates a messenger object."
        self.socket = socket
        self.message_queue = []
        self.running = False
        self.last_error = None
        self.logger = logging.getLogger(__name__)

    def run(self):
        self.logger.info("Starting messenger.")
        self.recv()

    def stop(self):
        self.logger.info("Stopping messenger.")
        self.running = False

    def recv(self):
        "Handles the reception of the messages from a remote Messenger object and adds them to the message queue."
        self.running = True
        buffer = b''
        while self.running:
            try:
                mess = self.socket.recv(1024)
            except Exception as e:
                self.logger.info("There was an error during socket.recv.", exc_info=True)
                self.last_error = e
                self.running = False
                break

            if len(mess) == 0:
                self.logger.info("Received empty string from socket.")
                self.running = False
                break

            buffer += mess
            # Parse messages from buffer
            messages = buffer.split(protocol.MESSAGE_SEPARATOR)
            # Set buffer to last incomplete message or '' if ending on a
            # separator
            buffer = messages.pop()
            self.message_queue += messages
            if len(messages):
                self.message_callback()
        self.logger.info("Messenger stopped.")

    def send(self, message):
        "Sends the given message to the remote Messenger to which this one is currently connected."
        form_message = message + protocol.MESSAGE_SEPARATOR
        sent = 0
        while sent < len(form_message):
            try:
                sent += self.socket.send(form_message[sent:])
            except (socket.error, AttributeError) as e:
                self.logger.critical("Error while sending message.", exc_info=True)
                raise MessengerException("Socket not connected.") from e

    def consume_message(self):
        "Returns the content of the first message and removes it from the queue."
        if len(self.message_queue) > 0:
            message = self.message_queue[0]
            self.message_queue = self.message_queue[1:]
            return message
        return None

    def consume_messages(self):
        "Returns the content of the message queue and empties it."
        messages = self.message_queue
        self.message_queue = []
        return messages

    def num_pending_messages(self):
        return len(self.message_queue)

    def message_callback(self):
        pass

    def set_message_callback(self, callback):
        self.message_callback = callback

    def raise_last_error_if_any(self):
        "Raises the last error that might have occured in the remote thread that deals with reception."
        if self.last_error:
            raise MessengerException("Connection closed.") from self.last_error
