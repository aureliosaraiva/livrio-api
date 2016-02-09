# -*- coding: utf-8 -*-
from send_mail import task_send_email
from send_push import task_send_push
from settings import db
from datetime import datetime
from location import task_location


def register_failure(task, args):
    date_utc = datetime.utcnow().replace(microsecond=0)
    payload = {
        '_created': date_utc,
        'task': task,
        'args': args
    }
    db.queue_failure.inser_one(payload)

def send_mail(account_id, template):
    args = [account_id, template]
    try:
        task_send_email.apply_async(args)
    except:
        register_failure('task_send_mail',args)


def send_push(notification_id):
    args = [notification_id]
    try:
        task_send_push.apply_async(args)
    except:
        register_failure('task_send_push',args)


def search_location(account_id):
    args = [account_id]
    try:
        task_location.apply_async(args)
    except:
        register_failure('task_location',args)

