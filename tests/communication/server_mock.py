import socket
import threading

class ServerMock():

    def __init__(self, host, port):
        self.host, self.port = host, port
        self.connected = False

    def __enter__(self):
        self.socket = socket.socket()
        self.socket.bind((self.host, self.port))
        ip, self.port = self.socket.getsockname()
        self.socket.listen(1)

        # Wait for connection from messenger
        def accept_client_conn():
            try:
                self.client_socket, addr = self.socket.accept()
            except OSError:
                return
            self.connected = True
        threading.Thread(target=accept_client_conn).start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connected:
            self.client_socket.close()
        self.socket.close()
