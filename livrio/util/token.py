import random
import string

def create():
    return '{}-{}-{}-{}'.format(
                (''.join(random.choice(string.ascii_uppercase) for x in range(5))),
                (''.join(random.choice(string.ascii_uppercase) for x in range(5))),
                (''.join(random.choice(string.ascii_uppercase) for x in range(5))),
                (''.join(random.choice(string.ascii_uppercase) for x in range(5)))
            )