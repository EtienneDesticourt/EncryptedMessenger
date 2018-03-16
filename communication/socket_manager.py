import socket
import logging

class SocketManager(object):
    """Manages the lifecycle of a socket handle.

    Args:
        socket: An optional existing socket.
    """

    def __init__(self, socket=None):
        self.socket = socket
        self.logger = logging.getLogger(__name__)

    def __enter__(self):
        if not self.socket:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.logger.info("Created new socket %s.", str(self.socket))
        return self

    def __exit__(self, *a):
        self.logger.info("Closing socket %s.", str(self.socket))
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
        except OSError:  # Was never connected or already closed
            pass
        finally:
            self.socket.close()

    def close(socket):
        """Closes the connection.

        Args:
            socket: The socket handle to the connection we which to close.
        """
        # self.__exit__() # TODO: Try this out to fix this fuckup
        with SocketManager(socket): pass
