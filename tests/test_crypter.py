
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, hmac
import unittest, socket, threading, time, math, os
import crypter, crypter_exception
import protocol

#AES KEY
TEST_AES_KEY = b'|\x894\xb1\xe5)yE\x9d3{\xcc\xc9E\xb5\xc5IeT\x99\xa2,f~\x98\xe3\x9d\x05\\X\x92\xdf'
#Test message
TEST_MESSAGE = b"Hello, world!\x00"
#Encrypted padded test message
TEST_ENCRYPTED_MESSAGE = b'z\xd5%\x94\x0b\x1e,\x05\x0bS\x8e\xd8\x90\xfb\x9b\xa0\xa1I\x95k(\xf7\xb9\x88yka\x93\x08p\x12&\xbe{\xb2bg\x9f<\xccmr\xf1\t\xb3q\xeb\xa3\x99\xbb%}\xc3\x04\xa5\xf4\xf7\x01\x07\xbc\x95>\xa1\xbc'
#Modified encrypted padded test message
TEST_ENCRYPTED_MESSAGE_MOD = b'z\xd5%\x94\x0b\x1e,\x05\x0bS\x8e\xd8\x90\xfb\x9b\xa0\xa1I\x95k(\xf7\xb9\x88yka\x94\x09p\x12&\xbe{\xb2bg\x9f<\xccmr\xf1\t\xb3q\xeb\xa3\x99\xbb%}\xc3\x04\xa5\xf4\xf7\x01\x07\xbc\x95>\xa1\xbc'

class TestCrypter(unittest.TestCase):

    def setUp(self):
        self.clientCrypter = crypter.Crypter(protocol.CLIENT_ROLE)
        self.serverCrypter = crypter.Crypter(protocol.SERVER_ROLE)

    def test_encryptMessage_success(self):
        data = self.clientCrypter.encryptMessage(TEST_MESSAGE)

        paddedMessLength = math.ceil(len(TEST_MESSAGE) / 16) * 16
        assert len(data) == 16 + paddedMessLength + 32

        iv = data[:16]
        encMess = data[16:-32]
        cipher = Cipher(algorithms.AES(self.clientCrypter.aesKey), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted = decryptor.update(encMess) + decryptor.finalize()
        assert decrypted[:len(TEST_MESSAGE)] == TEST_MESSAGE

    def test_encryptMessage_no_key(self):
        self.assertRaises(crypter_exception.CrypterException, self.serverCrypter.encryptMessage, TEST_MESSAGE)

    def test_decryptMessage_success(self):
        self.clientCrypter.aesKey = TEST_AES_KEY
        decrypted = self.clientCrypter.decryptMessage(TEST_ENCRYPTED_MESSAGE)
        assert decrypted == TEST_MESSAGE.decode('utf8')[:-1] #test message to string without termination char

    def test_decryptMessage_auth_comprommised(self):
        self.clientCrypter.aesKey = TEST_AES_KEY
        self.assertRaises(crypter_exception.CrypterException, self.clientCrypter.decryptMessage, TEST_ENCRYPTED_MESSAGE_MOD)


if __name__ == "__main__":
    unittest.main()
