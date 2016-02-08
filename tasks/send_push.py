# -*- coding: utf-8 -*-
from __future__ import absolute_import
from tasks.celery import celery
import push

@celery.task(queue='push', ignore_result=True)
def task_send_push(notification_id):
    push.send_push(notification_id)
   