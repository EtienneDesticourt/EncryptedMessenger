from encryption.crypter import DEFAULT_PADDING
from communication.network_exception import NetworkException
from communication.network_exception import UnexpectedResponseError
from communication.network_exception import UserDoesNotExistError
from communication.network_exception import ChallengeFailureError
from communication.network_exception import CommandFailureError
import config
import requests
import logging
import keys.utils
import json
import base64

class Network(object):
    NO_USER_ERROR = {'error': 'No such user.'}
    EXISTING_USER_ERROR = {'error': 'User already exists.'}
    OK_RESPONSE = {'status': 'OK'}
    FAILED_CHALLENGE_ERROR = {'error': 'Challenge failed.'}
    NO_CHALLENGE_ERROR = {'error': 'No existing challenge for user.'}

    def __init__(self, url, key_dir=config.KEY_DIR):
        self.url = url
        self.key_dir = key_dir
        self.get = self.raise_on_wrong_http_code(requests.get)
        self.post = self.raise_on_wrong_http_code(requests.post)
        self.logger = logging.getLogger(__name__)
        self.logger.info("Created network consumer with url %s.", url)

    def raise_on_wrong_http_code(self, func):
        def new_func(*args, **kwargs):
            self.logger.debug("Executed query. args: %s, kwargs: %s", str(args), str(kwargs))
            resp = func(*args, **kwargs)
            if resp.status_code != 200:
                raise NetworkException(resp.status_code)
            return resp
        return new_func

    def has_peer(self, name):
        self.logger.info("Checking if peer %s exists.", name)
        response = self.fetch_peer(name)
        if response.json() == Network.NO_USER_ERROR:
            return False
        return True

    def register(self, username, public_pem):
        self.logger.info("Registering new user: %s", username)

        public_key = public_pem.decode("utf8")
        result = self.post(self.url + "/user", data={"username": username,
                                                     "public_key": public_key})

        content = result.json()
        if content == Network.OK_RESPONSE:
            return
        elif "error" in content:
            raise CommandFailureError(content["error"])
        else:
            raise UnpexpectedResponseError(content)

    def connect(self, username):
        self.logger.info("Connecting to network as %s.", username)
        # Ask for an auth challenge and decrypt it
        response = self.get(self.url + "/challenge/" + username)
        challenge = response.json()

        if "challenge" not in challenge or "ip" not in challenge:
            if challenge == Network.NO_USER_ERROR:
                raise UserDoesNotExistError()
            else:
                raise UnpexpectedResponseError("Server provided unexpected response to challenge request.")

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
            self.logger.info("Succesfully connected to network.")
            return
        elif content == Network.FAILED_CHALLENGE_ERROR or content == Network.NO_CHALLENGE_ERROR:
            raise ChallengeFailureError()
        else:
            raise UnexpectedResponseError("Server provided unexpected response to ip update request.")

    def get_peer_info(self, username):
        response = self.fetch_peer(username)
        content = response.json()
        if content == Network.NO_USER_ERROR:
            raise UserDoesNotExistError()
        ip = self.fetch_peer_ip(username)
        content.update(ip)
        return content

    def get_peer_ip(self, username):
        return self.fetch_peer_ip(username)["ip"]

    def fetch_peer(self, username):
        response = self.get(self.url + "/user/" + username)
        return response

    def fetch_peer_ip(self, username):
        self.logger.info("Fetching ip for %s", username)
        response = self.get(self.url + "/ip/" + username)
        return response.json()

    def fetch_contact_ips(self):
        ips = []
        contact_names = os.listdir("contacts")
        for name in contact_names:
            contact = self.fetch_peer_ip(name)
            ips.append(contact)
        return ips
