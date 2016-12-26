import socket
import threading
from communication import protocol
from communication.messenger_exception import MessengerException


class Messenger(object):
    "Messenger object that handles socket logic to communicate to and fro two PCs."

    def __init__(self):
        "Creates a messenger object."
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.message_queue = []
        self.running = False
        self.role = None
        self.last_error = None

    def listen(self, host, port):
        "Binds a socket to the given address and listens and accepts one incoming connection."
        try:
            self.socket.bind((host, port))
        except socket.error as e:
            raise MessengerException("Other program already using port.") from e
        # For testing purposes... It's not great
        self.host, self.port = self.socket.getsockname()
        self.socket.listen(1)
        client_sock, addr = self.socket.accept()
        self.server_socket = self.socket
        self.socket = client_sock

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
                self.last_error = e
                self.stop()
                return

            # Parse messages from buffer
            messages = buffer.split(protocol.MESSAGE_SEPARATOR)
            # Set buffer to last incomplete message or '' if ending on a
            # separator
            buffer = messages.pop()
            self.message_queue += messages

    def send(self, message):
        "Sends the given message to the remote Messenger to which this one is currently connected."
        form_message = message + protocol.MESSAGE_SEPARATOR
        sent = 0
        while sent < len(form_message):
            try:
                sent += self.socket.send(form_message[sent:])
            except socket.error as e:
                raise MessengerException("Socket not connected.") from e

    def start(self, host, port, role):
        "Starts the Messenger and binds/connects to the given address depending on given CLIENT/SERVER role."
        self.role = role
        if role == protocol.CLIENT_ROLE:
            self.connect(host, port)
        else:
            self.listen(host, port)
        t = threading.Thread(target=self.recv)
        self.running = True
        t.start()

    def stop(self):
        "Closes the open sockets and set shutdown flag for running threads."
        self.running = False
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
        except OSError:  # Was never connected or already closed
            pass
        self.socket.close()
        if self.role == protocol.SERVER_ROLE:
            self.server_socket.close()

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

    def raise_last_error_if_any(self):
        "Raises the last error that might have occured in the remote thread that deals with reception."
        if self.last_error:
            raise MessengerException("Connection closed.") from self.last_error