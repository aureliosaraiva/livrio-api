# -*- coding: utf-8 -*-
from flask import current_app as app
from datetime import datetime
from bson.objectid import ObjectId
import account
from util import s3
import base64
import notification

def get_by_isbn(account_id, isbn):
    db = app.data.driver.db['books']
    lookup = {'account_id':account_id,'isbn':isbn}
    doc = db.find_one(lookup);
    if doc:
        return doc['_id'];

    return None


def search_isbn(isbn):
    if len(isbn) == 10:
        lookup['isbn'] = '978' + str(isbn)

    lookup = {
        '$or': [
            { 'isbn_10': isbn},
            { 'isbn': isbn}
        ]
    };
    
    return app.data.driver.db['isbn'].find_one(lookup)

#@slow
def save_cover(account_id, book_id, source):
    try:
        path = s3.upload_from_string(base64.b64decode(source),'cover/'+str(book_id)+'/front.jpg',content_type="image/jpg")
        if path:
            db = app.data.driver.db['books']
            db.update_one({'_id':book_id,'account_id':account_id}, {'$set': {'cover':path},'$push':{'covers_list': {'type':'upload','link':path}}})
    except:
        pass



def save(account_id, data, book_id=None):

    db = app.data.driver.db['books']
    date_utc = datetime.utcnow().replace(microsecond=0)

    if 'isbn' in data:
        book_id = get_by_isbn(account_id, data['isbn'])

    if not book_id:
        if 'isbn' in data:
            isbn_data = search_isbn(data['isbn'])
            if isbn_data:
                for i in isbn_data:
                    data[i] = isbn_data[i]

        payload = {
            '_created': date_utc,
            '_updated': date_utc,
            '_deleted': False,
            'account_id': account_id
        }

        accept = ['title','isbn','publisher', 'published_date','authors','description','page_count','shelves','draft','subtitle']
        for i in accept:
            if i in data:
                payload[i] = data[i]

        db.insert_one(payload)
        book_id = payload['_id']

    else:
        lookup = {'_id': book_id,'account_id': account_id}

        payload = {
            '_updated': date_utc,
            '_deleted': False
        }

        accept = ['title','isbn','publisher', 'published_date','authors','description','page_count','shelves','draft','subtitle']
        for i in accept:
            if i in data:
                payload[i] = data[i]

        db.update_one(lookup, {'$set': payload})


    if 'cover_source' in data:
        save_cover(book_id, data['cover_source'])

    return book_info(account_id, account_id, book_id)




#@bugfix melhorar logica
def book_search(account_id, params=None, friend_id=None):

    where = 'all'

    if 'where' in params:
        where = params['where']

    if 'friend' in params:
        friend_id = ObjectId(params['friend'])

    db = app.data.driver.db['accounts']
    user = db.find_one({'_id':account_id})


    if friend_id:
        accounts_search = [friend_id]
        lookup = {'account_id': friend_id}
    else:
        if where == 'friends':
            accounts_search = user['friends_list']
            lookup = {'account_id': {'$in': accounts_search}}  
        else:
            if where == 'my': 
                accounts_search = [account_id]
                lookup = {'account_id': account_id}
            else:
                accounts_search = user['friends_list']
                accounts_search.append(account_id)

            lookup = {'account_id': {'$in': accounts_search}}


    cursor = db.find({'_id': {'$in': accounts_search}},{'fullname':1})
    
    users = {}
    for i in cursor:
        users[i['_id']] = i

    if params:
        if 'search' in params:
            lookup["$text"] = { '$search': params['search'] }

        if 'shelves' in params:
            lookup['shelves'] = {'$in':[params['shelves']]}

    lookup['_deleted'] = False

    db = app.data.driver.db['books']
    cursor = db.find(lookup,{ 'title':1,'authors':1,'account_id':1,'cover':1,'shelves':1,'isbn':1,'page_count':1,'published_date':1,'publisher':1,'score': { '$meta': "textScore" } }).sort([('score', { '$meta': "textScore" } )])

    limit = 25
    offset = 0

    if 'limit' in params:
        limit = int(params['limit'])

    if 'offset' in params:
        offset = int(params['offset'])

    if offset > 0:
        offset = ((offset-1)*limit)

    cursor.skip(offset).limit(limit)

    d = []
    for document in cursor:
        document['owner'] = users[document['account_id']]

        if document['account_id'] == account_id:
            document['is_owner'] = True

        del document['account_id']
        d.append(document)

    return d

