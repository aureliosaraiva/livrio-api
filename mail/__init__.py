# -*- coding: utf-8 -*-

from util.mail import Mail
from settings import db


def signup(account_id):
    doc = db.accounts.find_one(account_id)
    m = Mail()
    m.subject('Bem-vindo ao Livrio!')
    m.from_name('Livrio')
    m.from_email('app@livr.io')
    m.to_name(doc['fullname'])
    m.to_email(doc['email'])

    m.template('signup')

    data = {
        'fullname': doc['fullname'],
        'first_name': doc['first_name'],
        'last_name': doc['last_name'],
        'email': doc['email']
    }

    m.variables(data)
    m.send()