# -*- coding: utf-8 -*-
from settings import db
from datetime import datetime, timedelta
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



def all(account_id, params=None):

    lookup = { '$or' :[{ 'owner_id': account_id}, {'friend_id': account_id}] }

    if 'active' in params:
        lookup['status'] = {'$in': ['sent','requested','delivery','delivered','request_return','confirm_return','send_return']}
    else:
        lookup['status'] = {'$in': ['cancel','finish']}

    print lookup
    print params
    cursor = db.books_loans.find(lookup).sort('_created',-1)

    arr = []
    for doc in cursor:
        doc['friend'] = account.info(doc['friend_id'])
        doc['owner'] = account.info(doc['owner_id'])
        doc['book'] = book.info(doc['book_id'])
        arr.append(doc)

    return arr

def info(account_id, loan_id):

    doc = db.books_loans.find_one({'_id': loan_id})

    if not doc['owner_id'] == account_id:
        if not doc['friend_id'] == account_id:
            return None

    data = {
        '_id': doc['_id'],
        'friend': account.info(doc['friend_id']),
        'owner': account.info(doc['owner_id']),
        'book': book.info(doc['book_id']),
        'status': doc['status'],
        '_created': doc['_created'],
        'duration': doc['duration']
    }

    if 'address' in doc:
        data['address'] = doc['address']

    if 'delivered_date' in doc:
        data['delivered_date'] = doc['delivered_date']

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
    
    user['account_id'] = user['_id']
    user['_id'] = payload['_id']

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


def address(account_id, loan_id, address):
    lookup = { '$or' :[{ 'owner_id': account_id}, {'friend_id': account_id}], '_id': loan_id }
    db.books_loans.update_one(lookup,{'$set':{'address': address}})

    create_messages(account_id, loan_id, 'Local de entrega: \n' + address,True)


def change_status(account_id, loan_id, data):
    
    lookup = {'_id': loan_id}
    date_utc = datetime.utcnow().replace(microsecond=0)
    doc = db.books_loans.find_one(lookup)


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

    if data['status'] == 'delivery':
        payload['$set']['delivered_date'] = date_utc + timedelta(days=int(doc['duration']))

    if data['status'] == 'finish':
        payload['$set']['finished_date'] = date_utc

    
    db.books_loans.update_one(lookup,payload)

    lookup = {'_id': doc['book_id']}


    if data['status'] in ['requested_denied','returned','sent_canceled','requested_canceled','cancel','finish']:
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

def messages(account_id, loan_id, offset=0):

    offset = int(offset)
    print {'_id': loan_id}
    doc = db.books_loans.find_one({'_id': loan_id},{'messages':1})

    print doc
    print loan_id
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

def create_messages(account_id, loan_id, text, system=False):

    date_utc = datetime.utcnow().replace(microsecond=0)

    payload = {
        '_id': ObjectId(),
        'account_id': account_id,
        'text': text,
        '_created': date_utc
    }

    if system:
        payload['system'] = True



    db.books_loans.update_one({'_id': loan_id}, {'$push':{'messages': payload}}, upsert=False)

    return payload