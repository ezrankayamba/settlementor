import json
import pysftp


def download(path, filename):
    with open('credentials.json') as creds_file:
        creds = json.load(creds_file)
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        creds['cnopts'] = cnopts
        with pysftp.Connection(**creds) as sftp:
            print('Connected...')
            sftp.get(f'{path}/{filename}', f'/files/{filename}')
            print(f'Downloaded successfully: {filename}')


def upload(path, filename):
    with open('credentials.json') as creds_file:
        creds = json.load(creds_file)
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        creds['cnopts'] = cnopts
        with pysftp.Connection(**creds) as sftp:
            print('Connected...')
            sftp.put(f'/files/{filename}', f'{path}/{filename}')
            print(f'Uploaded successfully: {filename}')
