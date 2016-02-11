# -*- coding: utf-8 -*-
from tasks import task_insert_book, task_send_email, task_send_push, task_location, task_download_photo_account, task_download_cover_account, task_download_cover_book, task_download_cover_isbn
from settings import db
from datetime import datetime



def register_failure(task, args, msg):
    date_utc = datetime.utcnow().replace(microsecond=0)
    payload = {
        '_created': date_utc,
        'task': task,
        'args': args,
        'message': msg
    }
    db.queue_failure.insert_one(payload)

def send_mail(account_id, template):
    args = [account_id, template]
    try:
        task_send_email.apply_async(args)
    except Exception, e:
        register_failure('task_send_mail',args, str(e))


def send_push(notification_id):
    args = [notification_id]
    try:
        task_send_push.apply_async(args)
    except Exception, e:
        register_failure('task_send_push',args, str(e))


def search_location(account_id):
    args = [account_id]
    try:
        task_location.apply_async(args)
    except Exception, e:
        register_failure('task_location',args, str(e))


def download_cover_book(book_id, isbn, url):
    if url.find('livrio-static') == -1:
        args = [book_id, isbn, url]
        try:
            task_download_cover_book.apply_async(args)
        except Exception, e:
            register_failure('task_download_cover_book',args, str(e))

def download_cover_book_isbn(isbn_id, isbn, url):
    if url.find('livrio-static') == -1:
        args = [isbn_id, isbn, url]
        try:
            task_download_cover_isbn.apply_async(args)
        except Exception, e:
            register_failure('task_download_cover_isbn',args, str(e))

def download_cover_account(account_id, url):
    if url.find('livrio-static') == -1:
        args = [account_id, url]
        try:
            task_download_cover_account.apply_async(args)
        except Exception, e:
            register_failure('task_download_cover_account',args, str(e))


def download_photo_account(account_id, url):
    if url.find('livrio-static') == -1:
        args = [account_id, url]
        try:
            task_download_photo_account.apply_async(args)
        except Exception, e:
            register_failure('task_download_photo_account',args, str(e))

def insert_book(book):
    args = [book]
    try:
        task_insert_book.apply_async(args)
    except Exception, e:
        print e
        register_failure('task_insert_book',args, str(e))

