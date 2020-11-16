from django.contrib.auth.models import User
import random
import string


def create_consumer(username):
    pwd = get_random_string(10)
    user = User.objects.create(username=username)
    user.set_password(pwd)
    print('User created: ', pwd)


def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str
