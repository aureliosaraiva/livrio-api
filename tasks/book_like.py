# -*- coding: utf-8 -*-
from __future__ import absolute_import
from tasks.celery import celery

@celery.task(queue='notification', ignore_result=True)
def task_book_like(data):
    print "Notiication"
    return None