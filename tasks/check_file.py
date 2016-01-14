#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals

import csv
import uuid
import time

from tasks.celery import celery
from settings import db, redis_client, BASE_DIR
from check import check_local
from .check_syntax import process_check_syntax
from .insert_db import process_insert_db
from bson.objectid import ObjectId

def to_unicode_or_bust(obj, encoding='utf-8'):
    if isinstance(obj, basestring):
        if not isinstance(obj, unicode):
            obj = unicode(obj, encoding)
    return obj
def convert_all(all, convert=to_unicode_or_bust):
    if isinstance(all, tuple):
        return tuple(convert_all(piece, convert) for piece in all)
    elif isinstance(all, list):
        return [convert_all(piece, convert) for piece in all]
    return convert(all)


def normalize(s):
    for i in ['utf-8', 'cp1252']:
        try:
            return s.decode(i)
        except:
            pass


@celery.task(queue='cm_check_file', ignore_result=True)
def process_check_file(process_id):

    doc = db.process.find_one(ObjectId(process_id))
    filename = doc['_internal_filename']
    delimiter = doc['delimiter'].encode("utf-8")
    quotechar = doc['quotechar'].encode("utf-8")
    column = int(doc['column'])
    deliverability = bool(doc['deliverability'])
    start_time = time.time()
    collection_name = 'process_' + process_id
    redis_client.set(process_id, 0)
    count_line  = 0
    
    #filename = 'emails.csv'

    with open(BASE_DIR + '/_files/' + filename, 'rb') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=delimiter, quotechar=quotechar)
        for row in spamreader:
            row = [normalize(s) for s in row]
            redis_client.incr(process_id)
            count_line += 1
            line_data = {'process_id':process_id, 'collection_name':collection_name, 'line':row, 'deliverability':deliverability}
            try:
                line_data['email'] = row[column].lower().replace(' ','')
                process_check_syntax.apply_async([line_data])
            except:
                line_data['error'] = 'ignore_line'
                process_insert_db.apply_async([line_data])
                pass

    db.process.update_one(
        {
            '_id': ObjectId(process_id)
        },
        {
            "$set": {
                "process_id": process_id,
                'collection_name':collection_name, 
                "start_time": time.time(),
                "count_line": count_line
            }
        }
    )



