# -*- coding: utf-8 -*-
from settings import db
from datetime import datetime
from bson.objectid import ObjectId
import account
from util import s3
import base64
import notification
from tasks import schedule
import loan
import urllib

def inc_amount_book(account_id):
    lookup = {'_id':account_id}
    db.accounts.update_one(lookup,{'$inc':{'amount_books':1}})
def decr_amount_book(account_id):
    lookup = {'_id':account_id}
    db.accounts.update_one(lookup,{'$inc':{'amount_books':-1}})

def get_by_isbn(account_id, isbn):
    lookup = {'account_id':account_id,'isbn':isbn}
    doc = db.books.find_one(lookup);
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
    
    return db.isbn.find_one(lookup)

#@slow
def save_cover(book_id, isbn, source):
    try:
        path = s3.upload_from_string(base64.b64decode(source),'cover/'+str(isbn)+'/' + str(book_id) + '.jpg',content_type="image/jpg")
        if path:
            db.books.update_one({'_id':book_id}, {'$set': {'cover':path}})
    except:
        pass



def save(account_id, data, book_id=None):

    date_utc = datetime.utcnow().replace(microsecond=0)

    if 'isbn' in data and not book_id:
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

        accept = ['title','isbn','publisher', 'published_date','authors','description','page_count','shelves','draft','subtitle','cover']
        for i in accept:
            if i in data:
                payload[i] = data[i]

        db.books.insert_one(payload)
        inc_amount_book(account_id)
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

        db.books.update_one(lookup, {'$set': payload})


    if 'cover_source' in data:
        save_cover(book_id, data['isbn'], data['cover_source'])

    if 'cover' in data:
        schedule.download_cover_book(book_id, data['isbn'], data['cover'])

    return book_info(account_id, book_id)


#@bugfix possivel bug de ser executado duas vezes e descrementar duas vezes
def delete(account_id, book_id):
    lookup = {'_id': book_id,'account_id': account_id}
    db.books.update_one(lookup, {'$set': {'_deleted':True}})
    decr_amount_book(account_id)
    return True


#@bugfix melhorar logica
def book_search(account_id, params=None, friend_id=None):

    where = 'all'

    if 'where' in params:
        where = params['where']

    if 'friend' in params:
        friend_id = ObjectId(params['friend'])

    user = db.accounts.find_one({'_id':account_id})

    if not 'friends_list' in user:
        user['friends_list'] = []


    lookup = {}
    accounts_search = None

    if friend_id:
        accounts_search = [friend_id]
    elif where == 'friends':
        accounts_search = user['friends_list']
    elif where == 'my':
        accounts_search = [account_id]
    elif where == 'all':
        accounts_search = user['friends_list']
        accounts_search.append(account_id)
    elif where == 'my_loan':
        accounts_search = [account_id]
        lookup['loaned'] = { '$exists': True }
    elif where == 'other_loan':
       lookup['loaned'] = { '$exists': True}
       lookup['loaned._id'] = account_id
    else:
        accounts_search = [account_id]
  

    users = {}

    if accounts_search:
        lookup['account_id'] = {'$in': accounts_search}

        users = account.account_info_basic(accounts_search,True)
        

    if params:
        if 'search' in params:
            text = urllib.unquote(params['search']).decode('utf8') 
            lookup["$text"] = { '$search': text }

        if 'shelves' in params:
            lookup['shelves'] = {'$in':[params['shelves']]}

    lookup['_deleted'] = False

    print lookup
    
    # ensureIndex({ title: "text", subtitle : "text", isbn : "text",publisher: "text",description:"text",authors:"text" });
    cursor = db.books.find(lookup,{ 'title':1,'authors':1,'account_id':1,'cover':1,'shelves':1,'isbn':1,'page_count':1,'published_date':1,'publisher':1,'loaned':1,'score': { '$meta': "textScore" } }).sort([('score', { '$meta': "textScore" } )])

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
        if document['account_id'] in users:
            document['owner'] = users[document['account_id']]
        else:
            document['owner'] = account.account_info_basic(document['account_id'])

        if document['account_id'] == account_id:
            document['is_owner'] = True

        del document['account_id']
        d.append(document)

    return d

