#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from tasks.celery import celery
import requests
from settings import redis_client, db, BASE_DIR
from bson.objectid import ObjectId
import json

@celery.task(queue='cm_webhook', ignore_result=True)
def process_webhook(process_id):

    doc = db.process.find_one(ObjectId(process_id))
    if doc['webhook']:
        data = {'process_id': process_id,'status':'completed'}
        headers = {
            'Content-type': 'application/json',
            'Accept': 'text/plain',
            'User-Agent': 'CheckMailing WebHook Agent'
        }
        requests.post(doc['webhook'], data=json.dumps(data), headers=headers)

    return None