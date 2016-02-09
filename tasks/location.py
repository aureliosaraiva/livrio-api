# -*- coding: utf-8 -*-
from __future__ import absolute_import
from tasks.celery import celery
from models import account

@celery.task(queue='location', ignore_result=True)
def task_location(account_id):
    
    account.update_location(account_id)