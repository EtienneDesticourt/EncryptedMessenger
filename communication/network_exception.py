

class NetworkException(Exception):
    pass


class UnexpectedResponseError(NetworkException):
    pass


class UserDoesNotExistError(NetworkException):
    pass


class ChallengeFailureError(NetworkException):
    pass
