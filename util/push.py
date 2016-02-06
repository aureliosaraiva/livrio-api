from gcm import GCM
from apns import APNs, Frame, Payload
from settings import PUSH


"""
from util import push
push.send_gcm('fufJ4o8vJuI:APA91bEBXag5PG32NCZnlG5CjPexymXcRwmfIB4TTVrs4IPZeSjO1rWLE2acGvfs0MscF1ujggyOoYWyhOg4cci9xQZ4K7lOX6ZYOAoWZigWcwTOKJxJAgs7iTFOmYQOIEXhTAigm-2h',{'title':'Livrio','message':'teste'})
"""
#fufJ4o8vJuI:APA91bEBXag5PG32NCZnlG5CjPexymXcRwmfIB4TTVrs4IPZeSjO1rWLE2acGvfs0MscF1ujggyOoYWyhOg4cci9xQZ4K7lOX6ZYOAoWZigWcwTOKJxJAgs7iTFOmYQOIEXhTAigm-2h

def send_gcm(token, data):
    gcm = GCM(PUSH['GCM'])
    gcm.plaintext_request(registration_id=token, data=data)

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


