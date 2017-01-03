import socket
import threading
from communication.server_exception import ServerException
from communication.socket_manager import SocketManager


class Server(SocketManager):
    "Server object that handles socket logic for incoming connections."

    def __init__(self, host, port):
        "Creates a server object."
        super().__init__()
        self.host = host
        self.port = port
        self.sockets = []
        self.running = False

    def __exit__(self, exc_type, exc_val, exc_tb):
        "Closes the open sockets and set shutdown flag for running threads."
        self.running = False
        # Create a socket manager for each connection just to let it close
        for socket in self.sockets:
            with SocketManager(socket):
                pass
        super().__exit__(exc_type, exc_val, exc_tb)

    def listen(self, handle_incoming_connection):
        "Binds a socket to the given address and listens and accepts one incoming connection."
        try:
            self.socket.bind((self.host, self.port))
        except socket.error as e:
            raise ServerException("Another program is already using this port.") from e

        self.running = True
        self.socket.listen(1)
        while self.running:
            try:
                connection, addr = self.socket.accept()
            except OSError: # In case the bound socket is closed
                self.running = False
                break
            self.sockets.append(connection)
            t = threading.Thread(target=handle_incoming_connection,
                                 args=[connection, addr])
            t.start()
