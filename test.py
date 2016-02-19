# -*- coding: utf-8 -*-


from event import profile
from pymongo import MongoClient


MONGO_DB = "mongodb://db.codeway.in:4455"
# MONGO_DB = "mongodb://db.codeway.in:27017"


#int(datetime.utcnow().strftime('%s'))
mongo_client = MongoClient(MONGO_DB)
db = mongo_client.livrio


cursor = db.accounts.find({'_deleted':False},{'_created':1,'fullname':1,'email':1,'amount_books':1,'location':1,'gender':1,'amount_friends':1})
i = 0
for doc in cursor:
    print doc['_id']
    print i

    profile(doc['_id'])
    i += 1

    # event_track.track_import(str(doc['_id']), 'signup',sec)

