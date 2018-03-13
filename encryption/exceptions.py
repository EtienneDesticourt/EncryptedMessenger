

class CrypterException(Exception):
    pass


class NoKeyException(CrypterException):
    pass


class CorruptedMessageException(CrypterException):
    pass
