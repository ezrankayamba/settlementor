from ldap3 import Server, Connection, SAFE_SYNC,  ALL, ALL_ATTRIBUTES
from pprint import pprint
import json

LDAP_SERVER_URI = 'LDAP://Directory01.tigo.co.tz'
LDAP_SEARCH_BASE = 'DC=tigo,DC=co,DC=tz'


def login(username, pwd):
    search_filter = f'(SAMAccountName=baraka.hamisi)'
    attrs = ALL_ATTRIBUTES
    # attrs = ['cn']
    server = Server(LDAP_SERVER_URI, get_info=ALL)
    usr = f'TIGO\{username}'
    with Connection(server, user=usr, password=pwd, client_strategy=SAFE_SYNC, auto_bind=True) as conn:
        status, result, response, _ = conn.search(LDAP_SEARCH_BASE, search_filter, attributes=attrs)
        # status, result, response, _ = conn.search(f'o={username}', '(objectclass=*)')
        if result['result'] == 0:
            print('Success')
            info = response[0]['raw_attributes']
            fullname = info['cn'][0].decode('utf-8')
            title = info['title'][0].decode('utf-8')
            phone = info['telephoneNumber'][0].decode('utf-8')
            fname = info['givenName'][0].decode('utf-8')
            lname = info['sn'][0].decode('utf-8')
            print(fullname, title, phone, fname, lname)
        # print(str(conn.extend.standard.who_am_i()))
        # res = str(conn.extend.standard.who_am_i()).split(":")[1] == usr
        # print(res)
        pprint(conn.entries)


if __name__ == '__main__':
    usr, pwd = 'godfred.nkayamba', '7242@!!Father'
    # login(usr, pwd)
    user_info(usr)
