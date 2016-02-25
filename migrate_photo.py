# -*- coding: utf-8 -*-
from pymongo import MongoClient
import re
from tasks import schedule
regx = re.compile("livrio-stoatic")

MONGO_DB = "mongodb://db.codeway.in:4455"
MONGO_DB = "mongodb://db.codeway.in:27017"



mongo_client = MongoClient(MONGO_DB)
db = mongo_client.livrio


cursor = db.accounts.find({'photo':{'$not':regx}},{'photo':1}).limit(10)

for doc in cursor:

    schedule.download_photo_account(doc['_id'],doc['photo'])
    
