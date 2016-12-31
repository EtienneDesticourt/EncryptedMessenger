from encryption.crypter import DEFAULT_PADDING
from communication.network_exception import NetworkException
from communication.network_exception import UnexpectedResponseError
from communication.network_exception import UserDoesNotExistError
from communication.network_exception import ChallengeFailureError
import requests
import keys.utils
import json
import base64

KEY_DIR = "keys"


class Network(object):
    NO_USER_ERROR = {'error': 'No such user.'}
    EXISTING_USER_ERROR = {'error': 'User already exists.'}
    OK_RESPONSE = {'status': 'OK'}
    FAILED_CHALLENGE_ERROR = {'error': 'Challenge failed.'}
    NO_CHALLENGE_ERROR = {'error': 'No existing challenge for user.'}

    def __init__(self, url, key_dir=KEY_DIR):
        self.url = url
        self.key_dir = key_dir
        self.get = self.raise_on_wrong_http_code(requests.get)
        self.post = self.raise_on_wrong_http_code(requests.post)

    def raise_on_wrong_http_code(self, func):
        def new_func(*args, **kwargs):
            resp = func(*args, **kwargs)
            if resp.status_code != 200:
                raise NetworkException(resp.status_code)
            return resp
        return new_func

    def has_peer(self, name):
        response = self.fetch_peer(name)
        if response.json() == Network.NO_USER_ERROR:
            return False
        return True

    def register(self, username):
        private_path, public_path = keys.utils.new_key(username, self.key_dir)
        with open(public_path, "r") as f:
            public_key = f.read()

        result = self.post(self.url + "/user", data={"username": username,
                                                     "public_key": public_key})


        content = result.json()
        if content == Network.OK_RESPONSE:
            return (True, "")
        elif "error" in content:
            return (False, content["error"])
        else:
            raise UnpexpectedResponseError(content)


    def connect(self, username):
        # Ask for an auth challenge and decrypt it
        response = self.get(self.url + "/challenge/" + username)
        challenge = response.json()

        if "challenge" not in challenge or "ip" not in challenge:
            if challenge == Network.NO_USER_ERROR:
                raise UserDoesNotExistError()
            else:
                raise UnpexpectedResponseError()

        encrypted_secret = base64.b64decode(challenge["challenge"])
        key = keys.utils.load_private_key(username, self.key_dir)
        secret_bytes = key.decrypt(encrypted_secret, DEFAULT_PADDING())
        secret = secret_bytes.decode('utf8')

        # Send decrypted challenge along with new ip
        data = {"username": username,
                "challenge": secret,
                "ip": challenge["ip"]}

        result = self.post(self.url + "/ip", data=data)
        content = result.json()
        if content == Network.OK_RESPONSE:
            return
        elif content == Network.FAILED_CHALLENGE_ERROR or content == Network.NO_CHALLENGE_ERROR:
            raise ChallengeFailureError("Failed to solve the challenge. There might be a server problem or you're using the wrong key.")
        else:
            raise UnexpectedResponseError()

    def fetch_peer(self, username):
        response = self.get(self.url + "/user/" + username)
        return response

    def fetch_peer_ip(self, username):
        return requests.get(self.url + "/ip/" + username)

    def fetch_contact_ips(self):
        ips = []
        contact_names = os.listdir("contacts")
        for name in contact_names:
            contact = self.fetch_peer_ip(name)
            ips.append(contact)
        return ips
