# -*- coding: utf-8 -*-
import MySQLdb, MySQLdb.cursors
import requests
import json
import redis
from pymongo import MongoClient
from datetime import datetime
from util import token
from bson import json_util
from bson.objectid import ObjectId

DATABASE = {'host': 'localhost', 'user': 'root', 'pass': '', 'base': 'CodeWay_Livrio'}
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
MONGO_DB = "mongodb://localhost:27017"

db = MySQLdb.connect(host=DATABASE['host'],
                     user=DATABASE['user'],
                     passwd=DATABASE['pass'],
                     db=DATABASE['base'],
                     charset='utf8',
                     use_unicode=True,
                     cursorclass=MySQLdb.cursors.DictCursor)

conn = db.cursor()


pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
redis_client = redis.Redis(connection_pool=pool)

mongo_client = MongoClient(MONGO_DB)
db = mongo_client.livrio

def to_datetime(date):
    return datetime.strptime(str(date),'%Y-%m-%d %H:%M:%S')
def to_date(str_):
    try:
        return datetime.strptime(str(str_),'%Y-%m-%d')
    except:
        return None

def decode_json(data):
    try:
        return json.loads(data)
    except:
        return {}

def to_str(s):
    if s:
        return s
    return ''

def remove_empty_from_dict(d):
    if type(d) is dict:
        return dict((k, remove_empty_from_dict(v)) for k, v in d.iteritems() if v and remove_empty_from_dict(v))
    elif type(d) is list:
        return [remove_empty_from_dict(v) for v in d if v and remove_empty_from_dict(v)]
    else:
        return d

def set_id(o,i,id):
    redis_client.set(o + ':'+str(i),id)

def get_id(o,i):
    return ObjectId(redis_client.get(o + ':'+str(i)))


db.accounts.delete_many({})
db.shelves.delete_many({})
db.phone_contacts.delete_many({})
db.events.delete_many({})
db.accounts_locations.delete_many({})
db.history_search.delete_many({})
db.isbn_not_founds.delete_many({})


date_utc = datetime.utcnow().replace(microsecond=0)

query = """SELECT * FROM sys_users"""
conn.execute(query)
result = conn.fetchall()
for row in result:
    payload = {
        '_created': to_datetime(row['registration']),
        '_updated': to_datetime(row['updated']),
        '_deleted': row['removed']==1,
        'first_name': row['first_name'],
        'last_name': row['last_name'],
        'fullname': row['first_name'] + ' '+ to_str(row['last_name']),
        'email': row['email'],
        'gender': row['gender'],
        'photo': row['photo'],
        'cover': row['cover'],
        'phone': row['phone'],
        'birthday': to_date(row['birthday']),
        'auth': {
            'password_php': row['password'],
            'mode':'php',
            'disabled': row['removed']==1
        },
        'location': {
            'latitude': row['latitude'],
            'longitude': row['longitude'],
            'city': row['city'],
            'state': row['state']
        },
        'facebook': {
            'user_id': row['facebook_id'],
            'token': row['token']
        },
        'last_access': decode_json(row['last_access']),
        'device_token': decode_json(row['push_tokens']),
        'device': {
            'platform': row['device'],
            'origin': row['origin'],
            'version': row['version_app']
        },
        'config': decode_json(row['config']),
        'old_id': row['id']
    }

    payload = remove_empty_from_dict(payload)

    db.accounts.insert_one(payload)
    set_id('user',row['id'],payload['_id'])


query = """SELECT * FROM sys_friends"""
conn.execute(query)
result = conn.fetchall()
for row in result:
    payload = {
        '$addToSet':{'friends_list': get_id('user',row['id_friend'])}
    }

    db.accounts.update_one({'_id': get_id('user',row['id_user'])}, payload)

query = """SELECT * FROM sys_shelfs"""
conn.execute(query)
result = conn.fetchall()
for row in result:
    payload = {
        '_created': date_utc,
        '_updated': date_utc,
        '_deleted': row['removed']==1,
        'name': row['name'],
        'old_id': row['id'],
        'account_id': get_id('user',row['id_created_by'])
    }

    payload = remove_empty_from_dict(payload)

    db.shelves.insert_one(payload)
    set_id('shelf',row['id'],payload['_id'])


