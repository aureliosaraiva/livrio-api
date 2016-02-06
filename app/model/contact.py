# -*- coding: utf-8 -*-
from flask import current_app as app
from datetime import datetime
from bson.objectid import ObjectId

def contact_save(account_id, data):
    db = app.data.driver.db['phone_contacts']

    date_utc = datetime.utcnow().replace(microsecond=0)

    for item in data:
        lookup = {'account_id': account_id, 'contact_id': item['id']}

        payload_data = {
            '_created': date_utc,
            'source': item
        }

        emails = []
        if item['emails']:
            for e in item['emails']:
                if e['value'].find('@'):
                    emails.append(e['value'])
            payload_data['emails'] = emails

        phones = []
        if item['phoneNumbers']:
            for e in item['phoneNumbers']:
                if len(e['value']) >=8 :
                    phones.append(e['value'])
            payload_data['phones'] = emails

        if item['displayName']:
            payload_data['fullname'] = item['displayName']

        payload = {
            '$set': payload_data
        }

        db.update_one(lookup,payload, upsert=True)

def contact_get(account_id, params):
    db = app.data.driver.db['phone_contacts']

    lookup = {
        'account_id': account_id,
        'fullname': {'$exists':True}
    }

    if params:
        if 'search' in params:
            lookup["$text"] = { '$search': params['search'] }

    print lookup
    cursor = db.find(lookup,{ 'fullname':1,'invited':1,'score': { '$meta': "textScore" } }).sort([('score', { '$meta': "textScore" } )])

    limit = 25
    offset = 0

    if 'limit' in params:
        limit = int(params['limit'])

    if 'offset' in params:
        offset = int(params['offset'])

    if offset > 0:
        offset = ((offset-1)*limit)

    cursor.skip(offset).limit(limit)

    d = []
    for document in cursor:
        d.append(document)

    return d


#@bugfix enviar email aqui
def contact_invite(account_id, contact_id):
    db = app.data.driver.db['phone_contacts']
    lookup = {'_id': contact_id,'account_id':account_id}
    doc = db.find_one(lookup);

    if not doc:
        return None

    date_utc = datetime.utcnow().replace(microsecond=0)

    payload = {
        '$set': {
            'invited': True,
            'invited_at': date_utc
        }
    }
    db.update(lookup,payload)