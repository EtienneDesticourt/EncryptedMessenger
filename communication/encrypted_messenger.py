import os
import time
import threading
import logging
from communication import messenger
from communication import protocol
from communication.exceptions import HandshakeFailure
from communication.exceptions import HandshakeTimeout
from encryption import crypter
import keys.utils


class EncryptedMessenger(messenger.Messenger):
    "Messenger object with cryptographic capabilities."

    def __init__(self, role, socket):
        super().__init__(socket)
        self.crypter = crypter.Crypter(os.urandom)
        self.role = role
        self.ready = False
        self.logger = logging.getLogger(__name__)

    def run(self, private_key, contact_public_key):
        args = [private_key, contact_public_key]
        threading.Thread(target=self.perform_handshake, args=args).start()
        super().run()

    def send(self, message):
        encrypted = self.crypter.encrypt_message(message)
        super().send(encrypted)

    def consume_message(self):
        message = super().consume_message()
        return self.crypter.decrypt_message(message)

    def consume_messages(self):
        messages = super().consume_messages()
        return [self.crypter.decrypt_message(mess) for mess in messages]

    def wait_for_next_message(self):
        message = None
        timeout_counter = 0
        while not message:
            message = super().consume_message()
            self.raise_last_error_if_any()
            time.sleep(1)
            timeout_counter += 1
            if timeout_counter > 45:
                self.logger.critical("Messenger timed out while waiting for next message.")
                raise HandshakeTimeout()

        return message

    def perform_handshake(self, private_key, contact_key):
        self.logger.info("Performing handshake as %s.", self.role)
        if self.role == protocol.SERVER_ROLE:
            self.perform_handshake_as_server(private_key, contact_key)
        elif self.role == protocol.CLIENT_ROLE:
            self.perform_handshake_as_client(private_key, contact_key)
        else:
            raise ValueError("Wrong role.")  # huehue
        self.logger.info("Handshake finished.")

    def perform_handshake_as_server(self, private_key, contact_key):
        # Send ephemeral RSA key and sign it with long-term RSA key
        self.crypter.gen_and_set_rsa_key()
        public_rsa_key = self.crypter.get_public_key_pem()
        signature = self.crypter.sign(private_key, public_rsa_key)
        self.logger.debug("Sending ephemeral RSA key.")
        super().send(public_rsa_key)
        self.logger.debug("Sending signature.")
        super().send(signature)


        # Receive encrypted AES key and verify its author
        self.logger.debug("Waiting for AES key.")
        encrypted_aes_key = self.wait_for_next_message()
        self.logger.debug("Waiting for signature.")
        signature = self.wait_for_next_message()
        self.crypter.verify_signature(contact_key, encrypted_aes_key, signature)
        self.crypter.aes_key = self.crypter.decrypt_key(encrypted_aes_key)
        self.ready = True

    def perform_handshake_as_client(self, private_key, contact_key):
        # Receive ephemeral RSA key and verify its author
        self.logger.debug("Waiting for public pem.")
        public_key_pem = self.wait_for_next_message()
        self.logger.debug("Waiting for signature.")
        signature = self.wait_for_next_message()
        self.crypter.verify_signature(contact_key, public_key_pem, signature)
        self.crypter.set_public_key_from_pem(public_key_pem)

        # Send AES key and sign it with long-term RSA key
        self.crypter.gen_and_set_aes_key()
        encrypted_key = self.crypter.encrypt_key(self.crypter.aes_key)
        signature = self.crypter.sign(private_key, encrypted_key)
        self.logger.debug("Sending AES key.")
        super().send(encrypted_key)
        self.logger.debug("Sending signature.")
        super().send(signature)
        self.ready = True
