#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from tasks.celery import celery
from settings import redis_client, db
from .make_csv import process_make_csv
from bson.objectid import ObjectId
import time

@celery.task(queue='cm_insert_db', ignore_result=True)
def process_insert_db(line_data):
    id = line_data['process_id']
    collection = line_data['collection_name']
    db[collection].insert_one(line_data)
    redis_client.decr(id)


    if int(redis_client.get(id)) == 0:
        redis_client.delete(id)
        db.process.update_one(
            {
                '_id': ObjectId(id)
            },
            {
                "$set": {
                    "end_time": time.time()
                }
            }
        )
        process_make_csv.apply_async([line_data])
    return None