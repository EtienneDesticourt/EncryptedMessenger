
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.asymmetric import padding
import unittest, socket, threading, time, math, os
from encryption import crypter, crypter_exceptions
from communication import protocol
import keys.utils as utils

#AES KEY
TEST_AES_KEY = b'|\x894\xb1\xe5)yE\x9d3{\xcc\xc9E\xb5\xc5IeT\x99\xa2,f~\x98\xe3\x9d\x05\\X\x92\xdf'
TEST_ENC_AES_KEY = b'\tO\xd4r\x9c\xea\x9fZ\xb5T\x89\x9f\xa2\x7f0\x1cu\x0b\x888\xb1\xbaT\x18Pe\xaf\xc8@\x0e\x99\xb7q\xfb\r?O\x9c#G4o, \xf2\xbd\x89(\x8e\xbbE\x1cS$\xd4\xee5R\xe5M{\xd6\x8e\xeei\xa5\x92\x01ke\xe2\xa8W/G\x91\xd1\xa9\xc8\x04\xb2m]\x01\xbf\xbe\xb7\x8b\xa7\xdf\x82\xe8\x03Q\xf2\x9d\xe5\xb0\xb5\x99kO\x02R\x16S\xf4)$^P\xb3\x15\x0cX\x0fd\xd9WFH\xc1 \xeb `K\xc9\xee\xfc0&\xf24\x14\xde\x85\xccP\xd7\xcb\xac:\xe2B\x98}\x91\x1cX\x9c\xffx\x05\x8a2\x93  \x00I\xdf\x9a\xe8\xf9\xaa\xd4-&\x12\x962V\xb9^\xf2\x01\xe0\x9d~+\xbf\x1c\x94\xf1\x06\xf0\x84B\xbc\xfb\x88\xdam\xae\x1f&\x00\x9eP\xbd\x81\xcb\xb8\xd0\xe1\xf8\x179\xe9\xc3\xe6\xe1\xf9\xce\xde\xd7\r\xd4o->\xdb\xf2~\xce\xb8\xa4hz^\xc9\xbb<\xa7\xd4aOZu2W\xd7\x0b\x1d\x93gd\xff\x9cR~\x10\x12\x95\x88'
#RSA KEYS
DUMMY_KEYS_DIR = os.path.join("tests", "dummy_keys")
#Test message
TEST_MESSAGE = b"Hello, world!\x00"
#Encrypted padded test message
TEST_ENCRYPTED_MESSAGE = b'z\xd5%\x94\x0b\x1e,\x05\x0bS\x8e\xd8\x90\xfb\x9b\xa0\xa1I\x95k(\xf7\xb9\x88yka\x93\x08p\x12&\xbe{\xb2bg\x9f<\xccmr\xf1\t\xb3q\xeb\xa3\x99\xbb%}\xc3\x04\xa5\xf4\xf7\x01\x07\xbc\x95>\xa1\xbc'
TEST_IV = TEST_ENCRYPTED_MESSAGE[:16]
TEST_HMAC = TEST_ENCRYPTED_MESSAGE[-32:]
#Modified encrypted padded test message
TEST_ENCRYPTED_MESSAGE_MOD = b'z\xd5%\x94\x0b\x1e,\x05\x0bS\x8e\xd8\x90\xfb\x9b\xa0\xa1I\x95k(\xf7\xb9\x88yka\x94\x09p\x12&\xbe{\xb2bg\x9f<\xccmr\xf1\t\xb3q\xeb\xa3\x99\xbb%}\xc3\x04\xa5\xf4\xf7\x01\x07\xbc\x95>\xa1\xbc'



