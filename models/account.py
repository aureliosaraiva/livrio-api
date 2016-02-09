# -*- coding: utf-8 -*-
from settings import db
from datetime import datetime
from bson.objectid import ObjectId
from util import legacy, token, fb, s3, google
import time
import base64
import notification
from tasks import schedule


#@slow
#@bugfix - cover sendo salvo e não apagado o anterior
def save_cover(account_id, source):
    try:
        filename = 'user/' + str(account_id) + '/cover_' + str(int(time.time())) + '.jpg'
        path = s3.upload_from_string(base64.b64decode(source),filename,content_type="image/jpg")
        if path:
            db.accounts.update_one({'_id':account_id}, {'$set': {'cover':path},'$addToSet':{'covers_list': path}})
    except:
        pass

#@slow
#@bugfix - cover sendo salvo e não apagado o anterior
def save_photo(account_id, source):
    try:
        filename = 'user/' + str(account_id) + '/photo_' + str(int(time.time())) + '.jpg'
        path = s3.upload_from_string(base64.b64decode(source),filename,content_type="image/jpg")
        if path:
            db.accounts.update_one({'_id':account_id}, {'$set': {'photo':path},'$push':{'photos_list': {'type':'upload','link':path}}})
    except:
        pass


def create(data):
    date_utc = datetime.utcnow().replace(microsecond=0)

    payload = {
        '_created': date_utc,
        '_updated': date_utc,
        '_deleted': False,
        'amount_books': 0,
        'amount_friends': 0,
        'auth': {

        }
    }

    accept = ['fullname','last_name','first_name','gender','phone','email','facebook','device_token','device']
    for i in accept:
        if i in data:
            payload[i] = data[i]

    db.accounts.insert_one(payload)

    # Notificação
    notification.notify(
        friend_id=payload['_id'], 
        group=notification.TYPE['SYSTEM_WELCOME'])

    schedule.send_mail(payload['_id'],'signup')


    return payload


def login_facebook(access_token):
    data = fb.profile(access_token)
    email = data['email']

    doc = db.accounts.find_one({'email':email}, {'auth': 1})

    if not doc:
        data['facebook'] = {
            'token': access_token,
            'user_id': data['id']
        }
        doc = create(data)


    return doc



#@bugfix melhorar logica
def login(email=None, password=None, access_token=None):
    if not access_token:
        doc = db.accounts.find_one({'email':email}, {'auth': 1})
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

    db.accounts.update_one(lookup,payload)

    return {
        'token': _token,
        '_id': doc['_id']
    }

def logout(account_id):

    lookup = {'_id':account_id}

    
    payload = {
        '$set': {
            'auth.token': None
        }
    }
    db.accounts.update_one(lookup,payload)



#@bug tratar data
def account_device(account_id, data):

    lookup = {'_id':account_id}
    doc = db.find_one(lookup)

    payload = {
        '$set': {
            'device_token': data
        }
    }
    db.accounts.update_one(lookup,payload)


#@bug tratar data
def account_update(account_id, data):
    lookup = {'_id':account_id}
    doc = db.accounts.find_one(lookup)

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
        schedule.search_location(account_id)

    if payload_data:
        payload = {
            '$set': payload_data
        }
        db.accounts.update_one(lookup,payload)

    if 'cover_source' in data:
        save_cover(account_id, data['cover_source'])

    if 'avatar_source' in data:
        save_photo(account_id, data['avatar_source'])

        


#@bug tratar data
def account_info(account_id):
    lookup = {'_id':account_id}
    doc = db.accounts.find_one(lookup,{
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
    if multi:
        lookup = {'_id':{'$in':account_id}}
        cursor = db.accounts.find(lookup,{'fullname':1,'first_name':1,'last_name':1,'photo':1})
        users = {}
        for doc in cursor:
            if not 'photo' in doc:
                doc['photo'] = 'img/avatar.png'
            users[doc['_id']] = doc
        return users
    

    lookup = {'_id':account_id}

    doc = db.accounts.find_one(lookup,{'fullname':1,'first_name':1,'last_name':1,'photo':1,'friends_list':1})

    if 'friends_list' in doc and friend_id in doc['friends_list']:
        doc['is_friend'] = True
    if 'friends_list' in doc:
        del doc['friends_list']

    if not 'photo' in doc:
        doc['photo'] = 'img/avatar.png'

    return doc


def update_location(account_id):
    doc = db.accounts.find_one(account_id)

    if 'location' in doc and 'latitude' in doc['location'] and 'longitude' in doc['location']:
        payload = doc['location']
        location = google.get_location(doc['location']['latitude'], doc['location']['longitude'])
        payload.update(location)
        db.accounts.update_one({'_id':account_id},{'$set':{'location': payload}})

