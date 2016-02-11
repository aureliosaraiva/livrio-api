# -*- coding: utf-8 -*-
import sendgrid
from datetime import datetime
from settings import SENDGRID, db, DEBUG, DEBUG_CONFIG
from jinja2 import Environment, PackageLoader
env = Environment(loader=PackageLoader('mail', 'templates'))


class Mail(object):

    data = {}
    payload = {}

    def __init__(self):
        self.sg = sendgrid.SendGridClient(SENDGRID['API_KEY'])
        self.create()


    def create(self):
        self.message = sendgrid.Mail()

    def subject(self, subject):
        self.message.set_subject(subject)
        self.payload['subject'] = subject

    def from_name(self, name):
        self.message.set_from_name(name)
        self.payload['from_name'] = name

    def from_email(self, email):
        self.message.set_from(email)
        self.payload['from_email'] = email

    def to_name(self, name):
        self.message.add_to_name(name)
        self.payload['to_name'] = name

    def to_email(self, email):
        
        if DEBUG:
            self.message.add_to( DEBUG_CONFIG['email'])
        else:
            self.message.add_to( email )
        

        self.payload['to_email'] = email



    def variables(self, data):

        self.data = data
        self.payload['variables'] = data

    def template(self, name):
        self.template_name = name
        self.payload['template'] = name

    def build(self):
        template = env.get_template(self.template_name + '.html')
        html = template.render(self.data)
        self.message.set_html(html)
        self.payload['html'] = html

        try:
            template = env.get_template(self.template_name + '.txt')
            text = template.render(self.data)
            self.message.set_text(text)
            self.payload['text'] = text
        except:
            pass

    def send(self):
        self.build()
        status, msg = self.sg.send(self.message)
        self.payload['response'] = {
            'status': status,
            'msg': msg
        }

        date_utc = datetime.utcnow().replace(microsecond=0)

        self.payload['_created'] = date_utc

        db.mailer.insert_one(self.payload)
