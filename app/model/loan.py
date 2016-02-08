# -*- coding: utf-8 -*-
from flask import current_app as app
from datetime import datetime
from bson.objectid import ObjectId
import account



def start_loan(account_id, book_id, friend_id, data):
    db = app.data.driver.db['books']
    date_utc = datetime.utcnow().replace(microsecond=0)

    lookup = {'_id': book_id}

    doc = db.find_one(lookup)

    if 'loaned' in doc:
        return None


    # Dono do livro ta emprestando
    if doc['account_id'] == account_id:
        type_request = 'sent'

    # Amigo está pedindo emprestado
    else:
        type_request = 'requested'

    payload = {
        '_created': date_utc,
        '_updated': date_utc,
        '_deleted': False,
        'book_id': book_id,
        'owner_id': doc['account_id'],
        'friend_id': friend_id,
        'type': type_request,
        'status': type_request
    }

    user = account.account_info_basic(friend_id)

    if 'duration' in data:
        payload['duration'] = data['duration']
        user['duration'] = data['duration']

    app.data.driver.db['books_loans'].insert_one(payload)

    
    user['status'] = type_request
    user['loan_id'] = payload['_id']

    db.update_one(lookup,{
        '$set':{
            'loaned':user
        }
    })

    return True

def change_status(account_id, book_id, data):
    db = app.data.driver.db['books']
    lookup = {'_id': book_id}
    date_utc = datetime.utcnow().replace(microsecond=0)
    doc = db.find_one(lookup)

    if not 'loaned' in doc:
        return None

    payload = {
        '$set': {
            'status': data['status'],
            'text': data['text']
        },
        '$push': {
            'log': {
                '_created': date_utc,
                'status': data['status'],
                'text': data['text']
            }
        }
    }

    
    app.data.driver.db['books_loans'].update_one({'_id': doc['loaned']['loan_id']},payload)

    if data['status'] in ['requested_denied','returned','sent_canceled','requested_canceled']:
        db.update_one(lookup,{'$unset':{'loaned':''}})

    return True

def get_info_old(account_id, loan_id):
    db = app.data.driver.db['books_loans']

    doc = db.find_one({'_id':loan_id},{'status':1, 'duration':1, '_created':1,'friend_id':1})

    if not doc:
        return False

    doc['expired'] = doc['duration']
    del doc['duration']


    user = account.account_info_basic(doc['friend_id'])
    del doc['friend_id']
    doc.update(user)

    return doc