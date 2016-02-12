# -*- coding: utf-8 -*-
from settings import db
from datetime import datetime
from bson.objectid import ObjectId
from util import google

#@bugfix melhorar logica
def search(params=None):


    if not 'word' in params:
        return []

    word = params['word']
    
    limit = 25
    offset = 0

    if 'limit' in params:
        limit = int(params['limit'])

    if 'offset' in params:
        offset = int(params['offset'])

    if offset > 0:
        offset = ((offset-1)*limit)

    books = google.search_books(word, offset=offset, limit=limit)

    return books