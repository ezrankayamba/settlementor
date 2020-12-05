from . import secure_store as ss
from cryptography.fernet import Fernet
import io
import ntpath
import hashlib
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
import base64
from Crypto.Signature import pkcs1_15, pss
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
import logging

logger = logging.getLogger(__name__)


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


def verify(filename, sign):
    with open(filename, "r") as file:
        data = file.read().replace('\n', '').encode('utf-8')
        public_key = get_public_key()
        signature = base64.b64decode(sign)
        msg_hash = SHA256.new(data)
        try:
            pss.new(public_key).verify(msg_hash, signature)
            return True
        except Exception as ex:
            logger.debug(ex)
            return False


def sign(filename, store_pass):
    with open(f'{filename}', "r") as file:
        data = file.read().replace('\n', '').encode('utf-8')
        private_key = get_private_key(store_pass)
        msg_hash = SHA256.new(data)
        sig = pss.new(private_key).sign(msg_hash)
        encoded = base64.b64encode(sig)
        signature = str(encoded, encoding='UTF-8')
        print(signature)
        return signature


def generate_key_pairs(password=None):
    if not password:
        print('Keypare generation requires password')
        return

    key = RSA.generate(2048)
    private_key = key.export_key()
    file_out = open("pki/private_key.pem", "wb")
    file_out.write(private_key)
    file_out.close()

    public_key = key.publickey().export_key()
    file_out = open("pki/public_key.pem", "wb")
    file_out.write(public_key)
    file_out.close()


def get_private_key(password=None):
    if not password:
        print('Password is required to retrive private key')
        return
    with open("pki/private_key2.pem", "rb") as key_file:
        # private_key = serialization.load_der_private_key(
        #     key_file.read(),
        #     password=password.encode(),
        #     backend=default_backend()
        # )
        private_key = RSA.import_key(key_file.read(), passphrase=password)
        return private_key


def get_public_key():
    with open("pki/public_key2.pem", "rb") as key_file:
        # public_key = serialization.load_der_public_key(
        #     key_file.read(),
        #     backend=default_backend()
        # )
        public_key = RSA.import_key(key_file.read())
        return public_key
