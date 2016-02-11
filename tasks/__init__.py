# -*- coding: utf-8 -*-
from __future__ import absolute_import
from tasks.celery import celery
from settings import db
from datetime import datetime



@celery.task(queue='mailer', ignore_result=True)
def task_send_email(account_id, template):
    import mail
    if template == 'signup':
        mail.signup(account_id)

@celery.task(queue='location', ignore_result=True)
def task_location(account_id):
    from models import account
    account.update_location(account_id)

@celery.task(queue='push', ignore_result=True)
def task_send_push(notification_id):
    import push
    push.send_push(notification_id)


@celery.task(queue='image', ignore_result=True)
def task_download_cover_account(account_id, url):
    from models import account
    account.download_cover(account_id, url)

@celery.task(queue='image', ignore_result=True)
def task_download_photo_account(account_id, url):
    from models import account
    account.download_photo(account_id, url)

@celery.task(queue='image', ignore_result=True)
def task_download_cover_book(book_id, isbn, url):
    from models import book
    book.download_cover(book_id, isbn, url)

@celery.task(queue='image', ignore_result=True)
def task_download_cover_isbn(isbn_id, isbn, url):
    from models import book
    print url
    book.download_cover_isbn(isbn_id, isbn, url)

@celery.task(queue='insert_book', ignore_result=True)
def task_insert_book(book):
    if 'isbn' in book:
        doc = db.isbn.find_one({'isbn':book['isbn']})
        if not doc:

            date_utc = datetime.utcnow().replace(microsecond=0)
            payload = {
                '_created': date_utc,
                '_updated': date_utc,
                '_deleted': False
            }

            payload.update(book)

            db.isbn.insert_one(payload)
            task_download_cover_isbn.apply_async([payload['_id'], book['isbn'], book['cover']])
