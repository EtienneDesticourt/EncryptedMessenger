import math

from cryptography.hazmat.primitives.serialization import load_pem_private_key, Encoding, PublicFormat, load_pem_public_key
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.exceptions import UnsupportedAlgorithm
import cryptography.exceptions

from communication import protocol
from encryption.exceptions import CrypterException, NoKeyException, CorruptedMessageException
import encryption.exceptions
from keys import utils
import config

DEFAULT_EXPONENT = 65537
DEFAULT_RSA_KEY_SIZE = 2048


def DEFAULT_PADDING():
    return padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None)

def OPENSSL_PADDING():
    return padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),
                        algorithm=hashes.SHA1(),
                        label=None)


class Crypter(object):
    """A utility that holds a user's secret keys, handles the authentication handshake, encryption and decryption of messages, 
    and garantees their integrity.

    Args:
        RNG: A random function that'll be used to generate keys. Must be cryptographically secure.
    """

    def __init__(self, RNG):
        self.rsa_key = None
        self.aes_key = None
        self.RNG = RNG

    def load_rsa_key(self, key_type, directory=config.KEY_DIR):
        """Loads an RSA key to perform handhsakes/authentication with.

        Args:
            key_type: keys.PUBLIC or keys.PRIVATE.
            directory: The directory in which the key is stored.

        Raises:
            CrypterException: If the specified key_type does not exist.
            NoKeyException: If there is no key file in the specified directory.
            BackendException: If the serialized key is of a type that is not supported by the backend 
                or if the key is encrypted with a symmetric cipher that is not supported by the backend.
        """
        try:
            self.rsa_key = utils.load_key(key_type, directory)
        except FileNotFoundError as e:
            raise NoKeyException() from e
        except ValueError as e:
            raise CrypterException("Wrong key type.") from e
        except UnsupportedAlgorithm as e:
            raise BackendException("Unable to load RSA key.") from e
        self.key_type = key_type

    def gen_and_set_rsa_key(self):
        """Generates and stores a new RSA key pair."""
        self.key_type = utils.PRIVATE
        self.rsa_key = rsa.generate_private_key(public_exponent=DEFAULT_EXPONENT,
                                                key_size=DEFAULT_RSA_KEY_SIZE,
                                                backend=default_backend())

    def set_public_key_from_pem(self, pem_data):
        """Sets a new public key from pem data.

        Args:
            The pem data bytes.
        """
        self.key_type = utils.PUBLIC
        self.rsa_key = load_pem_public_key(pem_data, backend=default_backend())

    def get_public_key_pem(self):
        """Gets pem data for the public rsa key.

        Returns:
            The pem data bytes.

        Raises:
            CrypterException: If the current key type does not exist.
        """
        if self.key_type == utils.PRIVATE:
            public_key = self.rsa_key.public_key()
        elif self.key_type == utils.PUBLIC:
            public_key = self.rsa_key
        else:
            raise CrypterException("Wrong key type.")
        return public_key.public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)

    def gen_and_set_aes_key(self):
        """Generates and stores a 32 bytes AES key to encrypt messages with.

        Returns:
            The generated 32 bytes AES key.
        """
        self.aes_key = self.RNG(32)
        return self.aes_key

    def gen_hmac(self, iv, encrypted_message):
        """Generates 32 bytes of HMAC from a given initialization vector and encrypted message 
        to ensure the message's integrity.

        Args:
            iv: The initialization vector to generate the HMAC.
            encrypted_message: The encrypted message to which the HMAC will be merged.

        Returns:
            The generated 32 bytes HMAC.
        """
        h = hmac.HMAC(self.aes_key, hashes.SHA256(), backend=default_backend())
        h.update(iv)
        h.update(encrypted_message)
        return h

    def encrypt_message(self, message):
        """Encrypts the given message using the current AES key.

        Args:
            message: The message to encrypt.

        Returns:
            An encrypted message along with its HMAC and its initialization vector.

        Raises:
            NoKeyException: If an AES key hasn't been generated yet.
        """
        if not self.aes_key:
            raise NoKeyException("Cannot encrypt message: AES key hasn't been set.")

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
        """Decrypts the given message using the current AES key.

        Args:
            message: The message to decrypt.

        Returns:
            The decrypted message as a string.

        Raises:
            CorruptedMessageException: The HMAC signature did not match the message or the message wasn't the right size.
        """
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
        """Encrypts a key.


        Args:
            raw_key: The secret key to encrypt.

        Returns:
            The encrypted key.

        Raises:
            NoKeyException: If the RSA key hasn't been loaded yet.
            CrypterException: If the loaded RSA key is private. It needs a public key to encrypt things.
        """
        if self.rsa_key == None:
            raise NoKeyException("Cannot encrypt AES key: RSA key hasn't been loaded.")
        if self.key_type != utils.PUBLIC: # TODO: Why just not get the public key from the private one?
            raise CrypterException("Cannot encrypt key. Public RSA key required.")
        enc_key = self.rsa_key.encrypt(raw_key, DEFAULT_PADDING())
        return enc_key

    def decrypt_key(self, encrypted_key):
        """Decrypts a key.


        Args:
            encrypted_key: The secret key to decrypt.

        Returns:
            The decrypted key.

        Raises:
            NoKeyException: If the RSA key hasn't been loaded yet.
            CrypterException: If the loaded RSA key is public. It needs a private key to decrypt things.
        """
        if self.rsa_key == None:
            raise NoKeyException("Cannot decrypt AES key: RSA key hasn't been loaded.")
        if self.key_type != utils.PRIVATE:
            raise CrypterException("Cannot decrypt key. Private RSA key required.")
        raw_key = self.rsa_key.decrypt(encrypted_key, DEFAULT_PADDING())
        return raw_key

    def sign(self, private_key, message):
        """Signs a message with the private RSA key to authenticate it.


        Args:
            private_key: The secret key with which to sign the message.
            message: The message to sign.

        Returns:
            The signature.
        """
        sign_padding = padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                                   salt_length=padding.PSS.MAX_LENGTH)

        signature = private_key.sign(message, sign_padding, hashes.SHA256())

        return signature

    def verify_signature(self, public_key, message, signature):
        """Verifies the author's identity for a given message.

        Args:
            public_key: The public key of the author.
            message: The message to authenticate.
            signature: The signature with which the author signed the message.




        Args:
            private_key: The secret key with which to sign the message.
            message: The message to sign.

        Raises:
            InvalidSignature: If the signature does not match the public key.
        """
        sign_padding = padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                                   salt_length=padding.PSS.MAX_LENGTH)

        try:
            public_key.verify(signature, message, sign_padding, hashes.SHA256())
        except cryptography.exceptions.InvalidSignature as e:
            raise encryption.exceptions.InvalidSignature() from e
