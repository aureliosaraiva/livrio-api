# -*- coding: utf-8 -*-
from datetime import datetime
from bson.objectid import ObjectId
from settings import PRIMARY_ACCOUNT, db

TYPE = {
    'SYSTEM_WELCOME':'system_welcome',
    'SYSTEM_FIRST_BOOK':'system_first_book',
    'SYSTEM_LIBRARY_EMPTY':'system_library_empty',
    'INFO_TEXT':'info_text',
    'SYSTEM_UPDATE':'system_updated',
    'FRIEND':'friend',
    'FRIEND_LIKE_BOOK':'friend_like_book',
    'FRIEND_RECOMMEND_BOOK':'friend_recommend_book',
    'REQUEST_FRIEND':'request_friend',
    'LENT_SENT':'lent_sent',
    'LOAN_REQUEST':'loan_request',
    'LOAN_CONFIRM':'loan_confirm',
    'LOAN_CONFIRM_YES':'loan_confirm_yes',
    'LOAN_CONFIRM_NO':'loan_confirm_no',
    'LOAN_RETURN':'loan_return',
    'LOAN_RETURN_CONFIRM':'loan_return_confirm',
    'LOAN_REQUEST_RETURN':'loan_request_return',
    'LOAN_SENT_CANCELED':'loan_sent_canceled',
    'LOAN_SENT_REFUSED':'loan_sent_refused',
    'BOOK_LOAN_RETURN':'book_loan_return',
    'BOOK_LOAN_RETURN_DAY':'book_loan_return_day',
    'BOOK_LOAN_LATE':'book_loan_late'
}


def notification_get(account_id):

    lookup = {'account_id': account_id}
    


    cursor = db.notifications.find(lookup).sort([('_created', -1 )]).limit(20)

    d = []
    for document in cursor:
        if not 'from' in document:
            document['from'] = account_info(document['from_id'])

        if not 'book' in document and 'book_id' in document:
            document['book'] = book_info(document['book_id'])

        d.append(document)

    return d


def notification_create(account_id, payload):

    date_utc = datetime.utcnow().replace(microsecond=0)

    if 'from_id' in payload:
        payload['from_id'] = ObjectId(payload['from_id'])

    if 'book_id' in payload:
        payload['book_id'] = ObjectId(payload['book_id'])

    payload['account_id'] = account_id
    payload['_created'] = date_utc
    payload['_updated'] = date_utc
    payload['_deleted'] = False
    db.notifications.insert_one(payload)
    

    return payload

def notification_read(account_id, notification_id):

    lookup = {'account_id': account_id, '_id': notification_id}

    doc = db.notifications.find_one(lookup)

    if not doc:
        return None

    if 'read' in doc and doc['read'] == False or not ('read' in doc):
        date_utc = datetime.utcnow().replace(microsecond=0)
      
        payload = {
            '$set': {
                'read': True,
                'read_time': date_utc
            }
        }

        db.notifications.update(lookup,payload)

    return True

def notification_view(account_id, ids):


    lookup = {'account_id': account_id, '_id': {'$in': ids} }

    date_utc = datetime.utcnow().replace(microsecond=0)
  
    payload = {
        '$set': {
            'view': True,
            'view_time': date_utc
        }
    }

    db.notifications.update(lookup,payload)

    return True

def account_info(account_id):
    return db.books.find_one({'_id':account_id},{'fullname':1,'photo':1})

def book_info(book_id):  
    return db.books.find_one({'_id':book_id},{'title':1})

def notify_request_friend_delete(account_id, friend_id):

    db.notifications.delete_one({
        'account_id': friend_id,
        'from_id': account_id,
        'view': False    
    })


def notify(friend_id, account_id=None, book_id=None, group=None):

    if not account_id:
        account_id = PRIMARY_ACCOUNT

   

    date_utc = datetime.utcnow().replace(microsecond=0)
    payload = {}
    payload['account_id'] = friend_id
    payload['from_id'] = account_id
    payload['_created'] = date_utc
    payload['_updated'] = date_utc
    payload['_deleted'] = False
    payload['view'] = False
    payload['from'] = account_info(account_id)

    payload['type'] = group

    if book_id:
        payload['book'] = book_info(book_id)

    db.notifications.insert_one(payload)
    

    return payload
