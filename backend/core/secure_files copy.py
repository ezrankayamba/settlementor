from . import secure_store as ss
from cryptography.fernet import Fernet
import io
import ntpath
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa


KEY_ENCRYPTION_FILE = 'FileEncryptionKey'


def encrypt(filename):
    key = get_file_enc_key().encode('utf-8')
    f = Fernet(key)
    with open(filename, "rb") as file:
        file_data = file.read()
        encrypted_data = f.encrypt(file_data)
        with open(f'{filename}.encrypted', "wb") as file:
            file.write(encrypted_data)


def decrypt(filename):
    key = get_file_enc_key().encode('utf-8')
    f = Fernet(key)
    with open(f'{filename}.encrypted', "rb") as file:
        encrypted_data = file.read()
        decrypted_data = f.decrypt(encrypted_data).decode('utf-8')
        print(decrypted_data)
        s = io.StringIO(decrypted_data)
        with open(filename, "w") as f:
            for line in s:
                f.write(line)


def generate_file_enc_key():
    key = Fernet.generate_key().decode('utf-8')
    ss.save('FileSharing', KEY_ENCRYPTION_FILE, key)
    print('Key: ', get_file_enc_key())


def get_file_enc_key():
    return ss.retrieve('FileSharing', KEY_ENCRYPTION_FILE)


def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)
