import socket
import threading
import logging
from communication import protocol
from communication.exceptions import MessengerException


class Messenger(object):
    """Handles all communications with another user.

    Args:
        socket: Handle to the connection with the other user.
    """

    def __init__(self, socket):
        self.socket = socket
        self.message_queue = []
        self.running = False
        self.last_error = None
        self.logger = logging.getLogger(__name__)

    def run(self):
        """Starts listening for messages."""
        self.logger.info("Starting messenger.")
        self.recv()

    def stop(self):
        """Stops listening for messages."""
        self.logger.info("Stopping messenger.")
        self.running = False

    def recv(self):
        """Listens continuously for incoming messages and hands them over to the message callback."""
        self.running = True
        buffer = b''
        while self.running:
            try:
                mess = self.socket.recv(1024)
            except Exception as e:
                self.logger.info("There was an error during socket.recv.", exc_info=True)
                # TODO: Add optional (True) fail on error parameter
                # this part was added so child classes can handle the error themselves
                # they should pass that parameter as False when calling super()
                # TODO: Add corresponding docstring mention
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
        """Sends the given message to the remote user to which it's connected.

        Args:
            message: The message to send.

        Raises:
            MessengerException: This error will be raised if there are connection issues while sending 
            the message.
        """
        form_message = message + protocol.MESSAGE_SEPARATOR
        sent = 0
        while sent < len(form_message):
            try:
                sent += self.socket.send(form_message[sent:])
            except (socket.error, AttributeError) as e:
                self.logger.critical("Error while sending message.", exc_info=True)
                raise MessengerException("Socket not connected.") from e

    def consume_message(self):
        """Consumes the first message from the queue.

        Returns:
            A message or None if the queue is empty.
        """
        if len(self.message_queue) > 0:
            message = self.message_queue[0]
            self.message_queue = self.message_queue[1:]
            return message
        return None

    def consume_messages(self):
        """Consumes all messages in the queue.

        Returns:
            A list of messages or an empty list if the queue is empty.
        """
        messages = self.message_queue
        self.message_queue = []
        return messages

    # TODO: Rename or make property and document
    def num_pending_messages(self):
        return len(self.message_queue)

    def message_callback(self):
        """Does nothing by default.
        This function will be called when a message is received and can be overwriten 
        to do any kind of necessary processing on received messages.
        """
        pass

    # TODO: Should be a property, no?
    def set_message_callback(self, callback):
        """Overwrites the current message callback.

        Args:
            callback: The new function that'll be called when a message is received.
        """
        self.message_callback = callback

    def raise_last_error_if_any(self):
        """Raises the last error that might have occured in the remote thread that deals with reception.

        Raises:
            MessengerException: Will always be raised."""
        if self.last_error:
            # TODO: Figure out what happens to the hardcoded message when using 'from'
            raise MessengerException("Connection closed.") from self.last_error
