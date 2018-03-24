import os
import threading
from communication.contact import Contact
import config
import logging

class ContactManager(object):
    """Manages multiple contacts for a user.

    Args:
        peer_registry: An object that allows the manager to fetch peers' ips by name.
        contact_dir: A directory in which contacts are/can be stored.
    """

    def __init__(self, peer_registry,
                 connection_callback=lambda contact, connected: None,
                 message_callback=lambda contact, message: None,
                 contact_dir=config.CONTACT_DIR):
        self.contacts = []
        self.peer_registry = peer_registry
        self.contact_dir = contact_dir
        self.connection_callback = connection_callback
        self.message_callback = message_callback
        self.logger = logging.getLogger(__name__)

    def get_contact(self, name):
        """Fetches a contact by name.

        Args:
            name: The name of the contact.

        Returns:
            The wanted contact or None if none match the given name.
        """
        for contact in self.contacts:
            if contact.name == name:
                return contact
        return None

    def update_contacts_ip(self):
        """Fetches the ip of all contacts from the peer registry."""
        self.logger.info("Updating contact ips.")
        for contact in self.contacts:
            contact.ip = self.peer_registry.get_peer_ip(contact.name)

    def get_contact_by_ip(self, ip):
        """Fetches a contact by ip.

        Args:
            ip: The contact's ip.

        Returns:
            The wanted contact or None if none match the given ip.
        """
        for contact in self.contacts:
            if contact.ip == ip:
                return contact
        return None

    # TODO: Shouldn't store callbacks here maybe? Transparent connect_as_server wrapper that doesn't impose
    # that particular use as callback
    # Rename connect_contact_as_server?
    def contact_connected(self, socket, ip):
        """Starts a messaging session with the contact that has just connected from the given IP 
        if it exists.

        Args:
            socket: The socket handle to the contact that connected.
            ip: The ip of the contact that's trying to connect.
        """
        self.logger.info("Incoming connection from ip %s on socket %s.", ip, str(socket))
        # We have to recheck each contact's ip because contacts
        # update their ip in the registry when they connect
        self.update_contacts_ip()
        contact = self.get_contact_by_ip(ip)
        if contact:
            contact.has_connected(socket, self.message_callback)
        else:
            self.logger.info("Found no matching contact for ip %s.", ip)

    def load_contact(self, owner_name, contact_name, contact_file):
        """Loads a contact into the manager from a file.

        Args:
            owner_name: The name of the user whose contact we're loading.
            contact_name: The contact's name.
            contact_file: The file where the contact data is stored.

        Returns:
            The loaded contact.

        Raises:
            FileNotFoundError: The error will be raised if the contact file does not exist in the contact directory.
        """
        self.logger.info("Loading contact %s from %s for user %s", contact_name, contact_file, owner_name)

        path = os.path.join(self.contact_dir, contact_file)
        with open(path, "rb") as f:
            public_key = f.read()

        contact = Contact(owner_name, contact_name, public_key, self.connection_callback)

        self.contacts.append(contact)
        return contact

    # TODO: associate contact list to username, save contacts order
    def load_contacts(self, username):
        """Loads all contacts for a given user.

        Args:
            username: The name of the user whose contacts will be loaded.
        """
        for contact_file in os.listdir(self.contact_dir):
            contact_name = contact_file[:-4]
            contact = self.load_contact(username, contact_name, contact_file)

    def connect_to_contact(self, contact):
        """Starts a messaging session with the given contact.

        Args:
            contact: A contact to which to connect.
        """
        if not contact.connected:
            contact.ip = self.peer_registry.get_peer_ip(contact.name)
            if contact.ip:
                contact.connect(self.message_callback)
            else:
                self.logger.info("No ip for contact %s.", contact.name)

    def connect_to_contacts(self):
        """Starts a messaging session with all loaded contacts."""
        for contact in self.contacts:
            threading.Thread(target=self.connect_to_contact, args=[contact]).start()

    def add_contact(self, owner, peer):
        """Adds a contact to the user's contact list.

        Args:
            owner: The username of the user to which we'll add the contact.
            peer: The contact data as a JSON string.
        """
        self.logger.info("Adding new contact %s for owner %s.", peer, owner)
        contact = Contact.from_json(owner, peer, self.connection_callback)
        for other_contact in self.contacts:
            if contact.name == other_contact.name:
                return # TODO: Raise ExistingContactError here?
        contact.save(self.contact_dir)
        self.contacts.append(contact)
        threading.Thread(target=self.connect_to_contact, args=[contact]).start()

    def check_status(self, contact):
        pass
