# -*- coding: utf-8 -*-
from eve import Eve, render
from flask import request, abort, Response
from .auth import TokenAuth, route_require_auth
from settings import EVE_SETTINGS_APP
from models import book, notification, friend, contact, account, loan
import json
from bson.objectid import ObjectId


app = Eve(__name__, settings=EVE_SETTINGS_APP, auth=TokenAuth)

@app.route('/v1/logout',methods=['DELETE'])
def route_logout():
    
    route_require_auth()
    account_id = app.auth.get_request_auth_value()
    account.logout(account_id)
    data['_status'] = 'OK'
    return render.render_json(data), 200, {'Content-Type': 'application/json; charset=utf-8'}

@app.route('/v1/auth',methods=['POST'])
def route_auth():
    
    if 'token' in request.json:
        token = request.json['token']
        data = account.login(access_token=token)

    else:
        email = request.json['email']
        password = request.json['password']

        data = account.login(email, password)

    if not data:
        abort(401, description='Email or password invalid')

    data['_status'] = 'OK'

    return render.render_json(data), 200, {'Content-Type': 'application/json; charset=utf-8'}


@app.route('/v1/books/<book_id>/loan/old',methods=['POST'])
def route_book_loan_old(book_id):
    route_require_auth()
    account_id = app.auth.get_request_auth_value()

    loan.start_loan(account_id, ObjectId(book_id), ObjectId(request.json['friend_id']), request.json)
    data = {
        '_status': 'OK'
    }

    return render.render_json(data), 200, {'Content-Type': 'application/json; charset=utf-8'}

@app.route('/v1/books/<book_id>/loan/status/old',methods=['POST'])
def route_book_loan_status_old(book_id):
    route_require_auth()
    account_id = app.auth.get_request_auth_value()

    loan.change_status(account_id, ObjectId(book_id), request.json)
    data = {
        '_status': 'OK'
    }

    return render.render_json(data), 200, {'Content-Type': 'application/json; charset=utf-8'}

@app.route('/v1/accounts/create',methods=['POST'])
def route_account_create():
    
    try:
        result = account.create(request.json)

        data = {
            '_id': result['_id'],
            '_status': 'OK'
        }
    except:
        data = {
            'error': 'Email duplicate'
        }


    return render.render_json(data), 200, {'Content-Type': 'application/json; charset=utf-8'}

@app.route('/v1/books/search',methods=['GET'])
def route_book():
    route_require_auth()
    account_id = app.auth.get_request_auth_value()
    result = book.book_search(account_id, request.args)
    data = {
        '_status': 'OK',
        '_items': result
    }
    return render.render_json(data), 200, {'Content-Type': 'application/json; charset=utf-8'}

@app.route('/v1/books/<book_id>/info',methods=['GET'])
def route_book_info(book_id):
    route_require_auth()
    account_id = app.auth.get_request_auth_value()

    data = book.book_info(account_id, ObjectId(book_id))

    return render.render_json(data), 200, {'Content-Type': 'application/json; charset=utf-8'}

@app.route('/v1/accounts/<account_id>/info',methods=['GET'])
def route_account_info(account_id):
    route_require_auth()
    if not ObjectId(account_id) == app.auth.get_request_auth_value():
        abort(401, description='Not permission')
    
    data = account.account_info(ObjectId(account_id))

    return render.render_json(data), 200, {'Content-Type': 'application/json; charset=utf-8'}




@app.route('/v1/accounts/<account_id>/update',methods=['PATCH'])
def route_account_update(account_id):
    route_require_auth()
    if not ObjectId(account_id) == app.auth.get_request_auth_value():
        abort(401, description='Not permission')
    
    account.account_update(ObjectId(account_id), request.json)
    
    data = {
        '_status': 'OK'
    }
    return render.render_json(data), 200, {'Content-Type': 'application/json; charset=utf-8'}

@app.route('/v1/accounts/<account_id>/device',methods=['PATCH'])
def route_account_device(account_id):
    route_require_auth()
    if not ObjectId(account_id) == app.auth.get_request_auth_value():
        abort(401, description='Not permission')
    
    account.account_device(ObjectId(account_id), request.json)
    
    data = {
        '_status': 'OK'
    }
    return render.render_json(data), 200, {'Content-Type': 'application/json; charset=utf-8'}

