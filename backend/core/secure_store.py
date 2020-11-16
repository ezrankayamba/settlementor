import keyring
from cryptography.fernet import Fernet

KEY_ENCRYPTION_KEY = 'EncryptionKey'
KEY_ENCRYPTION_STORE = 'Local'


def save(service, key, value):
    f = Fernet(get_encryption_key())
    keyring.set_password(service, key, f.encrypt(value.encode('utf-8')).decode('utf-8'))


def retrieve(service, key):
    f = Fernet(get_encryption_key())
    encrypted = keyring.get_password(service, key)
    return f.decrypt(encrypted.encode('utf-8')).decode('utf-8')


def generate_key():
    key = Fernet.generate_key()
    keyring.set_password(KEY_ENCRYPTION_STORE, KEY_ENCRYPTION_KEY, key.decode('utf-8'))


def get_encryption_key():
    return keyring.get_password(KEY_ENCRYPTION_STORE, KEY_ENCRYPTION_KEY).encode('utf-8')
