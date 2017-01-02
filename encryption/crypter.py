import math

from cryptography.hazmat.primitives.serialization import load_pem_private_key, Encoding, PublicFormat, load_pem_public_key
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.exceptions import InvalidSignature, UnsupportedAlgorithm

from communication import protocol
from encryption.crypter_exceptions import CrypterException, NoKeyException, CorruptedMessageException
from keys import utils
import config

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
        self.rsa_key = None
        self.aes_key = None
        self.RNG = RNG

    def load_rsa_key(self, key_type, directory=config.KEY_DIR):
        "Loads a public/private RSA key in the given directory (optional) depending on given keyType."
        try:
            self.rsa_key = utils.load_key(key_type, directory)
        except (FileNotFoundError, ValueError, UnsupportedAlgorithm) as e:
            raise CrypterException("Unable to load RSA key.") from e
        self.key_type = key_type

    def gen_and_set_rsa_key(self):
        "Generates a new RSA key pair."
        self.key_type = utils.PRIVATE
        self.rsa_key = rsa.generate_private_key(public_exponent=DEFAULT_EXPONENT,
                                                key_size=DEFAULT_RSA_KEY_SIZE,
                                                backend=default_backend())

    def set_public_key_from_pem(self, pem_data):
        self.key_type = utils.PUBLIC
        self.rsa_key = load_pem_public_key(pem_data, backend=default_backend())

    def get_public_key_pem(self):
        if self.key_type == utils.PRIVATE:
            public_key = self.rsa_key.public_key()
        elif self.key_type == utils.PUBLIC:
            public_key = self.rsa_key
        else:
            raise CrypterException("Wrong key type.")
        return public_key.public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)

    def gen_and_set_aes_key(self):
        "Generates a 32 bytes AES key and returns it. It'll be used by the Crypter from hereon."
        self.aes_key = self.RNG(32)
        return self.aes_key

    def gen_hmac(self, iv, encrypted_message):
        "Generates 32 bytes of HMAC from a given initialization vector and encrypted message."
        h = hmac.HMAC(self.aes_key, hashes.SHA256(), backend=default_backend())
        h.update(iv)
        h.update(encrypted_message)
        return h

    def encrypt_message(self, message):
        "Encrypts the given message using the Crypter's AES key."
        if not self.aes_key:
            raise NoKeyException(
                "Cannot encrypt message: AES key hasn't been set.")

        # Pad message for mode
        padding_length = math.ceil(len(message) / 16) * 16 - len(message)
        message += padding_length * b"0"

        # Random init vector
        iv = self.RNG(16)

        # Encrypt message
        aes = Cipher(algorithms.AES(self.aes_key),
                     modes.CBC(iv), backend=default_backend())
        encryptor = aes.encryptor()
        enc_array = encryptor.update(message) + encryptor.finalize()

        # Gen auth data
        h = self.gen_hmac(iv, enc_array)
        hmac_bytes = h.finalize()

        return iv + enc_array + hmac_bytes

    def decrypt_message(self, message):
        "Decrypts the given message using the Crypter's AES key."
        if not self.aes_key:
            raise NoKeyException("Cannot decrypt message: AES key hasn't been set.")

        if len(message) < 16 + 32 + 1:
            raise CorruptedMessageException()

        iv = message[:16]
        enc_mess = message[16:-32]
        hmac_bytes = message[-32:]

        # Verify auth
        h = self.gen_hmac(iv, enc_mess)
        try:
            h.verify(hmac_bytes)
        except InvalidSignature as e:
            raise CorruptedMessageException() from e

        # Decrypt message if there was no error
        aes = Cipher(algorithms.AES(self.aes_key),
                     modes.CBC(iv), backend=default_backend())
        decryptor = aes.decryptor()
        message = decryptor.update(enc_mess) + decryptor.finalize()

        # This doesn't belong here: crypter doesn't necessarily want to handle strings
        # long term we want to pass message length in message and simply cut the padding
        # And let messenger or interface decode
        # Kinda too lazy to do that right now, mby later
        message = message.decode('utf8')
        message = message.split('\0')[0]
        return message

    def encrypt_key(self, raw_key):
        "Encrypts the given key using the Crypter's RSA key."
        if self.rsa_key == None:
            raise NoKeyException("Cannot encrypt AES key: RSA key hasn't been loaded.")
        if self.key_type != utils.PUBLIC:
            raise CrypterException("Cannot encrypt key. Public RSA key required.")
        enc_key = self.rsa_key.encrypt(raw_key, DEFAULT_PADDING())
        return enc_key

    def decrypt_key(self, encrypted_key):
        "Decrypts the given key using the Crypter's RSA key."
        if self.rsa_key == None:
            raise NoKeyException("Cannot decrypt AES key: RSA key hasn't been loaded.")
        if self.key_type != utils.PRIVATE:
            raise CrypterException("Cannot decrypt key. Private RSA key required.")
        raw_key = self.rsa_key.decrypt(encrypted_key, DEFAULT_PADDING())
        return raw_key

    def sign(self, private_key, message):
        sign_padding = padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                                   salt_length=padding.PSS.MAX_LENGTH)

        signature = private_key.sign(message, sign_padding, hashes.SHA256())

        return signature

    def verify_signature(self, public_key, message, signature):
        sign_padding = padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                                   salt_length=padding.PSS.MAX_LENGTH)

        public_key.verify(signature, message, sign_padding, hashes.SHA256())
