import os
import time
from communication import messenger, protocol
from encryption import crypter
import keys.utils


class EncryptedMessenger(messenger.Messenger):
    "Messenger object with cryptographic capabilities"

    def __init__(self, verbose=False):
        super().__init__()
        self.crypter = crypter.Crypter(os.urandom)
        self.verbose = verbose

    def print_if_verbose(self, *args):
        if self.verbose:
            print(*args)

    def wait_for_next_message(self):
        message = None
        while not message:
            message = super().consume_message()
            self.raise_last_error_if_any()
            time.sleep(1)
        return message

    def perform_handshake_as_server(self):
        # TODO: Uncomment and add auth
        # self.crypter.loadRsaKey(keys.utils.PRIVATE)

        self.print_if_verbose("Generating new RSA key and sending to client.")
        self.crypter.gen_and_set_rsa_key()
        public_rsa_key = self.crypter.get_public_key_pem()
        super().send(public_rsa_key)

        self.print_if_verbose("Waiting for AES key from client.")
        encrypted_aes_key = self.wait_for_next_message()

        self.crypter.aes_key = self.crypter.decrypt_key(encrypted_aes_key)

    def perform_handshake_as_client(self):
        # TODO: Uncomment and add auth
        # self.crypter.loadRsaKey(keys.utils.PUBLIC)

        self.print_if_verbose("Waiting for ephemeral RSA key from server.")
        public_key_pem = self.wait_for_next_message()
        self.crypter.set_public_key_from_pem(public_key_pem)

        self.print_if_verbose("Generating new AES key and sending to server.")
        self.crypter.gen_and_set_aes_key()
        encrypted_key = self.crypter.encrypt_key(self.crypter.aes_key)
        super().send(encrypted_key)

    def send(self, message):
        encrypted = self.crypter.encrypt_message(message)
        super().send(encrypted)

    def consume_message(self):
        message = super().consume_message()
        return self.crypter.decryptMessage(message)

    def consume_messages(self):
        messages = super().consume_messages()
        return [self.crypter.decrypt_message(mess) for mess in messages]

    def start(self, host, port, role):
        self.print_if_verbose("Attempting to connect with remote as " + str(role) + " ...")

        super().start(host, port, role)

        self.print_if_verbose("Succesful connection.\n")
        self.print_if_verbose("Attempting handshake...")

        if role == protocol.SERVER_ROLE:
            self.perform_handshake_as_server()
        elif role == protocol.CLIENT_ROLE:
            self.perform_handshake_as_client()
        else:
            raise ValueError("Wrong role.")  # huehue

        self.print_if_verbose("Succesful handshake.\n")
