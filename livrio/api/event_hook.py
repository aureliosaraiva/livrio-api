# -*- coding: utf-8 -*-
from util import token
from model import isbn
import json
from flask import abort

def evt_isbn_pre_get(request, lookup):
    book = isbn.find_isbn(request.args['v'])
    print "========="
    if not book:
        abort(404, description='ISBN not found')    
    else:
        lookup['_id'] = book[0]['_id']

#@bugfix
def evt_isbn_post_get(request, payload):
    d = json.loads(payload.get_data())
    payload.set_data(json.dumps(d['_items'][0]))

def evt_create_token(documents):
    for document in documents:
        document["token"] = token.create()