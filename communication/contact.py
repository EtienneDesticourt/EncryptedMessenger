import os
from communication.client import Client
from communication import protocol
from communication.encrypted_messenger import EncryptedMessenger
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

    def connect_and_receive(self):
        if self.ip == None:
            return
        private_key = load_private_key(self.owner, config.KEY_DIR)
        with Client(self.ip, config.PORT) as client:
            self.messenger = EncryptedMessenger(role=protocol.CLIENT,
                                                socket=client.socket)
            self.connected = True
            self.messenger.run(private_key, self.public_key)

    def receive_from(self, socket):
        private_key = load_private_key(self.owner, config.KEY_DIR)
        self.messenger = EncryptedMessenger(role=protocol.SERVER,
                                            socket=client.socket)
        self.connected = True
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
