from __future__ import unicode_literals
import string
import random

def get_random_id(size=8, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def check_if_empty(lists):
    for elem in lists:
        if elem:
            return False
    return True