# -*- coding: utf-8 -*-
from flask import current_app as app
from datetime import datetime
from bson.objectid import ObjectId
import notification
import account




def friend(account_id, friend_id):
    lookup = {
        '_id': friend_id
    }

    db = app.data.driver.db['accounts']

    doc = db.find_one(lookup,{'fullname':1,'photo':1,'cover':1,'first_name':1,'last_name':1,'location':1,'friends_list':1,'invited_friends':1})

    if 'friends_list' in doc and account_id in doc['friends_list']:
        doc['is_friend'] = True

    if 'invited_friends' in doc:
        for i in doc['invited_friends']:
            if i['account_id'] == account_id:
                doc['invited'] = {
                    'id': doc['_id'],
                    'fullname': doc['fullname'],
                    'photo': doc['photo']
                }
                break

    if not 'photo' in doc:
        doc['photo'] = 'img/avatar.png'

    if not 'cover' in doc:
        doc['cover'] = 'img/bg.jpg'

    return doc

#@bugfix verificar se o usuário convidado existe e se está removido
#@task enviar email e notificação
#@task enviar push de notificação
#@bugfix verificar se o usuário ja é amigo
def friend_invite(account_id, friend_id):

    if account_id == friend_id:
        return None

    lookup = {
        '_id': account_id,
        "invited_friends.account_id": { '$ne': friend_id }
    }

    db = app.data.driver.db['accounts']

    doc = db.find_one(lookup)

    if not doc:
        return None

    date_utc = datetime.utcnow().replace(microsecond=0)
    payload = {
        '$push':{
            'invited_friends': {
                '_created': date_utc,
                'account_id': friend_id
            }
        }
    }

    db.update_one({'_id': account_id},payload)

    payload = {
        '$push':{
            'invited_friends_pending': {
                '_created': date_utc,
                'account_id': account_id
            }
        }
    }

    db.update_one({'_id': friend_id},payload)

    # Notificação
    notification.notify(
        account_id=account_id, 
        friend_id=friend_id,
        group=notification.TYPE['REQUEST_FRIEND'])

#@task registrar na tabela de eventos a data do aceite
#@task enviar push e email informando que o usuário aceitou o convite
def friend_invite_delete(account_id, friend_id):

    if account_id == friend_id:
        return None

    lookup = {
        '_id': account_id,
        "invited_friends.account_id":  friend_id 
    }

    db = app.data.driver.db['accounts']

    doc = db.find_one(lookup)

    if not doc:
        return None

    lookup = { '_id': friend_id }
    payload = {'$pull':{'invited_friends_pending':{'account_id':account_id}}}
    db.update_one(lookup,payload)

    lookup = { '_id': account_id }
    payload = { '$pull':{'invited_friends':{'account_id':friend_id}}}
    db.update_one(lookup,payload)
    notification.notify_request_friend_delete(account_id,friend_id)


#@task registrar na tabela de eventos a data do aceite
#@task enviar push e email informando que o usuário aceitou o convite
def friend_invite_accept(account_id, friend_id):

    if account_id == friend_id:
        return None

    lookup = {
        '_id': account_id,
        "invited_friends_pending.account_id":  friend_id 
    }

    db = app.data.driver.db['accounts']

    doc = db.find_one(lookup)

    if not doc:
        return None

    lookup = { '_id': account_id }
    payload = { '$addToSet':{'friends_list': friend_id},'$pull':{'invited_friends_pending':{'account_id':friend_id}}}
    db.update_one(lookup,payload)

    lookup = { '_id': friend_id }
    payload = { '$addToSet':{'friends_list': account_id},'$pull':{'invited_friends':{'account_id':account_id}}}
    db.update_one(lookup,payload)

    # Notificação
    notification.notify(
        account_id=account_id, 
        friend_id=friend_id, 
        group=notification.TYPE['FRIEND'])

#@task registrar na tabela de eventos a data do aceite
#@task enviar push e email informando que o usuário aceitou o convite
def friend_invite_cancel(account_id, friend_id):

    if account_id == friend_id:
        return None

    lookup = {
        '_id': account_id,
        "invited_friends_pending.account_id":  friend_id 
    }

    db = app.data.driver.db['accounts']

    doc = db.find_one(lookup)

    if not doc:
        return None

    lookup = { '_id': account_id }
    payload = {'$pull':{'invited_friends_pending':{'account_id':friend_id}}}
    db.update_one(lookup,payload)

    lookup = { '_id': friend_id }
    payload = { '$pull':{'invited_friends':{'account_id':account_id}}}
    db.update_one(lookup,payload)



def friend_suggest(account_id, params=None):
    lookup = {
        'account_id': account_id
    }

    if params:
        if 'search' in params:
            lookup["$text"] = { '$search': params['search'] }

    db = app.data.driver.db['friend_suggests']
    cursor = db.find(lookup,{ 'fullname':1,'score': { '$meta': "textScore" } }).sort([('score', { '$meta': "textScore" } )])

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

def friend_search(account_id, params=None):
    lookup = {
        "$and": [ 
            {'_id': {'$nin': [account_id]}},
            {'friends_list': { '$nin': [account_id]}}
        ]
    }

    if params:
        if 'search' in params:
            lookup["$text"] = { '$search': params['search'] }

    accounts = app.data.driver.db['accounts']
    cursor = accounts.find(lookup,{ 'fullname':1, 'first_name':1, 'last_name':1,'photo':1, 'score': { '$meta': "textScore" } }).sort([('score', { '$meta': "textScore" } )])

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
    for doc in cursor:

        if not 'photo' in doc:
            doc['photo'] = 'img/avatar.png'

        d.append(doc)

    return d

def friend_all(account_id, params=None):
    lookup = { '_id': account_id }

    accounts = app.data.driver.db['accounts']
    doc = accounts.find_one(lookup,{ 'friends_list':1})
    print doc

    lookup = { '_id': {'$in':doc['friends_list']} }

    print lookup

    accounts = app.data.driver.db['accounts']
    cursor = accounts.find(lookup,{ 'fullname':1,'photo':1})

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
        if not 'photo' in document:
            document['photo'] = 'img/avatar.png'

        d.append(document)

    return d

def delete(account_id, friend_id):
    db = app.data.driver.db['accounts']

    db.update_one({'_id': account_id},{'$pull':{'friends_list':friend_id}})
    db.update_one({'_id': friend_id},{'$pull':{'friends_list':account_id}})
