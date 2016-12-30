from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat, PrivateFormat, NoEncryption, load_pem_private_key, load_pem_public_key
import os

PUBLIC = "PUBLIC"
PRIVATE = "PRIVATE"
PUBLIC_KEY_FILE = "public.pem"
PRIVATE_KEY_FILE = "private.pem"

def gen_key_path(username, directory):
    private_path = os.path.join(directory, username + "_private.pem")
    public_path = os.path.join(directory, username + "_public.pem")
    return (public_path, private_path)

def new_key(username, directory):
    public_path, private_path = gen_key_path(username, directory)

    private_key = rsa.generate_private_key(public_exponent=65537,
                                           key_size=2048,
                                           backend=default_backend())
    private_bytes = private_key.private_bytes(Encoding.PEM,
                                              PrivateFormat.PKCS8,
                                              NoEncryption())


    public_key = private_key.public_key()
    public_bytes = public_key.public_bytes(Encoding.PEM,
                                           PublicFormat.SubjectPublicKeyInfo)

    # WRITE C CODE FOR PUBLIC KEY
    #hex_bytes = [ ("0x%02X" + get_sep(i)) % public_bytes[i] for i in range(len(public_bytes))]
    #public_key_c_def = "{\n\t" + "".join(hex_bytes) + "\n}"

    with open(private_path, "wb") as f:
        f.write(private_bytes)
    with open(public_path, "wb") as f:
        f.write(public_bytes)

    return (public_path, private_path)

def load_private_key(username, directory):
    public_path, private_path = gen_key_path(username, directory)
    with open(private_path, "rb") as f:
        pem_data = f.read()
    return = load_pem_private_key(pem_data, password=None, backend=default_backend())

def load_key(type, directory):
    if type == PRIVATE:
        path = os.path.join(directory, PRIVATE_KEY_FILE)
        def load_func(data, backend):
            return load_pem_private_key(data, password=None, backend=backend)
    elif type == PUBLIC:
        path = os.path.join(directory, PUBLIC_KEY_FILE)
        load_func = load_pem_public_key
    else:
        raise ValueError("Unknown key type.")

    with open(path, "rb") as f:
        pem_data = f.read()
    return load_func(pem_data, backend=default_backend())



if __name__ == '__main__':
    newKey()