def book_like(account_id, book_id, unlike=False):

    lookup = {'_id': book_id}

    books = app.data.driver.db['books']

    book = books.find_one(lookup)

    if not book:
        return None

    if not ('likes' in book and account_id in book['likes']):
        date_utc = datetime.utcnow().replace(microsecond=0)
        event_like = app.data.driver.db['event_like']
        event_like.insert_one({
            'book_id': book_id,
            'like': True,
            'account_id': account_id,
            '_created': date_utc
        })

        books.update_one(lookup, {'$addToSet':{'likes': account_id}}, upsert=False)

        
    elif unlike and 'likes' in book and account_id in book['likes']:
        date_utc = datetime.utcnow().replace(microsecond=0)
        event_like = app.data.driver.db['event_like']
        event_like.insert_one({
            'book_id': book_id,
            'unlike': True,
            'account_id': account_id,
            '_created': date_utc
        })

        books.update_one(lookup, {'$pull':{'likes': account_id}}, upsert=False)

    return True


def book_unlike(account_id, book_id):
    return book_like(account_id, book_id, True)

def book_is_like(account_id, book_id):
    lookup = {'_id': book_id}
    books = app.data.driver.db['books']
    book = books.find_one(lookup)

    if not book:
        return None

    return 'likes' in book and account_id in book['likes']



def book_get_comment(book_id):
    lookup = {'_id': book_id, '_deleted': False}
    books = app.data.driver.db['books']
    doc = books.find_one(lookup,{'comments':1})

    if 'comments' in doc:

        accs = []
        for i in doc['comments']:
            accs.append(i['account_id'])

        users = account.account_info_basic(accs, True)

        for i in doc['comments']:
            i['owner'] = users[i['account_id']]

        return doc['comments']
    else:
        return []
        

#@bugfix pegar dados do usuário
def book_create_comment(account_id, book_id, comment):
    lookup = {'_id': book_id}
    books = app.data.driver.db['books']

    date_utc = datetime.utcnow().replace(microsecond=0)
    payload = {
        '_id': ObjectId(),
        'account_id': account_id,
        'message': comment,
        '_created': date_utc,
        '_updated': date_utc,
        '_deleted': False
    }
    books.update_one(lookup, {'$push':{'comments': payload}}, upsert=False)
    payload['owner'] = account.account_info_basic(account_id)
    return payload


#@bug tratar data
def book_info(account_id, book_id):
    db = app.data.driver.db['books']
    lookup = {'_id':book_id}
    doc = db.find_one(lookup,{
        'title':1,    
        'isbn':1,
        'cover':1,
        'authors':1,
        'publisher':1,
        'account_id': 1,
        'page_count':1,
        'published_date':1,
        'description':1,
        'shelves': 1,
        'likes':1
    })

    if not 'cover' in doc:
        doc['cover'] = 'img/cover.gif'


    doc['owner'] = account.account_info_basic(doc['account_id'])

    if 'likes' in doc and account_id in doc['likes']:
        del doc['likes']
        doc['is_like'] = True

    if account_id == doc['account_id']:
        doc['is_owner'] = True
        del doc['account_id']

    


    return doc

def book_recommend(account_id, friend_id, book_id):
    print 'book_recommend'
    notification.notify_recommend_book(account_id, friend_id, book_id)