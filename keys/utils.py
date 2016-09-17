from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat, PrivateFormat, NoEncryption, load_pem_private_key, load_pem_public_key

PUBLIC = "PUBLIC"
PRIVATE = "PRIVATE"

def newKey():
    private_key = rsa.generate_private_key(public_exponent=65537,
        key_size=2048,
        backend=default_backend())

    #SAVE NEW PRIVATE KEY
    private_bytes = private_key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())

    with open("new_private.pem", "wb") as f:
        f.write(private_bytes)

    #WRITE C CODE FOR PUBLIC KEY
    public_key = private_key.public_key()
    public_bytes = public_key.public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)

    #hex_bytes = [ ("0x%02X" + get_sep(i)) % public_bytes[i] for i in range(len(public_bytes))]
    #public_key_c_def = "{\n\t" + "".join(hex_bytes) + "\n}"

    with open("new_public.pem", "wb") as f:
        f.write(public_bytes)

def loadKey(type):
    if type == PRIVATE:
        path = "keys\\private.pem"
        def load_func(data, backend): return load_pem_private_key(data, password=None, backend=backend)
    elif type == PUBLIC:
        path = "keys\\public.pem"
        load_func = load_pem_public_key
    else:
        raise ValueError("Unknown key type.")

    with open(path, "rb") as f:
        pem_data = f.read()
    return load_func(pem_data, backend=default_backend())

if __name__ == '__main__':
    newKey()
