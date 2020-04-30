from __future__ import unicode_literals
import string
import random

def get_random_id(size=8, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))