import json
import pysftp
import logging
from config import config as cfg

logger = logging.getLogger(__name__)


def download(path, filename):
    try:
        with open('credentials.json') as creds_file:
            creds = json.load(creds_file)
            cnopts = pysftp.CnOpts()
            cnopts.hostkeys = None
            creds['cnopts'] = cnopts
            with pysftp.Connection(**creds) as sftp:
                print('Connected...')
                local_path = cfg.sftp_local_path()
                sftp.get(f'{path}/{filename}', f'{local_path}{filename}')
                print(f'Downloaded successfully: {filename}')
        return True
    except Exception as ex:
        logger.debug(f'Error Downloading: {ex}')
        return False


def upload(path, filename):
    try:
        with open('credentials.json') as creds_file:
            creds = json.load(creds_file)
            cnopts = pysftp.CnOpts()
            cnopts.hostkeys = None
            creds['cnopts'] = cnopts
            with pysftp.Connection(**creds) as sftp:
                print('Connected...')
                local_path = cfg.sftp_local_path()
                sftp.put(f'{local_path}{filename}', f'{path}/{filename}')
                print(f'Uploaded successfully: {filename}')
        return True
    except Exception as ex:
        logger.debug(f'Error Uploading: : {ex}')
        return False
