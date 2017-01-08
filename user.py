import logging
import keys.utils
import config

class User(object):
    "The user of the desktop application."

    def __init__(self, username, peer_registry, contact_manager, key_utils=keys.utils):
        self.username = username
        self.peer_registry = peer_registry
        self.key_utils = key_utils
        self.contact_manager = contact_manager
        self.active_contact = None
        self.logger = logging.getLogger(__name__)
        self.logger.info("Created new user instance with name %s.", username)

    def register(self):
        "Registers the user to the peer registry and saves his credentials."
        private_key = self.key_utils.generate_new_key()
        public_pem_data = self.key_utils.get_public_pem(private_key)

        self.peer_registry.register(self.username, public_pem_data)
        self.save(private_key)

    def connect(self):
        "Connects to the peer registry with existing credentials."
        self.peer_registry.connect(self.username)
        self.contact_manager.load_contacts(self.username)
        self.contact_manager.connect_to_contacts()

    def save(self, private_key):
        "Saves the user's username and private key."
        self.key_utils.save_keys(private_key, self.username, config.KEY_DIR)
        with open(config.USER_FILE, "w") as f:
            f.write(self.username)

    def add_contact(self, name):
        "Adds a friend to the user's contact list."
        info = self.peer_registry.get_peer_info(name)
        self.contact_manager.add_contact(self.username, info)

    def say(self, message):
        "Sends a message to the currently active contact."
        if self.active_contact and self.active_contact.connected:
            self.active_contact.tell(message)

    def set_active_contact(self, name):
        self.active_contact = self.contact_manager.get_contact(name)

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        self._username = value
