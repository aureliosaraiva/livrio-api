# -*- coding: utf-8 -*-
from __future__ import absolute_import
from eve import Eve, render
from flask import current_app as app, request, abort
from eve.methods.post import post_internal
from util import search_isbn, google
from models import isbn
from settings import EVE_SETTINGS_ISBN
import json
from tasks import schedule

app = Eve(__name__, settings=EVE_SETTINGS_ISBN)

@app.route('/v1/search',methods=['GET'])
def route_search():
    result = isbn.search(request.args)
    data = {
        '_status': 'OK',
        '_items': result
    }
    return render.render_json(data), 200, {'Content-Type': 'application/json; charset=utf-8'}

def evt_isbn_pre_get(request, lookup):
    isbn_10 = None
    isbn = lookup['isbn']
    if len(isbn) == 10:
        isbn_10 = isbn
        isbn = '978' + isbn


    lookup = { 'isbn': isbn}

    if isbn_10:
        lookup = {
            '$or': [
                { 'isbn_10': isbn_10},
                { 'isbn': isbn}
            ]
        }

    print lookup
    
    book = app.data.driver.db['isbn'].find_one(lookup)
    if book:
        return book

    payload = search_isbn.find_isbn_amazon(isbn)

    if not payload:
        payload = google.search_books(isbn, limit=1)

    if not payload:
        return None

    if not 'isbn' in payload and 'isbn_10' in payload:
        payload['isbn'] = '978' + payload['isbn_10']

    if not 'cover' in payload:
        payload['cover'] = 'https://livrio-static.s3-sa-east-1.amazonaws.com/default/book.gif'




    post_internal('isbn', payload, True)

    schedule.download_cover_book_isbn(payload['_id'], payload['isbn'], payload['cover'])



def evt_isbn_post_get(request, payload):
    data = json.loads(payload.get_data())

    if not 'cover' in data:
        data['cover'] = 'img/cover.gif'

    payload.set_data(json.dumps(data))

app.on_pre_GET_isbn += evt_isbn_pre_get
app.on_post_GET_isbn += evt_isbn_post_get
if __name__ == '__main__':
    app.run()
