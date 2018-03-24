import os
import time
import threading
import logging
from communication import messenger
from communication import protocol
from communication.exceptions import HandshakeFailureException
from communication.exceptions import HandshakeTimeoutException
from encryption import crypter
import keys.utils


class EncryptedMessenger(messenger.Messenger):
    """Handles the transmission and encryption of messages over a connection.

    Args:
        role: Whether the messenger should work as a server or client.
        socket: A handle to the connection
    """

    def __init__(self, role, socket):
        super().__init__(socket)
        self.crypter = crypter.Crypter(os.urandom)
        self.role = role
        self.ready = False
        self.logger = logging.getLogger(__name__)

    def run(self, private_key, contact_public_key):
        """Start the messaging session.

        Args:
            private_key: The private key of the user.
            contact_public_key: The public of the contact with whom the user is connected.
        """
        args = [private_key, contact_public_key]
        threading.Thread(target=self.perform_handshake, args=args).start()
        super().run()

    def send(self, message):
        """Sends a message over the current connection.

        Args:
            message: A unicode string of the message.
        """
        encrypted = self.crypter.encrypt_message(message)
        super().send(encrypted)

    def set_message_callback(self, callback):
        """Overwrites the current message callback.

        Args:
            callback: The new function that'll be called when a message is received.
        """
        def decryptor_callback(message):
            decrypted = self.crypter.decrypt_message(message)
            return callback(decrypted)
        self.message_callback = decryptor_callback

    # def consume_message(self):
    #     """Fetches message from the connection.

    #     Returns:
    #         A decrypted message.
    #     """
    #     message = super().consume_message()
    #     return self.crypter.decrypt_message(message)

    # def consume_messages(self):
    #     """Fetches all pending messages.

    #     Returns:
    #         All decrypted messages.
    #     """
    #     messages = super().consume_messages()
    #     return [self.crypter.decrypt_message(mess) for mess in messages]

    def wait_for_next_message(self):
        """Tries continuously to fetch a message until it does.

        Returns:
            The latest pending message.

        Raises:
            HandshakeTimeoutException:  The wait will time-out if no handshake messages are received in a given period.
            OSError: The messenger will raise this error if there are issues with the connection 
                while attempting to receive data.
        """
        message = None
        timeout_counter = 0
        while not message:
            message = super().consume_message()
            self.raise_last_error_if_any()
            time.sleep(1)
            timeout_counter += 1
            if timeout_counter > 45: # TODO: Replace hardcoded timeout value: config or param
                # TODO: Rename function to 'wait for next handhsake message'? Clearly can't be used
                # for normal messages if it can't wait 45 seconds
                self.logger.critical("Messenger timed out while waiting for next message.")
                raise HandshakeTimeoutException()

        return message

    def perform_handshake(self, private_key, contact_key):
        """Performs a handshake with the contact to which we're connected.

        Args:
            private_key: The user's private key.
            contact_key: The contact's public key.

        Raises:
            ValueError: This error will be raised if the messenger's role does not exist.
        """
        self.logger.info("Performing handshake as %s.", self.role)
        if self.role == protocol.SERVER_ROLE:
            self.perform_handshake_as_server(private_key, contact_key)
        elif self.role == protocol.CLIENT_ROLE:
            self.perform_handshake_as_client(private_key, contact_key)
        else:
            raise ValueError("Wrong role.")  # huehue
        self.logger.info("Handshake finished.")

    def perform_handshake_as_server(self, private_key, contact_key):
        """Takes the initiative in exchanging keys with the contact to 
        start the messaging session.

        Args:
            private_key: The user's private key.
            contact_key: The contact's public key.

        Raises:
            HandshakeTimeoutException:  The wait will time-out if no handshake messages are received in a given period. 
            OSError: The messenger will raise this error if there are issues with the connection 
                while attempting to receive data.
            # TODO: Document crypter errors after I've documented crypter.
        """
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
        """Waits for the contact to start exchanging keys to validate their 
        authenticity then sends the user's.

        Args:
            private_key: The user's private key.
            contact_key: The contact's public key.

        Raises:
            HandshakeTimeoutException:  The wait will time-out if no handshake messages are received in a given period. 
            OSError: The messenger will raise this error if there are issues with the connection 
                while attempting to receive data.
            # TODO: Document crypter errors after I've documented crypter.
        """
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
