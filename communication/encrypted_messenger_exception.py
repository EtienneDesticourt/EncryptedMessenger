

class EncryptedMessengerException(Exception):
    pass

class HandshakeFailure(EncryptedMessengerException):
    pass

class HandshakeTimeout(HandshakeFailure):
    pass
