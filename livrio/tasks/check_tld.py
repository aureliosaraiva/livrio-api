#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from tasks.celery import celery

from check import check_tld
from .check_mx import process_check_mx
from .insert_db import process_insert_db



@celery.task(queue='cm_check_tld', ignore_result=True)
def process_check_tld(line_data): 
    v = check_tld(line_data['email'])

    if v[0]:
        process_check_mx.apply_async([line_data])
    else:
        line_data['error'] = v[1]
        process_insert_db.apply_async([line_data])
    
    return None