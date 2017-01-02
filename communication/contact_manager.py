import os
from communication.contact import Contact
import config


class ContactManager(object):

    def __init__(self, contact_dir=config.CONTACT_DIR):
        self.contacts = []
        self.contact_dir = contact_dir

    def load_contact(self, owner_name, contact_name):
        path = os.path.join(self.contact_dir, username)
        with open(path, "r") as f:
            public_key = f.read()
        contact = Contact(owner_name, contact_name, public_key)
        self.contacts.append(contact)
        return contact

    # TODO: associate contact list to username, save contacts order
    def load_contacts(self, username):
        for contact_file in os.listdir(self.contact_dir):
            contact_name = contact_file[:-4]
            contact = self.load_contact(username, contact_name)

    def connect_to_contact(self, contact):
        if not contact.connected:
            threading.Thread(target=contact.connect_and_receive).start()

    def connect_to_contacts(self):
        for contact in self.contacts:
            self.connect_to_contact(contact)

    def add_contact(self, peer):
        contact = Contact.from_json(peer)
        for other_contact in self.contacts:
            if contact.name == other_contact.name:
                return
        contact.save(self.contact_dir)
        self.contacts.append(contact)

    def check_status(self, contact):
        pass
