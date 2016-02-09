# -*- coding: utf-8 -*-
from gcm import GCM
from settings import PUSH, db, DEBUG, DEBUG_CONFIG
from datetime import datetime
from util import legacy



class Push(object):
    """docstring for push"""

    android = {
        'style': 'inbox',
        'title': 'Livrio',
        'image': 'http://img.livr.io/user/livrio.png',
        'summaryText': '%n% notificações',
        'ledColor': [0, 249,176 , 0]
    }

    ios = {

    }

    def __init__(self, platform, token):
        # self.data['notId'] = id
        
        if DEBUG:
            self.platform = DEBUG_CONFIG['platform']
            self.token = DEBUG_CONFIG['token']
        else:
            self.platform = platform
            self.token = token

    def account_id(self, id):
        self.id = id

    def notification(self, id):
        self.notification_id = id

    def message(self, message):
        self.android['message'] = message
        self.ios['message'] = message

    def photo(self, photo):
        self.android['image'] = photo

    def book(self, book):
        self.android['book_id'] = book['_id']
        self.android['book_title'] = book['title']

    def extra(self, data):
        self.android.update(data)

    def gcm(self):
        try:
            gcm = GCM(PUSH['GCM'])
            gcm.plaintext_request(registration_id=self.token, data=self.android)
            return ('Ok', '')
        except Exception, e:
            return ('Error', str(e))


    def send(self):

        if self.platform == 'android':
            status, msg = self.gcm()
            payload = self.android
        elif self.platform == 'ios':
            status, msg = self.apns()
            payload = self.ios


        if payload:
            payload['response'] = {
                'status': status,
                'msg': msg
            }

            if hasattr(self, 'id'):
                payload['account_id'] = self.id

            if hasattr(self, 'notification_id'):
                payload['notification_id'] = self.notification_id

            date_utc = datetime.utcnow().replace(microsecond=0)
            payload['_created'] = date_utc
            payload['device'] = self.token
            payload['platform'] = self.platform

            db.push.insert_one(payload)


    def apns(self):
        status = legacy.push_ios(self.token, self.ios['message'])
        if status:
            return ('OK', '')
        else:
            return ('Error','')


