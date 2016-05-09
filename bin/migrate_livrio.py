# -*- coding: utf-8 -*-
from __future__ import absolute_import
import MySQLdb, MySQLdb.cursors
import requests
import json
import redis
from pymongo import MongoClient
import datetime
from util import token
from bson import json_util
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

def to_datetime(str_):
    return datetime.strptime(str_,'%Y-%m-%d %H:%M:%S')
def to_date(str_):
    try:
        return datetime.datetime.strptime(str_,'%Y-%m-%d')
    except:
        return None

def decode_json(data):
    try:
        return json.loads(data)
    except:
        return {}


def remove_empty_from_dict(d):
    if type(d) is dict:
        return dict((k, remove_empty_from_dict(v)) for k, v in d.iteritems() if v and remove_empty_from_dict(v))
    elif type(d) is list:
        return [remove_empty_from_dict(v) for v in d if v and remove_empty_from_dict(v)]
    else:
        return d

query = """SELECT * FROM sys_users limit 1"""
conn.execute(query)
result = conn.fetchall()
for row in result:
    payload = {
        '_created': to_datetime(row['registration']),
        '_updated': to_datetime(row['updated']),
        '_deleted': row['removed']==1,
        'first_name': row['first_name'],
        'last_name': row['last_name'],
        'fullname': row['first_name'] + ' '+ row['last_name'],
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
        'config': decode_json(row['config'])

    }

    print db.accounts.insert_one(payload)

    