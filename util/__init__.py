# -*- coding: utf-8 -*-
def file_get_contents(filename):
    with open(filename) as f:
        return f.read()


