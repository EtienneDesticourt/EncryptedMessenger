import threading
import logging
from communication.exceptions import ServerException
from communication.socket_manager import SocketManager


class Server(SocketManager):
    """A server to listen for and manage incoming connections.

    Args:
        host: The address to which to bind the server.
        port: The port to listen on.
    """

    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.sockets = []
        self.running = False
        self.logger = logging.getLogger(__name__)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.running = False
        # Create a socket manager for each connection just to let it close
        for socket in self.sockets:
            with SocketManager(socket):
                pass
        super().__exit__(exc_type, exc_val, exc_tb)

    def listen(self, handle_incoming_connection):
        """Listens for incoming connections indefinitely.

        Args:
            handle_incoming_connection: A callback that will be called asynchronously and takes a socket handle as parameter.
        """
        self.logger.info("Server started listening.")
        try:
            self.socket.bind((self.host, self.port))
            self.logger.info("Bound socket on %s:%s with socket %s.", self.host, str(self.port), str(self.socket))
        except OSError as e:
            self.logger.critical("Socket error while trying to bind socket on %s:%s", self.host, str(self.port), exc_info=True)
            raise ServerException("Another program is already using this port.") from e

        self.running = True
        self.socket.listen(1)
        self.logger.info("Waiting for incoming connections.")
        while self.running:
            try:
                connection, (ip, port) = self.socket.accept()
                self.logger.info("New connection from ip %s.", ip)
            except OSError: # In case the bound socket is closed
                self.running = False
                break
            self.sockets.append(connection)
            t = threading.Thread(target=handle_incoming_connection,
                                 args=[connection, ip])
            t.start()
        self.logger.info("Stopped listening for incoming connections.")
