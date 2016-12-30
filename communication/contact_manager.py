
CONTACT_DIR = "contacts"

class ContactManager(object):
    def __init__(self, network, contact_dir=CONTACT_DIR):
        self.contacts = []
        self.network = network
        self.contact_dir = contact_dir

    def load_contact(self, username):
        path = os.path.join(self.contact_dir, username)
        with open(path, "r") as f:
            public_key = f.read()
        contact = Contact(username, public_key)
        self.contacts.append(contact)

    def load_contacts(self):
        for contact_name in os.listdir(self.contact_dir):
            self.load_contact(contact_name)

    def add_contact(self, username):
        contact_data = self.network.fetch_peer(username)
        key = contact_data["public_key"]
        ip = self.network.fetch_peer_ip(username)
        contact = Contact(username, key, ip)
        contact.save(self.contact_dir)
        self.contacts.append(contact)

    def check_status(self, contact):
        pass
