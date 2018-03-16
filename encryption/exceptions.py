

class CrypterException(Exception):
    pass


class NoKeyException(CrypterException):
    pass


class CorruptedMessageException(CrypterException):
    pass

class BackendException(CrypterException):
    pass

class InvalidSignature(BackendException):
    pass