from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from ldap3 import Server, Connection, SAFE_SYNC,  ALL, ALL_ATTRIBUTES
from config import config


class LDAPBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        try:
            print(f'LDAP: Try authenticating {username}')
            user = User.objects.get(username=username)
            if user and password:
                if user.is_staff or user.is_superuser:
                    server = Server(config.ldap_server_uri(), use_ssl=True)
                    usr = f'TIGO\\{username}'
                    with Connection(server, user=usr, password=password, client_strategy=SAFE_SYNC, auto_bind=True) as conn:
                        if str(conn.extend.standard.who_am_i()).split(":")[1] == usr:
                            search_filter = f'(SAMAccountName={username})'
                            status, result, response, _ = conn.search(config.ldap_search_base(), search_filter, attributes=ALL_ATTRIBUTES)
                            if result['result'] == 0:
                                info = response[0]['raw_attributes']
                                # fullname = info['cn'][0].decode('utf-8')
                                # title = info['title'][0].decode('utf-8')
                                phone = info['telephoneNumber'][0].decode('utf-8')
                                fname = info['givenName'][0].decode('utf-8')
                                lname = info['sn'][0].decode('utf-8')
                                mail = info['mail'][0].decode('utf-8')
                                if not user.email:
                                    user.email = mail
                                    user.first_name = fname
                                    user.last_name = lname
                                    user.save()
                                request.session['phone'] = phone
                                return user
                else:
                    if user.check_password(password):
                        print('Successfully authenticated the API user')
                        return user
        except Exception as ex:
            print('Failed: ', ex)

        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
