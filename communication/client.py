import logging
from communication.exceptions import ClientException
from communication.socket_manager import SocketManager


class Client(SocketManager):
    """Client object that handles socket logic for outgoing connections.

    Args:
        host: The address of the host.
        port: The port to open.
    """

    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.logger = logging.getLogger(__name__)

    def connect(self):
        """Connects the client's socket to the given address.

        Raises:
            ClientException: A client exception is raised when the client was unable to connect at the given host and port.
        """
        try:
            self.socket.connect((self.host, self.port))
            self.logger.info("Succesfully connected to %s:%s with socket %s.", self.host, str(self.port), str(self.socket))
        except (ConnectionRefusedError, TimeoutError) as e:
            raise ClientException("No host listening.") from e
