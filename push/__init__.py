# -*- coding: utf-8 -*-

from util.push import Push
from settings import db


MESSAGE = {
    'system_welcome':'Olá {fullname}, seja bem vindo ao Livrio. Por aqui, a gente compartilha livros com quem também ama livros.',
    'system_first_book':'Parabéns {fullname}! Você cadastrou seu primeiro livro. Que tal agora convidar seus amigos?',
    'system_library_empty':'{fullname}, você ainda não cadastrou nenhum livro. Cadastre e compartilhe com seus amigos!',
    'friend':'{fullname} aceitou sua solicitação de amizade.',
    'friend_like_book':'{fullname} curtiu seu livro {title}.',
    'friend_recommend_book':'{fullname} te recomendou o livro {title}.',
    'request_friend':'{fullname} gostaria de ser seu amigo e ter acesso aos seus livros.',
    'lent_sent':'{fullname} quer te emprestar o livro {title}',
    'loan_request':'{fullname} pediu o empréstimo o livro {title}',
    'loan_confirm':'{fullname} te emprestou o livro {title}',
    'loan_confirm_yes': '{fullname} vai te emprestar o livro {title} {message}',
    'loan_confirm_no':'{fullname} cancelou empréstimo do livro {title}',
    'loan_return_confirm':'{fullname} devolveu o livro {title}',
    'loan_request_return':'{fullname} pediu que devolvesse o livro {title}',
    'loan_sent_canceled':'{fullname} não aceitou o empréstimo do livro {title}',
    'book_loan_return':'Lembre-se de devolver amanhã o livro {title}',
    'book_loan_return_day':'Lembre-se de devolver hoje o livro {title}',
    'book_loan_late':'{fullname} está esperando você devolver o livro {title}',
    'info_text':None,
    'system_updated':None,
    'loan_return':None,
    'loan_sent_refused':None
}

def send_push(notification_id):
    doc = db.notifications.find_one(notification_id)

    user = db.accounts.find_one(doc['account_id'],{'device_token':1,'fullname':1})

    #@bugfix verificar se usuário autoriza push

    if not 'device_token' in user:
        return None

    device = user['device_token']
    p = Push(device['platform'], device['token'])
    p.notification(notification_id)
    p.account_id(doc['account_id'])


    fullname = ''
    if 'from' in doc:
        _from = doc['from']
        fullname = _from['fullname']
        p.photo(_from['photo'])

    

    if doc['type'] in ['system_library_empty','system_welcome','system_first_book']:
        fullname = user['fullname']


    if 'book' in doc:
        p.book(doc['book'])
        p.message(MESSAGE[doc['type']].format(fullname=_from['fullname'], title=doc['book']['title']))
    else:
        p.message(MESSAGE[doc['type']].format(fullname=fullname))



    p.extra({'type': doc['type']})
    p.send()


