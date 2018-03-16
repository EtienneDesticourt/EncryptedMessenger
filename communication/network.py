from encryption.crypter import DEFAULT_PADDING, OPENSSL_PADDING
from communication.exceptions import NetworkException
from communication.exceptions import UnexpectedResponseError
from communication.exceptions import UserDoesNotExistError
from communication.exceptions import ChallengeFailureError
from communication.exceptions import CommandFailureError
import config
import requests
import logging
import keys.utils
import json
import base64

# TODO: Rename class, network might be meaningless in this context, or not explicit enough (PeerNetwork ? PeerResolver? PeerRegistry?)
class Network(object):
    """Manages connections to the network of peers on which users are registered.

    Args:
        url: The endpoint to the peer network's API.
        key_dir: The directory in which the user's private key is stored.
    """
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
        """Creates a function that will raise a NetworkException when failling to fetch an http resource.

        Args:
            func: A function that returns an object that holds an http status code.

        Returns:
            A function that raises a NetworkException when the http functions returns an error status code.
        """
        def new_func(*args, **kwargs):
            self.logger.debug("Executed query. args: %s, kwargs: %s", str(args), str(kwargs))
            resp = func(*args, **kwargs)
            if resp.status_code != 200:
                raise NetworkException(resp.status_code)
            return resp
        return new_func

    def has_peer(self, name):
        """Checks whether the network has a peer with a specific name.

        Args:
            name: The name of the peer to look for.

        Returns:
            A boolean indicating whether the peer exists.
        """
        self.logger.info("Checking if peer %s exists.", name)
        response = self.fetch_peer(name)
        if response.json() == Network.NO_USER_ERROR:
            return False
        return True

    def register(self, username, public_pem):
        """Registers a user on the peer network.

        Args:
            username: The name to register with.
            public_pem: The public key to publicize so other users can connect to you.

        Raises:
            CommandFailureError: The peer network returned an error when attempting to register.
            UnexpectedResponseError: The network answered with an unexpected message.
        """
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
        """Connects to the network to update the user's ip.

        Args:
            username: The username of the user with which to connect.

        Raises:
            UserDoesNotExistError: There is no user with that username registered on the network.
            UnexpectedResponseError: The network answered with an unexpected message.
            ChallengeFailureError: The user failed to authenticate by solving the network's challenge with his private key.

        """
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
        secret_bytes = key.decrypt(encrypted_secret, OPENSSL_PADDING())
        secret = secret_bytes.decode('utf8')

        # Send decrypted challenge along with new ip
        data = {"username": username,
                "challenge": secret,
                "ip": challenge["ip"]}
        self.logger.debug("Messenger public ip is %s.", challenge["ip"])

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
        """Fetches the contact information (ip and public key) of the specified user.

        Args:
            username: The name of the user whose info we want to fetch.

        Returns:
            A JSON string that holds the user's data.

        Raises:
            UserDoesNotExistError: There is no user with that username registered on the network.
        """
        response = self.fetch_peer(username)
        content = response.json()
        if content == Network.NO_USER_ERROR:
            raise UserDoesNotExistError()
        ip = self.fetch_peer_ip(username)
        content.update(ip)
        return content

    def get_peer_ip(self, username):
        """Fetches the last recorded ip of the specified user.

        Args:
            username: The name of the user whose ip we want to fetch.

        Returns:
            The user's ip.
        """
        return self.fetch_peer_ip(username)["ip"]

    def fetch_peer(self, username):
        """Fetches the specified user's identification info (username and public key).

        Args:
            username: The name of the user whose ip we want to fetch.

        Returns:
            A JSON string that holds the user's public key and username.
        """
        response = self.get(self.url + "/user/" + username)
        return response

    def fetch_peer_ip(self, username):
        """Fetches the last recorded ip of the specified user.

        Args:
            username: The name of the user whose ip we want to fetch.

        Returns:
            A JSON string holding the user's ip.
        """
        self.logger.info("Fetching ip for %s", username)
        response = self.get(self.url + "/ip/" + username)
        return response.json()

    # TODO: Doesn't seem to be used and returns nonsensical results [list of ips with no other in ordered by listdir's order, weird]: Remove!
    def fetch_contact_ips(self): # TODO: contact-> contacts
        """Fetches the ips of all the user's contacts.

        Returns:
            A list of ips.
        """
        ips = []
        contact_names = os.listdir("contacts")
        for name in contact_names:
            contact = self.fetch_peer_ip(name)
            ips.append(contact)
        return ips
