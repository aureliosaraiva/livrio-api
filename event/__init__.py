# -*- coding: utf-8 -*-

from settings import db
from mixpanel import Mixpanel
from datetime import datetime
user_id = 1

mp = Mixpanel('3e5a5a623cb60717e75e983e06b40e30')


EVENT = {
    'signup': True,
    'signin': True,
    'account_update': True,
    'logout': True,
    'book_like': True,
    'book_comment': True,
    'book_view': True,
    'book_recommend': True,
    
    'book_create': True,
    'book_update': True,
    'book_search': True,
    'friend_request': True,
    'friend_accept': True,
    'friend_cancel': True,
    'friend_cancel': True,
    'contact_allow': True,
    'contact_view': True,
    'profile_view': True,
    'about_view': True
}

def register(event_type, account_id, book_id=None):
    date_utc = datetime.utcnow().replace(microsecond=0)
    payload = {
        '_created': date_utc,
        'event_type': event_type,
        'account_id': account_id,
        'book_id': book_id
    }
    db.event_track.insert_one(payload)

    if event_type in EVENT and EVENT[event_type]:
        track(event_type, str(account_id), None, timer=date_utc)

def track(event_type, account_id, data=None, timer=None):
    try:
        if not data:
            mp.track(account_id, event_type,meta={'$time':timer})
        elif data:
            mp.track(account_id, event_type, data,meta={'$time':timer})
    except:
        pass
    


def profile(account_id):

    doc = db.accounts.find_one({'_id':account_id})

    created = int(doc['_created'].strftime('%s'))

    payload = {
        '$name': doc['fullname'],
        '$email': doc['email'],
        '$created': str(doc['_created']),
        'books': doc['amount_books']
    }
    if 'amount_friends' in doc:
        payload['friends'] = doc['amount_friends']

    if 'gender' in doc:
        payload['gender'] = doc['gender']

    if 'location' in doc and 'state' in doc['location']: 
        payload['state'] = doc['location']['state']
        if 'city' in doc['location']:
            payload['city'] = doc['location']['city']

    mp.people_set(str(account_id),payload,{'$time':created})

def track_import(account_id, type_event, utc):
    
    mp.import_data('3e5a5a623cb60717e75e983e06b40e30',account_id, type_event,utc)
