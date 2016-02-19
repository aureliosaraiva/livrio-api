# -*- coding: utf-8 -*-


from event import profile, register
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
    register('signup',doc['_id'], timer=doc['_created'], retro=True)

    cursor_book = db.books.find({'account_id': doc['_id']})
    for book in cursor_book:
        register('book_create',doc['_id'], book_id=book['_id'], timer=book['_created'], retro=True)

    cursor_events = db.events.find({'account_id': doc['_id']})
    for evt in cursor_events:
        if 'like' in evt:
            register('book_like',doc['_id'], book_id=evt['book_id'], timer=evt['_created'], retro=True)
        elif 'book_view' in evt:
            register('book_view',doc['_id'], book_id=evt['book_id'], timer=evt['_created'], retro=True)
        elif 'friend_view' in evt:
            register('friend_view',doc['_id'], friend_id=evt['friend_id'],  timer=evt['_created'], retro=True)


    i += 1

    # event_track.track_import(str(doc['_id']), 'signup',sec)

