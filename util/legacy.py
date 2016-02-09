# -*- coding: utf-8 -*-
import subprocess
import os
import base64

def password_php(password, password_storage):
    try:
        cmd = "php {}/pass.php '{}' '{}'".format(os.path.dirname(__file__), password, password_storage)
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        out = proc.stdout.read()
        out = out.replace("'",'')
        if out == 'S':
            return True

        return False
    except:
        return False

def push_ios(token, message):
    try:
        message = base64.b64encode(message)
        cmd = "php {}/push_ios.php '{}' '{}'".format(os.path.dirname(__file__), token, message)
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        out = proc.stdout.read()
        out = out.replace("'",'')
        if out == 'S':
            return True

        return False
    except:
        return False