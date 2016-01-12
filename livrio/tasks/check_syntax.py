#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from tasks.celery import celery

from check import check_syntax
from .check_local import process_check_local
from .insert_db import process_insert_db



@celery.task(queue='cm_check_syntax', ignore_result=True)
def process_check_syntax(line_data):
    v = check_syntax(line_data['email'])

    if v[0]:
        process_check_local.apply_async([line_data])
    else:
        line_data['error'] = v[1]
        process_insert_db.apply_async([line_data])

    return None