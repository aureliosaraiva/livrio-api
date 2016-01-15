# -*- coding: utf-8 -*-
from __future__ import absolute_import
from eve import Eve
from .auth import TokenAuth
from .event_hook import evt_isbn_pre_get, evt_isbn_post_get, evt_create_token
from settings import EVE_SETTINGS


print "RUN"
app = Eve(__name__, settings=EVE_SETTINGS, auth=TokenAuth)
dir(app)
app.on_insert_accounts += evt_create_token
app.on_pre_GET_isbn += evt_isbn_pre_get
app.on_post_GET_isbn += evt_isbn_post_get
if __name__ == '__main__':
    print "SERVER"
    app.run()
