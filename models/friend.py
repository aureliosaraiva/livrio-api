# -*- coding: utf-8 -*-
from settings import db, DEFAULT
from datetime import datetime
from bson.objectid import ObjectId
import notification
import account


def inc_amount_friend(account_id):
    lookup = {'_id':account_id}
    db.accounts.update_one(lookup,{'$inc':{'amount_friends':1}})
def decr_amount_friend(account_id):
    lookup = {'_id':account_id}
    db.accounts.update_one(lookup,{'$inc':{'amount_friends':-1}});

def friend(account_id, friend_id):
    lookup = {
        '_id': friend_id
    }




    doc = db.accounts.find_one(lookup,{'fullname':1,'photo':1,'cover':1,'amount_books':1,'first_name':1,'last_name':1,'location':1,'friends_list':1,'invited_friends':1})

    if 'friends_list' in doc and account_id in doc['friends_list']:
        doc['is_friend'] = True

    if 'friends_list' in doc:
        del doc['friends_list']

    if 'location' in doc:
        if 'state' in doc['location']:
            doc['state'] = doc['location']['state']
        if 'city' in doc['location']:
            doc['city'] = doc['location']['city']

        del doc['location']

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
        doc['photo'] = DEFAULT['user']

    if not 'cover' in doc:
        doc['cover'] = DEFAULT['cover']

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


    doc = db.accounts.find_one(lookup)

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

    db.accounts.update_one({'_id': account_id},payload)

    payload = {
        '$push':{
            'invited_friends_pending': {
                '_created': date_utc,
                'account_id': account_id
            }
        }
    }

    db.accounts.update_one({'_id': friend_id},payload)

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


    doc = db.accounts.find_one(lookup)

    if not doc:
        return None

    lookup = { '_id': friend_id }
    payload = {'$pull':{'invited_friends_pending':{'account_id':account_id}}}
    db.accounts.update_one(lookup,payload)

    lookup = { '_id': account_id }
    payload = { '$pull':{'invited_friends':{'account_id':friend_id}}}
    db.accounts.update_one(lookup,payload)
    notification.notify_request_friend_delete(account_id,friend_id)
    decr_amount_friend(account_id)
    decr_amount_friend(friend_id)


#@task registrar na tabela de eventos a data do aceite
#@task enviar push e email informando que o usuário aceitou o convite
def friend_invite_accept(account_id, friend_id):

    if account_id == friend_id:
        return None

    lookup = {
        '_id': account_id,
        "invited_friends_pending.account_id":  friend_id 
    }


    doc = db.accounts.find_one(lookup)

    if not doc:
        return None

    lookup = { '_id': account_id }
    payload = { '$addToSet':{'friends_list': friend_id},'$pull':{'invited_friends_pending':{'account_id':friend_id}}}
    db.accounts.update_one(lookup,payload)

    lookup = { '_id': friend_id }
    payload = { '$addToSet':{'friends_list': account_id},'$pull':{'invited_friends':{'account_id':account_id}}}
    db.accounts.update_one(lookup,payload)

    inc_amount_friend(account_id)
    inc_amount_friend(friend_id)

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

    doc = db.accounts.find_one(lookup)

    if not doc:
        return None

    lookup = { '_id': account_id }
    payload = {'$pull':{'invited_friends_pending':{'account_id':friend_id}}}
    db.accounts.update_one(lookup,payload)

    lookup = { '_id': friend_id }
    payload = { '$pull':{'invited_friends':{'account_id':account_id}}}
    db.accounts.update_one(lookup,payload)



def friend_suggest(account_id, params=None):
    lookup = {
        'account_id': account_id
    }

    if params:
        if 'search' in params:
            lookup["$text"] = { '$search': params['search'] }


    cursor = db.friend_suggests.find(lookup,{ 'fullname':1,'score': { '$meta': "textScore" } }).sort([('score', { '$meta': "textScore" } )])

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


    cursor = db.accounts.find(lookup,{ 'fullname':1, 'first_name':1, 'last_name':1,'amount_books':1,'photo':1, 'score': { '$meta': "textScore" } }).sort([('score', { '$meta': "textScore" } )])

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
            doc['photo'] = DEFAULT['user']

        d.append(doc)

    return d

def friend_all(account_id, params=None):
    lookup = { '_id': account_id }

    doc = db.accounts.find_one(lookup,{ 'friends_list':1})
    if not 'friends_list' in doc:
        return []
    
    lookup = { '_id': {'$in':doc['friends_list']} }
    cursor = db.accounts.find(lookup,{ 'fullname':1,'photo':1,'amount_books':1})

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
            document['photo'] = DEFAULT['user']

        document['is_friend'] = True
        d.append(document)



    return d

def delete(account_id, friend_id):

    db.accounts.update_one({'_id': account_id},{'$pull':{'friends_list':friend_id}})
    db.accounts.update_one({'_id': friend_id},{'$pull':{'friends_list':account_id}})
