import socket
import logging

class SocketManager(object):
    "Socket manager that cleans itself on exit."

    def __init__(self, socket=None):
        self.socket = socket
        self.logger = logging.getLogger(__name__)

    def __enter__(self):
        if not self.socket:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.logger.info("Created new socket %s.", str(self.socket))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        "Closes the open sockets and set shutdown flag for running threads."
        self.logger.info("Closing socket %s.", str(self.socket))
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
        except OSError:  # Was never connected or already closed
            pass
        finally:
            self.socket.close()

    def close(socket):
        with SocketManager(socket): pass
