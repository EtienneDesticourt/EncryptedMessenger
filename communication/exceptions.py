

class CommunicationException(Exception):
    pass


class EncryptedMessengerException(CommunicationException):
    pass


class HandshakeFailureException(EncryptedMessengerException):
    pass


class HandshakeTimeoutException(HandshakeFailureException):
    pass


class ClientException(CommunicationException):
    pass


class MessengerException(CommunicationException):
    pass


class NetworkException(CommunicationException):
    pass


class CommandFailureError(NetworkException):
    pass


class UnexpectedResponseError(NetworkException):
    pass


class UserDoesNotExistError(NetworkException):
    pass


class ChallengeFailureError(NetworkException):
    pass


class ServerException(CommunicationException):
    pass
