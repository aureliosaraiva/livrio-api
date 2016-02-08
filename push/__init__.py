# -*- coding: utf-8 -*-

from util.push import Push
from app.model import notification
from settings import db

TYPE = notification.TYPE

def send_push(notification_id):
    doc = db.notifications.find_one(notification_id)

    user = db.accounts.find_one(doc['account_id'])

    #@bugfix verificar se usuário autoriza push

    if not 'device_token' in user:
        return None

    device = user['device_token']
    p = Push(device['platform'], device['token'])
    p.notification(notification_id)
    p.account_id(doc['account_id'])


    if 'book' in doc:
        _book = doc['book']
        p.book(_book)

    if 'from' in doc:
        _from = doc['from']
        p.photo(_from['photo'])

    p.extra({
          'type': doc['type']  
    })

    if doc['type'] == TYPE['FRIEND_LIKE_BOOK']:
        p.message('{} curtiu seu livro {}'.format(_from['fullname'], _book['title']))


    p.send()


