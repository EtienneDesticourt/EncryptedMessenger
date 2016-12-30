

class Contact(object):
    def __init__(self, name, public_key, ip=None):
        self.name = name
        self.public_key = public_key
        self.ip = ip

    def save(self, dir):
        path = os.path.join(dir, self.name)
        with open(path, "w") as f:
            f.write(self.public_key)

