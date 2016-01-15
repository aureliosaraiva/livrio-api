# -*- coding: utf-8 -*-
from __future__ import absolute_import
from eve import Eve
from flask import current_app as app
from eve.methods.post import post_internal
from util import search_isbn
from settings import EVE_SETTINGS_ISBN

app = Eve(__name__, settings=EVE_SETTINGS_ISBN)


def evt_isbn_pre_get(request, lookup):
    if len(lookup['isbn']) == 10:
        lookup['isbn'] = '978' + lookup['isbn']

    isbn = lookup['isbn']

    lookup = {
        '$or': [
            { 'isbn_10': isbn},
            { 'isbn': isbn}
        ]
    };
    
    book = app.data.driver.db['isbn'].find_one(lookup)
    if book:
        return book

    payload = search_isbn.find_isbn_amazon(isbn)

    if not payload:
        payload = search_isbn.find_isbn_google(isbn)

    if not payload:
        return None

    if not 'isbn' in payload and 'isbn_10' in payload:
        payload['isbn'] = '978' + payload['isbn_10']

    post_internal('isbn', payload, True)

app.on_pre_GET_isbn += evt_isbn_pre_get
if __name__ == '__main__':
    print "SERVER"
    app.run()
