# -*- coding: utf-8 -*-
# from tasks import send_mail
from tasks import send_push

# from util.push import Push
from bson.objectid import ObjectId


# doc = {
#     'fullname': 'Aurélio Saraiva',
#     'first_name': 'Aurélio',
#     'last_name': 'Saraiva',
#     'email': 'aurelio@codeway.com.br',
# }
# send_mail.task_send_email.apply_async([doc,'signup'])

# p = Push(1, platform='android',token='drtAhphfkkddddddyTsw:APA91bGZHNIfXddddFTQfFx86poUni3CbDdyKNUbkbYvAWoURdHJF4VrQgxw7dWAnBYpjT75XPIAF4XttqLOrulccAzyGP1N-tfrbl_dM158w_fuXlrPvEUkaGK8eI8lzFOaPTWjiKQ00tX3')

# p.account_id(ObjectId("56b8df25f387bc33fe9790d5"))
# p.message('Atualize seu aplicativo')


# p.send()

send_push.task_send_push.apply_async([ObjectId("56b8df27f387bc33fe97a43d")])