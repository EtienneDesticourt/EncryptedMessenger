from crypter import DEFAULT_PADDING
import requests
import keys.utils

KEY_DIR = "keys"


class Network(object):

    def __init__(self, url, key_dir=KEY_DIR):
        self.url = url
        self.key_dir = key_dir

    def register(self, username):
        private_path, public_path = keys.utils.new_key(username, self.key_dir)
        with open(public_path, "r") as f:
            public_key = f.read()

        result = requests.post(
            self.url + "/user", data={"username": username, "public_key": public_key})
        return result

    def connect(self, username):
        # Ask for an auth challenge and decrypt it
        challenge_data = requests.get(self.url + "/challenge/" + username)
        challenge = json.loads(challenge_data)
        encrypted_secret = challenge["challenge"]

        key = keys.utils.load_private_key(username, self.key_dir)
        secret = key.decrypt(encrypted_secret, DEFAULT_PADDING())

        # Send decrypted challenge along with new ip
        data = {"username": username,
                "challenge": secret,
                "ip": challenge["ip"]}
        result = requests.post(self.url + "/ip", data=data)
        return result

    def fetch_peer(self, username):
        return requests.get(self.url + "/user/" + username)

    def fetch_peer_ip(self, username):
        return requests.get(self.url + "/ip/" + username)

    def fetch_contact_ips(self):
        ips = []
        contact_names = os.listdir("../contacts")
        for name in contact_names:
            contact = self.fetch_peer_ip(name)
            ips.append(contact)
        return ips