def book_like(account_id, book_id, unlike=False):

    lookup = {'_id': book_id}


    book = db.books.find_one(lookup)

    if not book:
        return None

    date_utc = datetime.utcnow().replace(microsecond=0)
    if not ('likes' in book and account_id in book['likes']):
        db.event_like.insert_one({
            'book_id': book_id,
            'like': True,
            'account_id': account_id,
            '_created': date_utc
        })

        db.books.update_one(lookup, {'$addToSet':{'likes': account_id}}, upsert=False)

        # Notificação
        notification.notify(
            account_id=account_id, 
            friend_id=book['account_id'], 
            book_id=book_id, 
            group=notification.TYPE['FRIEND_LIKE_BOOK'])

        
    elif unlike and 'likes' in book and account_id in book['likes']:
        db.event_like.insert_one({
            'book_id': book_id,
            'unlike': True,
            'account_id': account_id,
            '_created': date_utc
        })

        db.books.update_one(lookup, {'$pull':{'likes': account_id}}, upsert=False)

    return True


def book_unlike(account_id, book_id):
    return book_like(account_id, book_id, True)

def book_is_like(account_id, book_id):
    lookup = {'_id': book_id}
    book = db.books.find_one(lookup)

    if not book:
        return None

    return 'likes' in book and account_id in book['likes']



def book_get_comment(book_id):
    lookup = {'_id': book_id, '_deleted': False}
    doc = db.books.find_one(lookup,{'comments':1})

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

    date_utc = datetime.utcnow().replace(microsecond=0)
    payload = {
        '_id': ObjectId(),
        'account_id': account_id,
        'message': comment,
        '_created': date_utc,
        '_updated': date_utc,
        '_deleted': False
    }
    db.books.update_one(lookup, {'$push':{'comments': payload}}, upsert=False)
    payload['owner'] = account.account_info_basic(account_id)
    return payload


#@bug tratar data
def book_info(account_id, book_id):
    lookup = {'_id':book_id}
    doc = db.books.find_one(lookup,{
        'title':1,    
        'isbn':1,
        'cover':1,
        'authors':1,
        'publisher':1,
        'account_id': 1,
        'loan_id': 1,
        'page_count':1,
        'published_date':1,
        'description':1,
        'shelves': 1,
        'loaned': 1,
        'likes':1
    })

    if not 'cover' in doc:
        doc['cover'] = 'https://livrio-static.s3-sa-east-1.amazonaws.com/default/book.png'


    doc['owner'] = account.account_info_basic(doc['account_id'], friend_id=account_id)

    if 'likes' in doc and account_id in doc['likes']:
        del doc['likes']
        doc['is_like'] = True

    if account_id == doc['account_id']:
        doc['is_owner'] = True
        del doc['account_id']


    return doc

def book_recommend(account_id, friend_id, book_id):
    notification.notify(
        account_id=account_id, 
        friend_id=friend_id, 
        book_id=book_id, 
        group=notification.TYPE['FRIEND_RECOMMEND_BOOK'])

def download_cover(book_id, isbn, url):
    try:
        import md5
        isbn = md5.new(isbn + 'E4+eU!BLS&h69^U5GxM@j5!3NnbZQ').hexdigest()
        filename = 'book/' + str(isbn) + '/front.jpg'
        path = s3.upload_from_url(url,filename,content_type="image/jpg")
        if path:
            db.books.update_one({'_id':book_id}, {'$set': {'cover':path}})
    except Exception, e:
        pass

def download_cover_isbn(isbn_id, isbn, url):
    try:
        import md5
        isbn = md5.new(isbn + 'E4+eU!BLS&h69^U5GxM@j5!3NnbZQ').hexdigest()
        filename = 'book/' + str(isbn) + '/front.jpg'
        path = s3.upload_from_url(url,filename,content_type="image/jpg")
        if path:
            db.isbn.update_one({'_id':isbn_id}, {'$set': {'cover':path}})
    except Exception, e:
        pass