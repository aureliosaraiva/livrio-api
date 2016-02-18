# -*- coding: utf-8 -*-
def file_get_contents(filename):
    with open(filename) as f:
        return f.read()



def generate_password(password):
    import md5
    return md5.new(password + '_E-sPKrKn?SjL_#TFX!XG!L-rsGJbLw5-+!bcXxVg&LtW#KmF').hexdigest()

def is_password(password, password_encrypt):
    return generate_password(password) == password_encrypt