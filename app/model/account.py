# -*- coding: utf-8 -*-
from flask import current_app as app
from datetime import datetime
from bson.objectid import ObjectId
from util import legacy
from util import token
from util import fb
import time
from util import s3
import base64

#@slow
#@bugfix - cover sendo salvo e não apagado o anterior
def save_cover(account_id, source):
    try:
        filename = 'user/' + str(account_id) + '/cover_' + str(int(time.time())) + '.jpg'
        path = s3.upload_from_string(base64.b64decode(source),filename,content_type="image/jpg")
        if path:
            db = app.data.driver.db['accounts']
            db.update_one({'_id':account_id}, {'$set': {'cover':path},'$addToSet':{'covers_list': path}})
    except:
        pass

#@slow
#@bugfix - cover sendo salvo e não apagado o anterior
def save_photo(account_id, source):
    try:
        filename = 'user/' + str(account_id) + '/photo_' + str(int(time.time())) + '.jpg'
        path = s3.upload_from_string(base64.b64decode(source),filename,content_type="image/jpg")
        if path:
            db = app.data.driver.db['accounts']
            db.update_one({'_id':account_id}, {'$set': {'photo':path},'$push':{'photos_list': {'type':'upload','link':path}}})
    except:
        pass


def create(data):
    db = app.data.driver.db['accounts']
    date_utc = datetime.utcnow().replace(microsecond=0)

    payload = {
        '_created': date_utc,
        '_updated': date_utc,
        '_deleted': False,
        'auth': {

        }
    }

    accept = ['fullname','last_name','first_name','gender','phone','email','facebook','device_token','device']
    for i in accept:
        if i in data:
            payload[i] = data[i]

    db.insert_one(payload)
    return payload


def login_facebook(access_token):
    data = fb.profile(access_token)
    email = data['email']

    db = app.data.driver.db['accounts']
    doc = db.find_one({'email':email}, {'auth': 1})

    if not doc:
        data['facebook'] = {
            'token': access_token,
            'user_id': data['id']
        }
        doc = create(data)


    return doc



#@bugfix melhorar logica
def login(email=None, password=None, access_token=None):
    db = app.data.driver.db['accounts']
    if not access_token:
        doc = db.find_one({'email':email}, {'auth': 1})
    else:
        doc = login_facebook(access_token)

    
    auth = doc['auth']

    if 'mode' in auth and auth['mode'] == 'php' and password:
        if not legacy.password_php(password, auth['password_php']):
            return False

    _token = token.create()
    lookup = {'_id':doc['_id']}
    
    payload = {
        '$set': {
            'auth.token': _token
        }
    }

    db.update_one(lookup,payload)

    return {
        'token': _token,
        '_id': doc['_id']
    }

def logout(account_id):
    db = app.data.driver.db['accounts']
    lookup = {'_id':account_id}
    doc = db.find_one(lookup)
    
    payload = {
        '$set': {
            'auth.token': None
        }
    }
    db.update_one(lookup,payload)



#@bug tratar data
def account_device(account_id, data):
    db = app.data.driver.db['accounts']
    lookup = {'_id':account_id}
    doc = db.find_one(lookup)

    payload = {
        '$set': {
            'device_token': data
        }
    }
    db.update_one(lookup,payload)


#@bug tratar data
def account_update(account_id, data):
    db = app.data.driver.db['accounts']
    lookup = {'_id':account_id}
    doc = db.find_one(lookup)

    payload_data = {}

    if 'fullname' in data:
        data['first_name'], data['last_name'] = data['fullname'].split(' ',1)

    accept = ['device_token','config','fullname','last_name','first_name','gender','phone']

    for i in accept:
        if i in data:
            payload_data[i] = data[i]

    if 'birthday' in data:
        try:
            payload_data['birthday'] = datetime.strptime(str(data['birthday']),'%Y-%m-%d')
        except:
            pass
    
    if 'state' in data:
        payload_data['location.state'] = data['state']

    if 'city' in data:
        payload_data['location.city'] = data['city']

    if 'location' in data:
        l = data['location'].split(',')
        payload_data['location.latitude'] = l[0]
        payload_data['location.longitude'] = l[1]

    if payload_data:
        payload = {
            '$set': payload_data
        }
        db.update_one(lookup,payload)

    if 'cover_source' in data:
        save_cover(account_id, data['cover_source'])

    if 'avatar_source' in data:
        save_photo(account_id, data['avatar_source'])

        


#@bug tratar data
def account_info(account_id):
    db = app.data.driver.db['accounts']
    lookup = {'_id':account_id}
    doc = db.find_one(lookup,{
        'first_name':1,
        'last_name':1,
        'email':1,
        'gender':1,
        'birthday':1,
        'photo':1,
        'cover':1,
        'fullname':1,
        'config': 1
    })

    if not 'photo' in doc:
        doc['photo'] = 'img/avatar.png'

    if not 'cover' in doc:
        doc['cover'] = 'img/bg.jpg'

    if not 'config' in doc:
        doc['config'] = {'allowSearchEmail':True,'allowLocation':False,'allowNotificationPush':True,'allowNotificationEmail':True}

    # if 'birthday' in doc:
    #     doc['birthday'] = 'img/avatar.png'
   

    return doc


def account_info_basic(account_id, multi=False, friend_id=None):
    db = app.data.driver.db['accounts']
    if multi:
        lookup = {'_id':{'$in':account_id}}
        cursor = db.find(lookup,{'fullname':1,'first_name':1,'last_name':1,'photo':1})
        users = {}
        for doc in cursor:
            if not 'photo' in doc:
                doc['photo'] = 'img/avatar.png'
            users[doc['_id']] = doc
        return users
    

    lookup = {'_id':account_id}

    doc = db.find_one(lookup,{'fullname':1,'first_name':1,'last_name':1,'photo':1,'friends_list':1})

    if 'friends_list' in doc and friend_id in doc['friends_list']:
        doc['is_friend'] = True
    
    del doc['friends_list']

    if not 'photo' in doc:
        doc['photo'] = 'img/avatar.png'

    return doc
