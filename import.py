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
import urllib2

DATABASE = {'host': 'mysql01.codeway.com.br', 'user': 'CodeWay_Livrio', 'pass': 'vqtIeyYfohR7fjE4', 'base': 'CodeWay_Livrio'}
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
#MONGO_DB = "mongodb://db01.codeway.com.br:4455"
MONGO_DB = "mongodb://db.codeway.in"

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


date_utc = datetime.utcnow().replace(microsecond=0)

def find_isbn(isbn):
    try:
        url = "http://127.0.0.1:5001/v1/book/{}".format(isbn)

        response = urllib2.urlopen(url)
        html = response.read()
        data = json.loads(html)
        if not '_id' in data:
            return False
        return data
    except:
        return False


isbn_list = []
for line in open("tmp/lourival.txt", 'r'):
    isbn = line.strip()
    doc = find_isbn(isbn)
    if doc:
        print "ISBN: {}, OK".format(isbn)
    else:
        print "ISBN: {}, ERR".format(isbn)