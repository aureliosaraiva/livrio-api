#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from tasks.celery import celery

from settings import db, BASE_DIR
from bson.objectid import ObjectId
from .check_file import process_check_file
import uuid
import urllib

@celery.task(queue='cm_download_file', ignore_result=True)
def process_download_file(process_id):

    doc = db.process.find_one(ObjectId(process_id))

    filename = str(uuid.uuid4()).replace('-','_')
    link = doc['link']
    urllib.urlretrieve (link, BASE_DIR + '/_files/' + filename)

    db.process.update_one(
        {
            '_id': ObjectId(process_id)
        },
        {
            "$set": {
                "_internal_filename": filename,
                "filename": link.split("/")[-1]
            }
        }
    )
    process_check_file.apply_async([process_id])