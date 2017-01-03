import os
from communication.client import Client
from communication import protocol
from communication.encrypted_messenger import EncryptedMessenger
from communication.socket_manager import SocketManager
from keys.utils import load_private_key
import config


class Contact(object):

    def __init__(self, owner_name, contact_name, public_key, ip=None):
        self.owner = owner_name
        self.name = contact_name
        self.public_key = public_key
        self.ip = ip
        self.messenger = None
        self.connected = False

    def connect(self):
        if self.ip == None:
            raise ValueError("Contact has no known ip.")

        with Client(self.ip, config.PORT) as client:
            client.connect()
            self.start_messenger(client.socket, protocol.CLIENT)

    def has_connected(self, socket):
        with SocketManager(socket) as socket_manager:
            self.start_messenger(socket, protocol.SERVER)

    def start_messenger(self, socket, role):
        self.messenger = EncryptedMessenger(role=role,
                                            socket=socket)
        self.connected = True
        private_key = load_private_key(self.owner, config.KEY_DIR)
        self.messenger.run(private_key, self.public_key)

    def stop_messenger(self):
        if self.connected:
            self.messenger.stop()
            self.connected = False

    def from_json(contact_data):
        name = contact_data["username"]
        key = contact_data["public_key"]
        ip = contact_data["ip"]
        return Contact(name, key, ip)

    def save(self, save_dir):
        path = os.path.join(save_dir, self.name + ".pem")
        with open(path, "w") as f:
            f.write(self.public_key)
