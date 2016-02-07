# -*- coding: utf-8 -*-
import sendgrid
from settings import SENDGRID




   
    
    
    message.set_html('Body')
    message.set_text('Body')
    
    status, msg = sg.send(message)


class Mail(object):

    def __init__(self):
        self.sg = sendgrid.SendGridClient(SENDGRID['API_KEY'])


    def create(self):
        self.message = sendgrid.Mail()

    def subject(self, subject):
        self.message.set_subject(subject)

    def from_name(self, name):
        message.set_from_name(name)

    def from_email(self, email):
        message.set_from(email)

    def to_name(self, name):
        self.message.add_to_name(name)

    def to_email(self, email):
        self.message.add_to(email)

    def variables(self, data):
        pass


    def send(self):
        pass