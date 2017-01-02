

class SocketManager(object):
    "Socket manager that cleans itself on exit."

    def __init__(self, socket=None):
        self.socket = socket

    def __enter__(self):
        if not self.socket:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        "Closes the open sockets and set shutdown flag for running threads."
        self.running = False
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
        except OSError:  # Was never connected or already closed
            pass
        else:
            self.socket.close()
