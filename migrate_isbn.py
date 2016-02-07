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
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
MONGO_DB = "mongodb://db.codeway.com.br:27017"

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


db.isbn.delete_many({})

date_utc = datetime.utcnow().replace(microsecond=0)


print "sys_isbns"
offset = 0
query = "SELECT count(*) as total FROM sys_isbns"
conn.execute(query)
result = conn.fetchone()

total = result['total']
page = ceil(total/5000)

for i in range(0, page):
    query = "SELECT * FROM sys_isbns limit {},5000".format(i*5000)
    conn.execute(query)
    result = conn.fetchall()
    print "PAGE: " + i
    for row in result:
        payload = {
            '_created': date_utc,
            '_updated': date_utc,
            '_deleted': False,
            'isbn': row['isbn'],
            'isbn_10': row['isbn_10'],
            'title': row['title'],
            'authors': row['author'],
            'description': row['description'],
            'cover': row['thumb'],
            'page_count': row['page_count'],
            'publisher': row['publisher'],
            'publishedDate': row['published_year'],
            'categories': [row['category']],
            'origin': {'name':row['origin'],'id':item['id']}
        }

        payload = remove_empty_from_dict(payload)

        if not 'isbn' in payload and 'isbn_10' in payload:
            payload['isbn'] = '978' + payload['isbn_10']

        db.isbn.insert_one(payload)


