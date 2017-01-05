

class NetworkException(Exception):
    pass

class CommandFailureError(NetworkException):
    pass

class UnexpectedResponseError(NetworkException):
    pass


class UserDoesNotExistError(NetworkException):
    pass


class ChallengeFailureError(NetworkException):
    pass
