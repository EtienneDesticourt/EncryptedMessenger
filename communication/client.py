import socket
from communication.client_exception import ClientException
from communication.socket_manager import SocketManager


class Client(SocketManager):
    "Client object that handles socket logic for outgoing connections."

    def __init__(self, host, port):
        "Creates a client object."
        self.host = host
        self.port = port

    def __enter__(self):
        "Starts the server and binds to the given address."
        super().__enter__()
        self.connect()
        return self

    def connect(self):
        "Connects the client's socket to the given address."
        try:
            self.socket.connect((self.host, self.port))
        except ConnectionRefusedError as e:
            raise ClientException("No host listening.") from e
