# -*- coding: utf-8 -*-
import sendgrid
from settings import SENDGRID
from string import Template

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


def process_template():
    s = Template('$who likes $what')
    s.substitute(who='tim', what='kung pao')