class TestCrypter(unittest.TestCase):

    def mockRNG(self, numBytes):
        if numBytes == 16: #Asking for an IV
            return TEST_IV
        elif numBytes == 32: #Asking for AES key
            return TEST_AES_KEY
        else:
            raise ValueError("Test parameters have changed.")

    def setUp(self):
        self.testCrypter = crypter.Crypter(self.mockRNG)

    def test_loadRsaKey_success(self):
        try:
            self.testCrypter.loadRsaKey(utils.PRIVATE, DUMMY_KEYS_DIR)
        except:
            assert False, "Unexpected exception in loadRsaKey while loading private key."
        assert self.testCrypter.rsaKey != None, "Private key failed to be loaded."

        self.testCrypter.rsaKey = None
        try:
            self.testCrypter.loadRsaKey(utils.PUBLIC, DUMMY_KEYS_DIR)
        except:
            assert False, "Unexpected exception in loadRsaKey while loading public key."
        assert self.testCrypter.rsaKey != None, "Public key failed to be loaded."

    def test_loadRsaKey_no_file(self):
        self.assertRaises(crypter_exceptions.CrypterException, self.testCrypter.loadRsaKey, utils.PUBLIC, "wrong_dir")
        assert self.testCrypter.rsaKey == None

    def test_loadRsaKey_unknown_type(self):
        self.assertRaises(crypter_exceptions.CrypterException, self.testCrypter.loadRsaKey, "WRONG KEY TYPE", DUMMY_KEYS_DIR)
        assert self.testCrypter.rsaKey == None

    def test_genAndSetAesKey(self):
        assert self.testCrypter.aesKey == None
        newKey = self.testCrypter.genAndSetAesKey()
        assert self.testCrypter.aesKey != None
        assert newKey == self.testCrypter.aesKey

    def test_encryptMessage_success(self):
        self.testCrypter.genAndSetAesKey()
        encryptedMessage = self.testCrypter.encryptMessage(TEST_MESSAGE)
        assert encryptedMessage == TEST_ENCRYPTED_MESSAGE

    def test_encryptMessage_no_key(self):
        self.assertRaises(crypter_exceptions.NoKeyException, self.testCrypter.encryptMessage, TEST_MESSAGE)

    def test_decryptMessage_success(self):
        self.testCrypter.genAndSetAesKey()
        decrypted = self.testCrypter.decryptMessage(TEST_ENCRYPTED_MESSAGE)
        assert decrypted == TEST_MESSAGE.decode('utf8')[:-1] #test message to string without termination char

    def test_decryptMessage_no_key(self):
        self.assertRaises(crypter_exceptions.NoKeyException, self.testCrypter.encryptMessage, TEST_MESSAGE)

    def test_decryptMessage_auth_comprommised(self):
        self.testCrypter.genAndSetAesKey()
        self.assertRaises(crypter_exceptions.CorruptedMessageException, self.testCrypter.decryptMessage, TEST_ENCRYPTED_MESSAGE_MOD)

    def test_encryptKey_success(self):
        self.testCrypter.loadRsaKey(utils.PUBLIC, DUMMY_KEYS_DIR)
        encKey = self.testCrypter.encryptKey(TEST_AES_KEY)

        privateKey = utils.loadKey(utils.PRIVATE, DUMMY_KEYS_DIR)
        assert TEST_AES_KEY == privateKey.decrypt(encKey, crypter.DEFAULT_PADDING())

    def test_encryptKey_wrong_key(self):
        self.testCrypter.loadRsaKey(utils.PRIVATE, DUMMY_KEYS_DIR)
        self.assertRaises(crypter_exceptions.CrypterException, self.testCrypter.encryptKey, TEST_AES_KEY)

    def test_encryptKey_no_key(self):
        self.assertRaises(crypter_exceptions.NoKeyException, self.testCrypter.encryptKey, TEST_AES_KEY)

    def test_decryptKey_success(self):
        self.testCrypter.loadRsaKey(utils.PRIVATE, DUMMY_KEYS_DIR)
        decKey = self.testCrypter.decryptKey(TEST_ENC_AES_KEY)
        assert decKey == TEST_AES_KEY

    def test_decryptKey_wrong_key(self):
        self.testCrypter.loadRsaKey(utils.PUBLIC, DUMMY_KEYS_DIR)
        self.assertRaises(crypter_exceptions.CrypterException, self.testCrypter.decryptKey, TEST_ENC_AES_KEY)

    def test_decryptKey_no_key(self):
        self.assertRaises(crypter_exceptions.NoKeyException, self.testCrypter.decryptKey, TEST_ENC_AES_KEY)


if __name__ == "__main__":
    unittest.main()
