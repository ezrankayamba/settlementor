import configparser
from django.conf import settings

BASE_DIR = settings.BASE_DIR
config = configparser.ConfigParser()
config.read(f'{BASE_DIR}/config/settings.ini')


def bal_url():
    base_url = config.get('ENDPOINTS', 'MTPG_BASE_URL')
    p = config.get('ENDPOINTS', 'BAL_CHECK_PROFILE_ID')
    return f'{base_url}?p={p}'


def tta_url():
    base_url = config.get('ENDPOINTS', 'MTPG_BASE_URL')
    p = config.get('ENDPOINTS', 'TTA_TRANSFER_PROFILE_ID')
    return f'{base_url}?p={p}'


def result_file_url():
    return config.get('ENDPOINTS', 'RESULT_FILE_URL')


def approval_url():
    return config.get('ENDPOINTS', 'APPROVAL_URL')


def env_token_exp():
    return int(config.get('ENVIRONMENT', 'ENV_TOKEN_EXP'))


def sftp_tigo_path():
    return config.get('TTA_SFTP', 'REMOTE_TIGO_PATH')


def sftp_tapsoa_path():
    return config.get('TTA_SFTP', 'REMOTE_TAPSOA_PATH')


def sftp_local_path():
    return config.get('TTA_SFTP', 'LOCAL_PATH')


def consumer_data(name='TTA_TAPSOA'):
    return (config.get(name, 'username'), config.get(name, 'password'), config.get(name, 'brand_id'))


def ldap_server_uri():
    return config.get('LDAP', 'LDAP_SERVER_URI')


def ldap_search_base():
    return config.get('LDAP', 'LDAP_SEARCH_BASE')