@app.route('/v1/friends/<friend_id>/books',methods=['GET'])
def route_friend_book(friend_id):
    route_require_auth()
    account_id = app.auth.get_request_auth_value()
    result = book.book_search(account_id, request.args, ObjectId(friend_id))
    data = {
        '_status': 'OK',
        '_items': result
    }
    return render.render_json(data), 200, {'Content-Type': 'application/json; charset=utf-8'}


@app.route('/v1/friend',methods=['GET'])
def route_friend_all():
    route_require_auth()
    account_id = app.auth.get_request_auth_value()
    result = friend.friend_all(account_id, request.args)
    data = {
        '_status': 'OK',
        '_items': result
    }
    return render.render_json(data), 200, {'Content-Type': 'application/json; charset=utf-8'}

@app.route('/v1/friends/<friend_id>',methods=['GET'])
def route_friend(friend_id):
    route_require_auth()
    account_id = app.auth.get_request_auth_value()
    result = friend.friend(account_id, ObjectId(friend_id))
    return render.render_json(result), 200, {'Content-Type': 'application/json; charset=utf-8'}

@app.route('/v1/friends/<friend_id>',methods=['DELETE'])
def route_friend_delete(friend_id):
    route_require_auth()
    account_id = app.auth.get_request_auth_value()
    result = friend.delete(account_id, ObjectId(friend_id))
    return render.render_json(result), 200, {'Content-Type': 'application/json; charset=utf-8'}


@app.route('/v1/friend/<friend_id>/invite',methods=['POST','DELETE'])
def route_friend_invite(friend_id):
    route_require_auth()
    account_id = app.auth.get_request_auth_value()
    if request.method == 'POST':
        result = friend.friend_invite(account_id, ObjectId(friend_id))
    else:
        result = friend.friend_invite_delete(account_id, ObjectId(friend_id))
    data = {
        '_status': 'OK'
    }
    return render.render_json(data), 200, {'Content-Type': 'application/json; charset=utf-8'}

@app.route('/v1/friend/<friend_id>/invite/accept',methods=['POST'])
def route_friend_invite_accept(friend_id):
    route_require_auth()
    account_id = app.auth.get_request_auth_value()

    result = friend.friend_invite_accept(account_id, ObjectId(friend_id))

    data = {
        '_status': 'OK'
    }
    return render.render_json(data), 200, {'Content-Type': 'application/json; charset=utf-8'}

@app.route('/v1/friend/<friend_id>/invite/cancel',methods=['POST'])
def route_friend_invite_cancel(friend_id):
    route_require_auth()
    account_id = app.auth.get_request_auth_value()

    result = friend.friend_invite_cancel(account_id, ObjectId(friend_id))

    data = {
        '_status': 'OK'
    }
    return render.render_json(data), 200, {'Content-Type': 'application/json; charset=utf-8'}


@app.route('/v1/friend/suggest',methods=['GET'])
def route_friend_suggest():
    route_require_auth()
    account_id = app.auth.get_request_auth_value()

    result = friend.friend_suggest(account_id, request.args)

    data = {
        '_status': 'OK',
        '_items': result
    }
    return render.render_json(data), 200, {'Content-Type': 'application/json; charset=utf-8'}

@app.route('/v1/friend/search',methods=['GET'])
def route_friend_search():
    route_require_auth()
    account_id = app.auth.get_request_auth_value()

    result = friend.friend_search(account_id, request.args)

    data = {
        '_status': 'OK',
        '_items': result
    }
    return render.render_json(data), 200, {'Content-Type': 'application/json; charset=utf-8'}

@app.route('/v1/contacts',methods=['POST'])
def route_contacts():
    route_require_auth()
    account_id = app.auth.get_request_auth_value()

    result = contact.contact_save(account_id, request.json)

    data = {
        '_status': 'OK'
    }
    return render.render_json(data), 201, {'Content-Type': 'application/json; charset=utf-8'}

@app.route('/v1/contacts',methods=['GET'])
def route_contacts_get():
    route_require_auth()
    account_id = app.auth.get_request_auth_value()

    result = contact.contact_get(account_id, request.args)

    data = {
        '_status': 'OK',
        '_items': result
    }
    return render.render_json(data), 200, {'Content-Type': 'application/json; charset=utf-8'}

