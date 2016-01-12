#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from tasks.celery import celery

from check import check_domain
from .check_tld import process_check_tld
from .insert_db import process_insert_db



@celery.task(queue='cm_check_domain', ignore_result=True)
def process_check_domain(line_data):
    v = check_domain(line_data['email'])

    if v[0]:
        process_check_tld.apply_async([line_data])
    else:
        line_data['error'] = v[1]
        process_insert_db.apply_async([line_data])
    
    return None