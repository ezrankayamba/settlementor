from core import sftp_connect as sftp
from config import config as cfg


def run():
    file = 'test.csv'
    sftp.upload(f'{cfg.sftp_local_path}/{file}', f'{cfg.sftp_tigo_path()}/{file}')
