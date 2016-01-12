# -*- coding: utf-8 -*-

from __future__ import absolute_import
from tasks.celery import celery
from settings import redis_client, db, BASE_DIR
import csv
from bson.objectid import ObjectId
from .webhook import process_webhook


@celery.task(queue='cm_make_csv', ignore_result=True)
def process_make_csv(line_data):
    process_id = line_data['process_id']

    doc = db.process.find_one(ObjectId(process_id))

    collection = doc['collection_name']
    delimiter = doc['delimiter'].encode("utf-8")
    quotechar = doc['quotechar'].encode("utf-8")

    with open(BASE_DIR + '/_output/' + doc['_internal_filename'] + '.csv', 'wb') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=delimiter, quotechar=quotechar, quoting=csv.QUOTE_MINIMAL)
        for row in db[collection].find():
            line = row['line']
            try:
                line.append(row['error'])
            except:
                line.append('OK')
            
            spamwriter.writerow([unicode(s).encode("utf-8") for s in line])

    process_webhook.apply_async([process_id])