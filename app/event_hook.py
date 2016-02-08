# -*- coding: utf-8 -*-
from util import token
import json
from flask import request, current_app as app, g, abort
from model import book
from bson.objectid import ObjectId

def evt_create_account(items):
    account = items[0]
    data = {
        'account': account,
        'type':'signup'
    }
    print data
    #send_email.task_send_email.apply_async([data])

def evt_create_token(documents):
    for document in documents:
        document["token"] = token.create()


def evt_book_get_result(request, payload):
    data = json.loads(payload.get_data())
    print data
    if not '_items' in data:
        
        if not 'cover' in data:
            data['cover'] = 'img/cover.gif'

        account_id = app.auth.get_request_auth_value()
        
        data['is_like'] = book.book_is_like(account_id, ObjectId(data['_id']))
    
    payload.set_data(json.dumps(data))
