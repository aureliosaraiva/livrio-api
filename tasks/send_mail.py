# -*- coding: utf-8 -*-
from __future__ import absolute_import
from tasks.celery import celery
import mail


@celery.task(queue='mailer', ignore_result=True)
def task_send_email(account_id, template):
    
    if template == 'signup':
        mail.signup(account_id)