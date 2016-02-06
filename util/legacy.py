# -*- coding: utf-8 -*-
import subprocess
import os

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