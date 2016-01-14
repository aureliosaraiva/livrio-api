from __future__ import absolute_import
import os

from celery import Celery

celery = Celery()
celery.config_from_object('settings')

if __name__ == '__main__':
    celery.start()
