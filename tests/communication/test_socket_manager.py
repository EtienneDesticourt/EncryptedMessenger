import socket
import unittest
from communication.socket_manager import SocketManager

class SocketMock(object):

    def __init__(self, error):
        self.error = error
        self.shutdown_called = False
        self.close_called = False
        self.shutdown_reason = None

    def shutdown(self, reason):
        self.shutdown_called = True
        self.shutdown_reason = reason
        if self.error:
            raise self.error

    def close(self):
        self.close_called = True

class TestException(Exception):
    pass

class TestSocketManager(unittest.TestCase):

    def test_enter(self):
        with SocketManager() as manager:
            assert type(manager) == SocketManager
            assert hasattr(manager, 'socket')
            assert manager.socket != None
            assert manager.socket.family == socket.AF_INET
            assert manager.socket.type == socket.SOCK_STREAM

    def test_exit_no_error(self):
        mock = SocketMock(error=False)
        with SocketManager(mock) as manager:
            pass
        assert mock.shutdown_called
        assert mock.shutdown_reason == socket.SHUT_RDWR
        assert mock.close_called

    def test_exit_oserror(self):
        mock = SocketMock(error=OSError)
        with SocketManager(mock) as manager:
            pass
        assert mock.shutdown_called
        assert mock.shutdown_reason == socket.SHUT_RDWR
        assert mock.close_called

    def test_exit_other_error(self):
        mock = SocketMock(error=TestException)
        try:
            with SocketManager(mock) as manager:
                pass
        except TestException:
            pass
        else:
            assert False

        assert mock.shutdown_called
        assert mock.shutdown_reason == socket.SHUT_RDWR
        assert mock.close_called
