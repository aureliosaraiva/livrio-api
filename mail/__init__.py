# -*- coding: utf-8 -*-
import sendgrid
from settings import SENDGRID
from util import file_get_contents
from jinja2 import Template

sg = sendgrid.SendGridClient(SENDGRID['API_KEY'])

def send_mail(from_email, from_name, subject, template, variables={}):
    message = sendgrid.Mail()
    message.add_to('aurelio@codeway.com.br')
    message.add_to_name('Aurelio')
    message.set_subject('Test API')
    message.set_html('Body')
    message.set_text('Body')
    message.set_from('Doe John <doe@email.com>')
    status, msg = sg.send(message)
    print status
    print msg


def process_template(name, variables):
    html = file_get_contents('/home/aureliosaraiva/projetos/livrio/api/mail/templates/{}.html'.format(name))
    print html.encode('utf-8')
    text = file_get_contents('/home/aureliosaraiva/projetos/livrio/api/mail/templates/{}.txt'.format(name))
    s = Template(html)
    html = s.render(variables)

    s = Template(text)
    text = s.render(variables)

    return {
        'html': html,
        'text': text
    }


def mail_signup(account_id):
    print process_template('signup',{'name':'Aurélio'})
    print "mail_signup"