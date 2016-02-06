# -*- coding: utf-8 -*-
from __future__ import absolute_import
from tasks.celery import celery
from mail import send_mail

@celery.task(queue='send_email', ignore_result=True)
def task_send_email(data):
    print "Send Email"
    return None