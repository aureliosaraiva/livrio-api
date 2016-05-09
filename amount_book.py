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


MONGO_DB = "mongodb://db.codeway.in:4455"
# MONGO_DB = "mongodb://db.codeway.in:27017"



mongo_client = MongoClient(MONGO_DB)
db = mongo_client.livrio


cursor = db.accounts.find({})

for doc in cursor:

    count = db.books.find({'account_id':doc['_id']}).count()

    db.accounts.update({'_id': doc['_id'] },{'$set':{'amount_books': count}})
