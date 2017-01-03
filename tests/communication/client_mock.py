import socket

class ClientMock():

    def __init__(self, host, port):
        self.host, self.port = host, port
        self.connected = False

    def __enter__(self):
        self.client_socket = socket.socket()
        self.client_socket.connect((self.host, self.port))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client_socket.close()
