import os
import logging
from communication.client import Client
from communication.exceptions import ClientException
from communication import protocol
from communication.encrypted_messenger import EncryptedMessenger
from communication.socket_manager import SocketManager
from keys.utils import load_private_key
from keys.utils import load_public_key
import config


class Contact(object):

    def __init__(self, owner_name, contact_name, public_key, ip=None):
        self.owner = owner_name
        self.name = contact_name
        self.public_key = public_key
        self.ip = ip
        self.messenger = None
        self.connected = False
        self.message_history = []
        self.logger = logging.getLogger(__name__)

    def tell(self, message):
        message_bytes = message.encode("utf8") + b"\x00" # TODO: move to messenger
        self.messenger.send(message_bytes)

    def get_pending_messages(self):
        if self.connected and self.messenger.ready:
            new_messages = self.messenger.consume_messages()
            self.message_history += new_messages
            return new_messages
        return []

    def num_pending_messages(self):
        if self.connected:
            return len(self.messenger.num_pending_messages())
        return 0

    def connect(self):
        self.logger.info("Connecting to contact %s with ip %s for user %s.", self.name, self.ip, self.owner)

        if self.ip == None:
            raise ValueError("Contact has no known ip.")

        with Client(self.ip, config.PORT) as client:
            try:
                client.connect()
            except ClientException:
                self.logger.info("Couldn't connect: contact is not online.")
            else:
                self.start_messenger(client.socket, protocol.CLIENT_ROLE)

    def has_connected(self, socket):
        self.logger.info("Contact %s has connected with ip %s.", self.name, self.ip)
        with SocketManager(socket) as socket_manager:
            self.start_messenger(socket, protocol.SERVER_ROLE)

    def start_messenger(self, socket, role):
        self.logger.info("Starting messenger for contact %s.", self.name)
        self.messenger = EncryptedMessenger(role=role,
                                            socket=socket)
        self.connected = True
        private_key = load_private_key(self.owner, config.KEY_DIR)
        public_key = load_public_key(self.public_key)
        self.messenger.run(private_key, public_key)
        self.connected = False

    def stop_messenger(self):
        if self.connected:
            self.messenger.stop()
            self.connected = False

    def from_json(owner, contact_data):
        name = contact_data["username"]
        key = contact_data["public_key"].encode("utf8")
        ip = contact_data["ip"]
        return Contact(owner, name, key, ip)

    def save(self, save_dir):
        path = os.path.join(save_dir, self.name + ".pem")
        with open(path, "wb") as f:
            f.write(self.public_key)