@app.route('/v1/contacts/<contact_id>/invite',methods=['POST'])
def route_contacts_invite(contact_id):
    route_require_auth()
    account_id = app.auth.get_request_auth_value()

    result = contact.contact_invite(account_id, ObjectId(contact_id))

    data = {
        '_status': 'OK'
    }
    return render.render_json(data), 201, {'Content-Type': 'application/json; charset=utf-8'}

@app.route('/v1/books/<book_id>/recommend/<friend_id>',methods=['POST'])
def route_book_recommend(book_id, friend_id):
    route_require_auth()

    account_id = app.auth.get_request_auth_value()
    book_id = ObjectId(book_id)

    #@bugfix send push and notification
    result = book.book_recommend(account_id, ObjectId(friend_id), ObjectId(book_id))


    return render.render_json({'_status':'OK'}), 200, {'Content-Type': 'application/json; charset=utf-8'}

@app.route('/v1/books/<book_id>',methods=['PATCH'])
@app.route('/v1/books',methods=['POST'],defaults={'book_id': None})
def route_book_save(book_id):
    route_require_auth()
    account_id = app.auth.get_request_auth_value()
    if book_id:
        book_id = ObjectId(book_id)

    result = book.save(account_id, request.json, book_id)
    return render.render_json(result), 200, {'Content-Type': 'application/json; charset=utf-8'}

@app.route('/v1/books/<book_id>',methods=['DELETE'])
def route_book_delete(book_id):
    route_require_auth()
    account_id = app.auth.get_request_auth_value()
    book_id = ObjectId(book_id)

    book.delete(account_id, book_id)
    data = {
        '_status': 'OK'
    }
    return render.render_json(data), 200, {'Content-Type': 'application/json; charset=utf-8'}

@app.route('/v1/books/<book_id>/like',methods=['POST','DELETE'])
def route_book_like(book_id):
    route_require_auth()

    account_id = app.auth.get_request_auth_value()
    book_id = ObjectId(book_id)

    if request.method == 'POST':
        result = book.book_like(account_id, book_id)
    else:
        result = book.book_unlike(account_id, book_id)

    if not result:
        abort(404, description='Resource not found')

    return render.render_json({'_status':'OK'}), 200, {'Content-Type': 'application/json; charset=utf-8'}

@app.route('/v1/books/<book_id>/comments',methods=['POST','GET'])
def route_book_comment(book_id):
    route_require_auth()
    account_id = app.auth.get_request_auth_value()
    book_id = ObjectId(book_id)

    if request.method == 'GET': #create
        comments = book.book_get_comment(book_id)

        data = {
            '_status': 'OK',
            '_items': comments
        }
        return render.render_json(data), 200, {'Content-Type': 'application/json; charset=utf-8'}

    else:
        data = request.json
        if ('comment' in data) and data['comment']:
            comment = book.book_create_comment(account_id, book_id, data['comment'])
        return render.render_json(comment), 201, {'Content-Type': 'application/json; charset=utf-8'}


@app.route('/v1/notifications',methods=['POST','GET'])
def route_notifications():
    route_require_auth()
    account_id = app.auth.get_request_auth_value()
    
    if request.method == 'GET': #create
        notifications = notification.notification_get(account_id)
        data = {
            '_status': 'OK',
            '_items': notifications
        }
        return render.render_json(data), 200, {'Content-Type': 'application/json; charset=utf-8'}
    else:

        data = notification.notification_create(account_id,request.json)
        return render.render_json(data), 201, {'Content-Type': 'application/json; charset=utf-8'}
    
@app.route('/v1/notifications/<notification_id>/read',methods=['PATCH'])
def route_notifications_read(notification_id):
    route_require_auth()
    account_id = app.auth.get_request_auth_value()

    notification.notification_read(account_id, ObjectId(notification_id))
    data = {
        '_status': 'OK'
    }
    return render.render_json(data), 200, {'Content-Type': 'application/json; charset=utf-8'}

@app.route('/v1/notifications/view',methods=['PATCH'])
def route_notifications_view():
    route_require_auth()
    account_id = app.auth.get_request_auth_value()
    notification.notification_view(account_id, [ObjectId(i) for i in request.json['notifications']])
    data = {
        '_status': 'OK'
    }
    return render.render_json(data), 200, {'Content-Type': 'application/json; charset=utf-8'}


if __name__ == '__main__':
    app.run()
