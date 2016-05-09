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
from math  import ceil

DATABASE = {'host': 'mysql01.codeway.com.br', 'user': 'CodeWay_Livrio', 'pass': 'vqtIeyYfohR7fjE4', 'base': 'CodeWay_Livrio'}
# DATABASE = {'host': 'localhost', 'user': 'root', 'pass': '', 'base': 'CodeWay_Livrio'}
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
MONGO_DB = "mongodb://db.codeway.in:4455"

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
        return dict((k, remove_empty_from_dict(v)) for k, v in d.iteritems()  if type(v) is bool or (v and remove_empty_from_dict(v)))
    elif type(d) is list:
        return [remove_empty_from_dict(v) for v in d  if type(v) is bool or (v and remove_empty_from_dict(v))]
    else:
        return d

def set_id(o,i,id):
    redis_client.set(o + ':'+str(i),id)

def get_id(o,i):
    return ObjectId(redis_client.get(o + ':'+str(i)))


db.phone_contacts.delete_many({})

date_utc = datetime.utcnow().replace(microsecond=0)

print "sys_contacts_phone"

offset = 0
query = "SELECT count(*) as total FROM sys_contacts_phone"
conn.execute(query)
result = conn.fetchone()

total = result['total']
page = int(ceil(total/5000))+1

for i in range(0, page):
    query = "SELECT * FROM sys_contacts_phone limit {},5000".format(i*5000)
    conn.execute(query)
    result = conn.fetchall()
    print "PAGE: " + str(i)
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