from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature, UnsupportedAlgorithm
import os, math
from keys import utils
import protocol
from crypter_exception import CrypterException

def DEFAULT_PADDING():
    return padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None)

class Crypter(object):
    def __init__(self, role):
        self.role = role
        if role == protocol.CLIENT_ROLE:
            keyType = utils.PUBLIC
            self.aesKey = os.urandom(32)
        elif role == protocol.SERVER_ROLE:
            keyType = utils.PRIVATE
            self.aesKey = None
        else:
            raise CrypterException("Unknown role.")

        try:
            self.rsaKey = utils.loadKey(keyType)
        except (FileNotFoundError, ValueError, UnsupportedAlgorithm) as e:
            raise CrypterException("Unable to load RSA key.") from e

    def genHmac(self, iv, encMess):
        h = hmac.HMAC(self.aesKey, hashes.SHA256(), backend=default_backend())
        h.update(iv)
        h.update(encMess)
        return h

    def encryptMessage(self, message):
        if not self.aesKey:
            raise CrypterException("Can't encrypt message. Key hasn't been received from client yet.")

        #Pad message for mode
        paddingLength = math.ceil(len(message) / 16) * 16 - len(message)
        message += paddingLength * b"0"

        #Random init vector
        iv = os.urandom(16)

        #Encrypt message
        aes = Cipher(algorithms.AES(self.aesKey), modes.CBC(iv), backend=default_backend())
        encryptor = aes.encryptor()
        encArray = encryptor.update(message) + encryptor.finalize()

        #Gen auth data
        h = self.genHmac(iv, encArray)
        hmacBytes = h.finalize()

        return iv + encArray + hmacBytes

    def decryptMessage(self, message):
        if not self.aesKey:
            raise CrypterException("Can't decrypt message. Key hasn't been received from client yet.")

        if len(message) < 16 + 32 + 1:
            raise CrypterException("Corrupted message.")

        iv = message[:16]
        encMess = message[16:-32]
        hmacBytes = message[-32:]

        #Verify auth
        h = self.genHmac(iv, encMess)
        try:
            h.verify(hmacBytes)
        except InvalidSignature as e:
            raise CrypterException("Corrupted message.") from e

        #Decrypt message if there was no error
        aes = Cipher(algorithms.AES(self.aesKey), modes.CBC(iv), backend=default_backend())
        decryptor = aes.decryptor()
        message = decryptor.update(encMess) + decryptor.finalize()

        message = message.decode('utf8')
        message = message.split('\0')[0]
        return message

    def encryptKey(self, rawKey):
        if self.role != protocol.CLIENT_ROLE:
            raise CrypterException("Wrong role for encryptKey. The client is in charge of encrypting the AES key.")
        encKey = self.rsaKey.encrypt(rawKey, DEFAULT_PADDING())
        return encKey

    def decryptKey(self, encKey):
        if self.role != protocol.SERVER_ROLE:
            raise CrypterException("Wrong role for decryptKey. The server is in charge of decrypting the AES key.")
        rawKey = self.rsaKey.decrypt(encKey, DEFAULT_PADDING())
        return rawKey
