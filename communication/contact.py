import os
import logging
from communication.client import Client
from communication.client_exception import ClientException
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
        self.logger = logging.getLogger(__name__)

    @property
    def connected(self):
        return self._connected

    @connected.setter
    def connected(self, value):
        self._connected = value
        self.connection_callback()

    def connection_callback(self):
        pass

    def new_messages_callback(self):
        pass

    def tell(self, message):
        message_bytes = message.encode("utf8") + b"\x00" # TODO: move to messenger
        self.messenger.send(message_bytes)

    def connect(self):
        self.logger.info("Connecting to contact %s for user %s.", self.name, self.owner)

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
        with SocketManager(socket) as socket_manager:
            self.start_messenger(socket, protocol.SERVER_ROLE)

    def start_messenger(self, socket, role):
        self.logger.info("Starting messenger for contact %s.", self.name)
        self.messenger = EncryptedMessenger(role=role,
                                            socket=socket)
        self.messenger.set_message_callback(self.new_messages_callback)
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
