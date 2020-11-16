from . import secure_store as ss
from cryptography.fernet import Fernet
import io
import ntpath
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding


def encrypt(filename):
    with open(filename, "rb") as file:
        file_data = file.read()
        public_key = get_public_key()
        encrypted_data = public_key.encrypt(
            file_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        with open(f'{filename}.encrypted', "wb") as file:
            file.write(encrypted_data)


def decrypt(filename, store_pass):
    with open(f'{filename}.encrypted', "rb") as file:
        encrypted_data = file.read()
        private_key = get_private_key(store_pass)
        decrypted_data = private_key.decrypt(
            encrypted_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        ).decode('utf-8')
        print(decrypted_data)
        s = io.StringIO(decrypted_data)
        with open(filename, "w") as f:
            for line in s:
                f.write(line)


def generate_key_pairs(password=None):
    if not password:
        print('Keypare generation requires password')
        return

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(password.encode())
    )
    with open('pki/private_key.pem', 'wb') as f:
        f.write(pem)

    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    with open('pki/public_key.pem', 'wb') as f:
        f.write(pem)


def get_private_key(password=None):
    if not password:
        print('Password is required to retrive private key')
        return
    with open("pki/private_key.pem", "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=password.encode(),
            backend=default_backend()
        )
        return private_key


def get_public_key():
    with open("pki/public_key.pem", "rb") as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read(),
            backend=default_backend()
        )
        return public_key
