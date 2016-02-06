# -*- coding: utf-8 -*-
from flask import current_app as app
from datetime import datetime
from tasks import book_like
from bson.objectid import ObjectId

def notification_get(account_id):

    lookup = {'account_id': account_id}
    print lookup
    notifications = app.data.driver.db['notifications']

    cursor = notifications.find(lookup).sort([('_created', -1 )]).limit(20)

    d = []
    for document in cursor:
        d.append(document)

    return d


def notification_create(account_id, payload):
    notifications = app.data.driver.db['notifications']

    date_utc = datetime.utcnow().replace(microsecond=0)

    if 'from_id' in payload:
        payload['from_id'] = ObjectId(payload['from_id'])

    if 'book_id' in payload:
        payload['book_id'] = ObjectId(payload['book_id'])

    payload['account_id'] = account_id
    payload['_created'] = date_utc
    payload['_updated'] = date_utc
    payload['_deleted'] = False
    notifications.insert_one(payload)
    

    return payload

def notification_read(account_id, notification_id):
    notifications = app.data.driver.db['notifications']
    lookup = {'account_id': account_id, '_id': notification_id}

    doc = notifications.find_one(lookup)

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

        notifications.update(lookup,payload)

    return True

def notification_view(account_id, ids):
    notifications = app.data.driver.db['notifications']

    lookup = {'account_id': account_id, '_id': {'$in': ids} }

    date_utc = datetime.utcnow().replace(microsecond=0)
  
    payload = {
        '$set': {
            'view': True,
            'view_time': date_utc
        }
    }

    notifications.update(lookup,payload)

    return True

def account_info(account_id):
    db = app.data.driver.db['accounts']
    return db.find_one({'_id':account_id},{'fullname':1,'photo':1})

def book_info(book_id):
    db = app.data.driver.db['books']
    return db.find_one({'_id':book_id},{'title':1})

def notify_request_friend_delete(account_id, friend_id):
    db = app.data.driver.db['notifications']
    db.delete_one({
        'account_id': friend_id,
        'friend_id': account_id,
        'view': False    
    })

def notify_request_friend(account_id, friend_id):
    notifications = app.data.driver.db['notifications']

    date_utc = datetime.utcnow().replace(microsecond=0)
    payload = {}
    payload['account_id'] = friend_id
    payload['from_id'] = account_id
    payload['_created'] = date_utc
    payload['_updated'] = date_utc
    payload['_deleted'] = False
    payload['type'] = 'request_friend'
    payload['view'] = False

    payload['from'] = account_info(account_id)

    notifications.insert_one(payload)
    

    return payload


#@bugfix - verificar duplicados
def notify_recommend_book(account_id, friend_id, book_id):
    notifications = app.data.driver.db['notifications']

    date_utc = datetime.utcnow().replace(microsecond=0)
    payload = {}
    payload['account_id'] = friend_id
    payload['from_id'] = account_id
    payload['_created'] = date_utc
    payload['_updated'] = date_utc
    payload['_deleted'] = False
    payload['type'] = 'friend_recommend_book'
    payload['view'] = False

    payload['from'] = account_info(account_id)
    payload['book'] = book_info(book_id)

    notifications.insert_one(payload)
    

    return payload