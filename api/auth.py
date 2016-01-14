# -*- coding: utf-8 -*-

from flask import request, current_app as app, g, abort

class TokenAuth(object):
    def set_mongo_prefix(self, value):
        g.mongo_prefix = value

    def get_mongo_prefix(self):
        return g.get('mongo_prefix')

    def set_request_auth_value(self, value):
        g.auth_value = value

    def get_request_auth_value(self):
        return g.get('auth_value')

    def check_auth(self, token, allowed_roles, resource, method):
        if resource == 'accounts':
            return True

        accounts = app.data.driver.db['accounts']
        lookup = {'token': token}
        if allowed_roles:
            lookup['roles'] = {'$in': allowed_roles}

        acc = accounts.find_one(lookup)

        if acc:
            self.set_request_auth_value(acc['_id'])

        return acc

    def authenticate(self):
        abort(401, description='Please provide proper credentials')

    def authorized(self, allowed_roles, resource, method):
        
        args = request.args

        token = None
        if 'apikey' in args:
            token = args['apikey']
            return token and self.check_auth(token, allowed_roles, resource,method)


        auth = request.headers.get('Authorization')

        
        try:
            token = auth
        except:
            token = None

        return token and self.check_auth(token, allowed_roles, resource,method)

class RealTimeTokenAuth(object):
    def set_mongo_prefix(self, value):
        g.mongo_prefix = value

    def get_mongo_prefix(self):
        return g.get('mongo_prefix')

    def set_request_auth_value(self, value):
        g.auth_value = value

    def get_request_auth_value(self):
        return g.get('auth_value')

    def check_auth(self, token, allowed_roles, resource, method):
        if resource == 'accounts':
            return True

        accounts = app.data.driver.db['accounts']
        lookup = {'token': token}
        if allowed_roles:
            lookup['roles'] = {'$in': allowed_roles}

        acc = accounts.find_one(lookup)

        if acc:
            self.set_request_auth_value(acc['_id'])

        return acc

    def authenticate(self):
        abort(401, description='Please provide proper credentials')

    def authorized(self, allowed_roles, resource, method):
        args = request.args

        token = None
        if 'apikey' in args:
            token = args['apikey']

        return token and self.check_auth(token, allowed_roles, resource,method)
