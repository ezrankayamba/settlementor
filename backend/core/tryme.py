from core import sftp_connect as sftp
from config import config as cfg

if __name__ == "__main__":
    file = 'test.csv'
    cfg.upload(f'{cfg.sftp_local_path}/{file}', f'{cfg.sftp_tigo_path()}/{file}')
