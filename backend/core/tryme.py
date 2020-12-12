from core import sftp_connect as sftp
from config import config as cfg


def run():
    file = 'test.csv'
    sftp.upload(file, cfg.sftp_tigo_path())
