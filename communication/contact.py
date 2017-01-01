import os
from communication.client import Client
from communication import protocol
from communication.encrypted_messenger import EncryptedMessenger

class Contact(object):
    def __init__(self, name, public_key, ip=None):
        self.name = name
        self.public_key = public_key
        self.ip = ip

    def from_json(contact_data):
        name = contact_data["username"]
        key = contact_data["public_key"]
        ip = contact_data["ip"]
        return Contact(name, key, ip)

    def save(self, save_dir):
        path = os.path.join(save_dir, self.name + ".pem")
        with open(path, "w") as f:
            f.write(self.public_key)

