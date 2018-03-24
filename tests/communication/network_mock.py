

class MockNetwork(object):

    def __init__(self, *args, **kwargs):
        self.has_peer_answer = False
        self.register_answer = None
        self.connect_answer = None
        self.get_peer_info_answer = None


    def raise_on_wrong_http_code(self, func):
        return lambda: None

    def has_peer(self, name):
        return self.has_peer_answer

    def register(self, username, public_pem):
        if self.register_answer != None:
            raise self.register_answer

    def connect(self, username):
        if self.connect_answer != None:
            raise self.connect_answer

    def get_peer_info(self, username):
        if self.get_peer_info_answer == None:
            data = self.fetch_peer(username)
            data.update(self.fetch_peer_ip(username))
            return data
        raise UserDoesNotExistError()

    def get_peer_ip(self, username):
        return "192.168.0.0"

    def fetch_peer(self, username):
        return {"username": username,
                "public_key": "Fake public key"}

    def fetch_peer_ip(self, username):
        return {"ip": "192.168.0.0"}

    def fetch_contact_ips(self):
        ips = [fetch_peer_ip("") for i in range(5)]
        return ips
