# -*- coding: utf-8 -*-
from settings import db
from datetime import datetime
from bson.objectid import ObjectId
import account
import book
import notification
from dateutil.parser import parse

STATUS_NOTIFICATION = {
    'wait_delivery': 'LOAN_CONFIRM_YES',
    'wait_delivery': 'LOAN_SENT_CANCELED',
    'sent_refused': 'LOAN_SENT_REFUSED',
    'requested_denied': 'LOAN_CONFIRM_NO',
    'wait_delivery_canceled': 'LOAN_CONFIRM_NO',
    'requested_returned': 'LOAN_REQUEST_RETURN',
    'wait_return': 'LOAN_RETURN_CONFIRM'
}



def info(account_id, book_id):
    lookup = {'_id': book_id}

    bok = db.books.find_one(lookup)

    if not 'loaned' in bok:
        return None

    doc = db.books_loans.find_one({'_id': bok['loaned']['loan_id']})

    print doc['owner_id']
    print account_id
    if not doc['owner_id'] == account_id:
        if not doc['friend_id'] == account_id:
            return None

    print doc
    data = {
        '_id': doc['_id'],
        'friend': account.info(doc['friend_id']),
        'owner': account.info(doc['owner_id']),
        'book': book.info(book_id),
        'status': doc['status'],
        '_created': doc['_created'],
        'duration': doc['duration']
    }

    return data



def start_loan(account_id, book_id, friend_id, data):

    date_utc = datetime.utcnow().replace(microsecond=0)

    lookup = {'_id': book_id}

    doc = db.books.find_one(lookup)

    if 'loaned' in doc:
        return None


    # Dono do livro ta emprestando
    if doc['account_id'] == account_id:
        type_request = 'sent'
        type_notification = 'LOAN_CONFIRM'


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

    return user

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


    print payload

    if data['status'] in ['requested_denied','returned','sent_canceled','requested_canceled']:
        db.books.update_one(lookup,{'$unset':{'loaned':''}})
    else:
        db.books.update_one(lookup,{'$set':{'loaned.status':data['status']}})

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

def messages(account_id, book_id, offset=0):

    offset = int(offset)
    lookup = {'_id': book_id}

    bok = db.books.find_one(lookup)

    if not 'loaned' in bok:
        return None

    doc = db.books_loans.find_one({'_id': bok['loaned']['loan_id']},{'messages':1})

    if 'messages' in doc:
        d = []
        i = -1
        for m in doc['messages']:
            i += 1
            if i>offset:
                d.append(m)
            
        return d

    else:
        return []

def create_messages(account_id, book_id, text):
    lookup = {'_id': book_id}

    bok = db.books.find_one(lookup)

    if not 'loaned' in bok:
        return None

    date_utc = datetime.utcnow().replace(microsecond=0)

    payload = {
        '_id': ObjectId(),
        'account_id': account_id,
        'text': text,
        '_created': date_utc
    }



    db.books_loans.update_one({'_id': bok['loaned']['loan_id']}, {'$push':{'messages': payload}}, upsert=False)

    return payload