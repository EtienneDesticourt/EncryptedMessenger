from cryptography.hazmat.primitives.serialization import load_pem_private_key, Encoding, PublicFormat, load_pem_public_key
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.exceptions import InvalidSignature, UnsupportedAlgorithm
import os, math
from keys import utils
import protocol
from crypter_exceptions import CrypterException, NoKeyException, CorruptedMessageException

DEFAULT_KEY_DIR = "keys"
DEFAULT_EXPONENT = 65537
DEFAULT_RSA_KEY_SIZE = 2048

def DEFAULT_PADDING():
    return padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None)

class Crypter(object):
    "Cryptography wrapper that provides convenience functions to crypt/decrypt keys and messages."
    def __init__(self, RNG):
        "Takes a random number generating function and creates a Crypter object with it."
        self.rsaKey = None
        self.aesKey = None
        self.RNG = RNG

    def loadRsaKey(self, keyType, directory=DEFAULT_KEY_DIR):
        "Loads a public/private RSA key in the given directory (optional) depending on given keyType."
        try:
            self.rsaKey = utils.loadKey(keyType, directory)
        except (FileNotFoundError, ValueError, UnsupportedAlgorithm) as e:
            raise CrypterException("Unable to load RSA key.") from e
        self.keyType = keyType

    def genAndSetRsaKey(self):
        "Generates a new RSA key pair."
        self.keyType = utils.PRIVATE
        self.rsaKey = rsa.generate_private_key(public_exponent=DEFAULT_EXPONENT,
            key_size=DEFAULT_RSA_KEY_SIZE,
            backend=default_backend())

    def setPublicKeyFromPem(self, pemData):
        self.keyType = utils.PUBLIC
        self.rsaKey = load_pem_public_key(pemData, backend=default_backend())

    def getPublicKeyPem(self):
        if self.keyType == utils.PRIVATE:
            publicKey = self.rsaKey.public_key()
        elif self.keyType == utils.PUBLIC:
            publicKey = self.rsaKey
        else:
            raise ValueError("Wrong key type.")
        return publicKey.public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)

    def genAndSetAesKey(self):
        "Generates a 32 bytes AES key and returns it. It'll be used by the Crypter from hereon."
        self.aesKey = self.RNG(32)
        return self.aesKey

    def genHmac(self, iv, encMess):
        "Generates 32 bytes of HMAC from a given initialization vector and encrypted message."
        h = hmac.HMAC(self.aesKey, hashes.SHA256(), backend=default_backend())
        h.update(iv)
        h.update(encMess)
        return h

    def encryptMessage(self, message):
        "Encrypts the given message using the Crypter's AES key."
        if not self.aesKey:
            raise NoKeyException("Cannot encrypt message: AES key hasn't been set.")

        #Pad message for mode
        paddingLength = math.ceil(len(message) / 16) * 16 - len(message)
        message += paddingLength * b"0"

        #Random init vector
        iv = self.RNG(16)

        #Encrypt message
        aes = Cipher(algorithms.AES(self.aesKey), modes.CBC(iv), backend=default_backend())
        encryptor = aes.encryptor()
        encArray = encryptor.update(message) + encryptor.finalize()

        #Gen auth data
        h = self.genHmac(iv, encArray)
        hmacBytes = h.finalize()

        return iv + encArray + hmacBytes

    def decryptMessage(self, message):
        "Decrypts the given message using the Crypter's AES key."
        if not self.aesKey:
            raise NoKeyException("Cannot decrypt message: AES key hasn't been set.")

        if len(message) < 16 + 32 + 1:
            raise CorruptedMessageException()

        iv = message[:16]
        encMess = message[16:-32]
        hmacBytes = message[-32:]

        #Verify auth
        h = self.genHmac(iv, encMess)
        try:
            h.verify(hmacBytes)
        except InvalidSignature as e:
            raise CorruptedMessageException() from e

        #Decrypt message if there was no error
        aes = Cipher(algorithms.AES(self.aesKey), modes.CBC(iv), backend=default_backend())
        decryptor = aes.decryptor()
        message = decryptor.update(encMess) + decryptor.finalize()

        #This doesn't belong here: crypter doesn't necessarily want to handle strings
        #long term we want to pass message length in message and simply cut the padding
        #And let messenger or interface decode
        #Kinda too lazy to do that right now, mby later
        message = message.decode('utf8')
        message = message.split('\0')[0]
        return message

    def encryptKey(self, rawKey):
        "Encrypts the given key using the Crypter's RSA key."
        if self.rsaKey == None:
            raise NoKeyException("Cannot encrypt AES key: RSA key hasn't been loaded.")
        if self.keyType != utils.PUBLIC:
            raise CrypterException("Cannot encrypt key. Public RSA key required.")
        encKey = self.rsaKey.encrypt(rawKey, DEFAULT_PADDING())
        return encKey

    def decryptKey(self, encKey):
        "Decrypts the given key using the Crypter's RSA key."
        if self.rsaKey == None:
            raise NoKeyException("Cannot decrypt AES key: RSA key hasn't been loaded.")
        if self.keyType != utils.PRIVATE:
            raise CrypterException("Cannot decrypt key. Private RSA key required.")
        rawKey = self.rsaKey.decrypt(encKey, DEFAULT_PADDING())
        return rawKey
