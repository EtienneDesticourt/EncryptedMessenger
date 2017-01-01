import os
from communication.contact import Contact

CONTACT_DIR = "contacts"

class ContactManager(object):
    def __init__(self, contact_dir=CONTACT_DIR):
        self.contacts = []
        self.contact_dir = contact_dir

    def load_contact(self, username):
        path = os.path.join(self.contact_dir, username)
        with open(path, "r") as f:
            public_key = f.read()
        contact = Contact(username[:-4], public_key)
        self.contacts.append(contact)

    def load_contacts(self): #TODO: associate contact list to username, save contacts order
        for contact_name in os.listdir(self.contact_dir):
            self.load_contact(contact_name)

    def add_contact(self, peer):
        contact = Contact.from_json(peer)
        for other_contact in self.contacts:
            if contact.name == other_contact.name:
                return
        contact.save(self.contact_dir)
        self.contacts.append(contact)

    def check_status(self, contact):
        pass
