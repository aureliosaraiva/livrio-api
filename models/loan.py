# -*- coding: utf-8 -*-
from settings import db
from datetime import datetime
from bson.objectid import ObjectId
import account

STATUS_NOTIFICATION = {
    'wait_delivery': 'LOAN_CONFIRM_YES',
    'wait_delivery': 'LOAN_SENT_CANCELED',
    'sent_refused': 'LOAN_SENT_REFUSED',
    'requested_denied': 'LOAN_CONFIRM_NO',
    'wait_delivery_canceled': 'LOAN_CONFIRM_NO',
    'requested_returned': 'LOAN_REQUEST_RETURN',
    'wait_return': 'LOAN_RETURN_CONFIRM'
}


def start_loan(account_id, book_id, friend_id, data):

    date_utc = datetime.utcnow().replace(microsecond=0)

    lookup = {'_id': book_id}

    doc = db.books.find_one(lookup)

    if 'loaned' in doc:
        return None


    # Dono do livro ta emprestando
    if doc['account_id'] == account_id:
        type_request = 'sent'
        type_notification = 'LENT_SENT'

    # Amigo está pedindo emprestado
    else:
        type_request = 'requested'
        type_notification = 'LOAN_REQUEST'

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

    db.books_loans.insert_one(payload)

    
    user['status'] = type_request
    user['loan_id'] = payload['_id']

    db.books.update_one(lookup,{
        '$set':{
            'loaned':user
        }
    })

    # Notificações
    notification.notify(
        account_id=account_id, 
        friend_id=friend_id, 
        book_id=book_id, 
        group=notification.TYPE[type_notification])

    return True

def change_status(account_id, book_id, data):
    
    lookup = {'_id': book_id}
    date_utc = datetime.utcnow().replace(microsecond=0)
    doc = db.books.find_one(lookup)

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

    
    db.books_loans.update_one({'_id': doc['loaned']['loan_id']},payload)



    if data['status'] in ['requested_denied','returned','sent_canceled','requested_canceled']:
        db.update_one(lookup,{'$unset':{'loaned':''}})

    # Notificação
    if data['status'] in STATUS_NOTIFICATION:
        loaned = db.books_loans.find_one({'_id': doc['loaned']['loan_id']})
        if account_id == loaned['owner_id']:
            account_id = loaned['owner_id']
            friend_id = loaned['friend_id']
        else:
            account_id = loaned['friend_id']
            friend_id = loaned['owner_id']

        notification.notify(
            account_id=account_id, 
            friend_id=friend_id, 
            book_id=book_id, 
            group=notification.TYPE[STATUS_NOTIFICATION[data['status']]])

    return True

def get_info_old(account_id, loan_id):

    doc = db.books_loans.find_one({'_id':loan_id},{'status':1, 'duration':1, '_created':1,'friend_id':1})

    if not doc:
        return False

    doc['expired'] = doc['duration']
    del doc['duration']


    user = account.account_info_basic(doc['friend_id'])
    del doc['friend_id']
    doc.update(user)

    return doc