import os
import logging
from communication.client import Client
from communication.exceptions import ClientException
from communication import protocol
from communication.encrypted_messenger import EncryptedMessenger
from communication.messenger import Messenger
from communication.socket_manager import SocketManager
from keys.utils import load_private_key
from keys.utils import load_public_key
import config


class Contact(object):
    """One of the user's contacts.

    Args:
        owner_name: The name of the user.
        contact_name: The name of the contact.
        public_key: The public key to be used for the handshake with said contact.
        ip: The ip to use to connect to the contact.
    """

    def __init__(self, owner_name, contact_name, public_key,
                 ip=None,
                 host=4664, # TODO: FIX HARDCODED, LOAD FROM SETTINGS
                 connection_callback=lambda contact, connected: None):
        self.owner = owner_name
        self.name = contact_name
        self.public_key = public_key
        self.ip = ip
        self.messenger = None
        self._connected = False
        self.connection_callback = connection_callback
        self.message_history = []
        self.logger = logging.getLogger(__name__)

    @property
    def connected(self):
        return self._connected

    @connected.setter
    def connected(self, value):
        self.connection_callback(self, value)
        self._connected = value

    def tell(self, message):
        """Sends a message to the contact.

        Args:
            message: The message to send.
        """
        message_bytes = message.encode("utf8") + b"\x00" # TODO: move to messenger
        self.messenger.send(message_bytes)

    def get_pending_messages(self):
        """Checks if there are any pending messages.

        Returns:
            All pending messages or an empty list if there aren't any.
        """
        if self.connected and self.messenger.ready:
            new_messages = self.messenger.consume_messages()
            self.message_history += new_messages
            return new_messages
        return []

    # TODO: Rename or make property
    def num_pending_messages(self):
        """Checks how many pending messages there are.

        Returns:
            The number of pending messages.
        """
        if self.connected:
            return len(self.messenger.num_pending_messages())
        return 0

    # TODO: Rename connect_as_client?
    def connect(self, message_received_callback=lambda c, m:None):
        """Attempts to connect to the contact's server and start a messaging session.

        Raises:
            ValueError: A value error is raised when the contact's ip is not defined.
        """
        self.logger.info("Connecting to contact %s with ip %s for user %s.", self.name, self.ip, self.owner)

        if self.ip == None:
            raise ValueError("Contact has no known ip.")

        with Client(self.ip, config.PORT) as client:
            try:
                client.connect()
            except ClientException:
                # TODO: This should be reraised and caught by the UI, no? But it's in a thread
                self.logger.info("Couldn't connect: contact is not online.")
            else:
                self.start_messenger(client.socket, protocol.CLIENT_ROLE, lambda m: message_received_callback(self, m))

    # TODO: Rename connect_as_server?
    def has_connected(self, socket, message_received_callback=lambda c, m:None):
        """Should be called if the contact has connected to our server.

        Args:
            socket: The socket handle.
        """
        self.logger.info("Contact %s has connected with ip %s.", self.name, self.ip)
        with SocketManager(socket) as socket_manager:
            self.start_messenger(socket, protocol.SERVER_ROLE, lambda m: message_received_callback(self, m))

    # TODO: Figure out if it belongs here. Seems weird that we have
    # repeating owner attr. Should be central manager, no?
    # Single keys loading/caching procedure for every messaging session?
    # At least for the identity keys
    def start_messenger(self, socket, role, message_received_callback):
        """Starts a messaging session with the contact.

        Args:
            socket: A handle to the socket which we'll be used to pass messages.
            role: Whether the user is a server (the contact has connected to him), or a client.
        """
        self.logger.info("Starting messenger for contact %s.", self.name)
        # self.messenger = EncryptedMessenger(role=role,
        #                                     socket=socket)
        self.messenger = Messenger(socket=socket)
        self.connected = True
        # private_key = load_private_key(self.owner, config.KEY_DIR)
        # public_key = load_public_key(self.public_key)
        self.messenger.set_message_callback(message_received_callback)
        # self.messenger.run(private_key, public_key)
        self.messenger.run()
        self.connected = False

    def stop_messenger(self):
        """Stops the ongoing messaging session if there is one."""
        if self.connected:
            self.messenger.stop()
            self.connected = False

    @staticmethod
    def from_json(owner, contact_data,
                  connection_callback=lambda contact, connected: None):
        """Creates a contact from JSON data.

        Args:
            owner: The user's name.
            contact_data: A JSON object containing the necessary parameters to define a contact.

        Returns:
            A contact instance with the specified parameters.
        """
        name = contact_data["username"]
        key = contact_data["public_key"].encode("utf8")
        ip = contact_data["ip"]
        return Contact(owner, name, key, ip, connection_callback)

    def save(self, save_dir):
        """Saves the contact as JSON data.

        Args:
            save_dir: The directory in which to save the contact.
        """
        path = os.path.join(save_dir, self.name + ".pem")
        with open(path, "wb") as f:
            f.write(self.public_key)
