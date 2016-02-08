# -*- coding: utf-8 -*-
from gcm import GCM
from apns import APNs, Frame, Payload
from settings import PUSH, db
from datetime import datetime



class Push(object):
    """docstring for push"""

    data = {
        'style': 'inbox',
        'title': 'Livrio',
        'image': 'http://img.livr.io/user/livrio.png',
        'summaryText': '%n% notificações',
        'ledColor': [0, 249,176 , 0]
    }

    def __init__(self, platform, token):
        # self.data['notId'] = id
        self.platform = platform
        self.token = token

    def account_id(self, id):
        self.id = id

    def notification(self, id):
        self.notification_id = id

    def message(self, message):
        self.data['message'] = message

    def photo(self, photo):
        self.data['image'] = photo

    def book(self, book):
        self.data['book_id'] = book['_id']
        self.data['book_title'] = book['title']

    def extra(self, data):
        self.data.update(data)

    def gcm(self):
        try:
            gcm = GCM(PUSH['GCM'])
            gcm.plaintext_request(registration_id=self.token, data=self.data)
            return ('Ok', '')
        except Exception, e:
            return ('Error', str(e))


    def send(self):

        if self.platform == 'android':
            status, msg = self.gcm()
        elif self.platform == 'ios':
            status, msg = self.apns()


        if status:
            self.data['response'] = {
                'status': status,
                'msg': msg
            }

            if hasattr(self, 'id'):
                self.data['account_id'] = self.id

            if hasattr(self, 'notification_id'):
                self.data['notification_id'] = self.notification_id

            date_utc = datetime.utcnow().replace(microsecond=0)
            self.data['_created'] = date_utc

            db.push.insert_one(self.data)


    def apns():
        pass





        
"""
from util import push
push.send_gcm('fufJ4o8vJuI:APA91bEBXag5PG32NCZnlG5CjPexymXcRwmfIB4TTVrs4IPZeSjO1rWLE2acGvfs0MscF1ujggyOoYWyhOg4cci9xQZ4K7lOX6ZYOAoWZigWcwTOKJxJAgs7iTFOmYQOIEXhTAigm-2h',{'title':'Livrio','message':'teste'})
"""
#fufJ4o8vJuI:APA91bEBXag5PG32NCZnlG5CjPexymXcRwmfIB4TTVrs4IPZeSjO1rWLE2acGvfs0MscF1ujggyOoYWyhOg4cci9xQZ4K7lOX6ZYOAoWZigWcwTOKJxJAgs7iTFOmYQOIEXhTAigm-2h



{"platform":"ios","token":""}

"""
from util import push
push.send_apn('f152b3b0d623172afa07a5e2f19264eb3ff615f7ec706b741c77217b54d909e9',{'title':'Livrio','message':'teste'})
"""
def send_apn(token, data):
    path = '/home/aureliosaraiva/projetos/livrio/api/settings/ssl/apns/'
    apns = APNs(use_sandbox=True, cert_file=path + 'ck-no.pem', key_file=path + 'ckp-no.pem')
    payload = Payload(alert="Hello World!", sound="default", badge=1)
    apns.gateway_server.send_notification(token, payload)