query = """SELECT * FROM sys_books"""
conn.execute(query)
result = conn.fetchall()
for row in result:
    payload = {
        '_created': to_datetime(row['registration']),
        '_updated': to_datetime(row['updated']),
        '_deleted': row['removed']==1,
        'account_id': get_id('user',row['id_created_by']),
        'old_id': row['id'],
        'isbn': row['isbn'],
        'title': row['title'],
        'authors': row['author'],
        'description': row['description'],
        'cover': row['thumb'],
        'page_count': row['page_count'],
        'publisher': row['publisher'],
        'published_year': row['published_year']
    }

    payload = remove_empty_from_dict(payload)

    db.books.insert_one(payload)
    set_id('book',row['id'],payload['_id'])

query = """SELECT * FROM sys_book_shelfs"""
conn.execute(query)
result = conn.fetchall()
for row in result:
    payload = {
        '$addToSet': {'shelves': get_id('shelf',row['id_shelf'])}
    }

    db.books.update_one({'_id': get_id('book',row['id_book'])}, payload)


query = """SELECT * FROM sys_book_likes"""
conn.execute(query)
result = conn.fetchall()
for row in result:
    payload = {
        '$addToSet':{'likes': get_id('user',row['id_created_by'])}
    }

    db.books.update_one({'_id': get_id('book',row['id_book'])}, payload)

    db.events.insert_one({
            'book_id': get_id('book',row['id_book']),
            'like': True,
            'account_id': get_id('user',row['id_created_by']),
            '_created': to_datetime(row['registration'])
    })

query = """SELECT * FROM sys_book_comments"""
conn.execute(query)
result = conn.fetchall()
for row in result:
    payload = {
        '$push':{

            'comments': {
                '_id': ObjectId(),
                '_created': to_datetime(row['registration']),
                '_updated': to_datetime(row['registration']),
                'message': row['message'],
                '_deleted': False,
                'account_id': get_id('user',row['id_created_by'])
            }
        }
    }

    db.books.update_one({'_id': get_id('book',row['id_book'])}, payload)


query = """SELECT * FROM sys_contacts_phone"""
conn.execute(query)
result = conn.fetchall()
for row in result:

    item = decode_json(row['raw_contact'])
    lookup = {'account_id': get_id('user',row['id_created_by']), 'contact_id': item['id']}

    payload_data = {
        '_created': to_datetime(row['registration']),
        '_updated': to_datetime(row['updated']),
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

    payload_data = remove_empty_from_dict(payload_data)
    payload = {
        '$set': payload_data
    }

    db.phone_contacts.update_one(lookup,payload, upsert=True)


query = """SELECT * FROM sys_history"""
conn.execute(query)
result = conn.fetchall()
for row in result:
    if row['type'] == 'book':
        db.events.insert_one({
                'book_id': get_id('book',row['entity']),
                'book_view': True,
                'account_id': get_id('user',row['id_created_by']),
                '_created': to_datetime(row['registration'])
        })
    elif row['type'] == 'friend':
        db.events.insert_one({
                'friend_id': get_id('user',row['entity']),
                'friend_view': True,
                'account_id': get_id('user',row['id_created_by']),
                '_created': to_datetime(row['registration'])
        })


query = """SELECT * FROM sys_history_location"""
conn.execute(query)
result = conn.fetchall()
for row in result:
    db.accounts_locationsc.insert_one({
            'latitude': row['latitude'],
            'longitude': row['longitude'],
            'account_id': get_id('user',row['id_created_by']),
            '_created': to_datetime(row['registration'])
    })

query = """SELECT * FROM sys_history_search"""
conn.execute(query)
result = conn.fetchall()
for row in result:
    db.history_search.insert_one({
            'search': row['word'],
            'count_found': row['count_found'],
            'account_id': get_id('user',row['id_created_by']),
            '_created': to_datetime(row['registration'])
    })

query = """SELECT * FROM sys_isbns_not_found"""
conn.execute(query)
result = conn.fetchall()
for row in result:
    db.isbn_not_founds.insert_one({
            'isbn': row['isbn'],
            '_created': to_datetime(row['registration'])
    })