
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, hmac
import unittest, socket, threading, time, math, os
import crypter, crypter_exceptions
import protocol
import keys.utils as utils

#AES KEY
TEST_AES_KEY = b'|\x894\xb1\xe5)yE\x9d3{\xcc\xc9E\xb5\xc5IeT\x99\xa2,f~\x98\xe3\x9d\x05\\X\x92\xdf'
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
            assert False, "Unexpected exception in loadRsaKey."
        assert self.testCrypter.rsaKey != None

        self.testCrypter.rsaKey = None
        try:
            self.testCrypter.loadRsaKey(utils.PUBLIC, DUMMY_KEYS_DIR)
        except:
            assert False, "Unexpected exception in loadRsaKey."
        assert self.testCrypter.rsaKey != None

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


if __name__ == "__main__":
    unittest.main()
