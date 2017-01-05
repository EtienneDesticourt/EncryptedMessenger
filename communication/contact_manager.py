import os
import threading
from communication.contact import Contact
import config
import logging

class ContactManager(object):

    def __init__(self, peer_registry, conn_callback=None, mess_callback=None, contact_dir=config.CONTACT_DIR):
        self.contacts = []
        self.peer_registry = peer_registry
        self.contact_dir = contact_dir
        self.conn_callback = conn_callback
        self.mess_callback = mess_callback
        self.logger = logging.getLogger(__name__)

    def get_contact(self, name):
        for contact in self.contacts:
            if contact.name == name:
                return contact
        return None

    def get_contact_by_ip(self, ip):
        for contact in self.contacts:
            # We have to recheck each contact's ip because contacts
            # update their ip in the registry when they connect
            contact_ip = self.peer_registry.get_peer_ip(contact.name)
            if contact_ip == ip:
                return contact
        return None

    def contact_connected(self, socket, ip):
        contact = self.get_contact_by_ip(ip)
        if contact:
            contact.has_connected(socket)

    def load_contact(self, owner_name, contact_name, contact_file):
        self.logger.info("Loading contact %s from %s for user %s", contact_name, contact_file, owner_name)

        path = os.path.join(self.contact_dir, contact_file)
        with open(path, "rb") as f:
            public_key = f.read()

        contact = Contact(owner_name, contact_name, public_key)
        if self.conn_callback:
            contact.connection_callback = self.conn_callback
        if self.mess_callback:
            contact.new_messages_callback = self.mess_callback

        self.contacts.append(contact)
        return contact

    # TODO: associate contact list to username, save contacts order
    def load_contacts(self, username):
        for contact_file in os.listdir(self.contact_dir):
            contact_name = contact_file[:-4]
            contact = self.load_contact(username, contact_name, contact_file)

    def connect_to_contact(self, contact):
        if not contact.connected:
            contact.ip = self.peer_registry.get_peer_ip(contact.name)
            if contact.ip:
                contact.connect()
            else:
                self.logger.info("No ip for contact %s.", contact.name)

    def connect_to_contacts(self):
        for contact in self.contacts:
            threading.Thread(target=self.connect_to_contact, args=[contact]).start()

    def add_contact(self, owner, peer):
        contact = Contact.from_json(owner, peer)
        for other_contact in self.contacts:
            if contact.name == other_contact.name:
                return
        contact.save(self.contact_dir)
        self.contacts.append(contact)
        threading.Thread(target=self.connect_to_contact, args=[contact]).start()

    def check_status(self, contact):
        pass
