# -*- coding: utf-8 -*-
from eve import Eve, render
from flask import request, abort, Response
from .auth import TokenAuth, route_require_auth
from settings import EVE_SETTINGS_APP
from models import book, notification, friend, contact, account, loan
import json
from bson.objectid import ObjectId
from event import register as event_track
from flask.ext.cors import CORS


app = Eve(__name__, settings=EVE_SETTINGS_APP, auth=TokenAuth)
CORS(app)

@app.route('/v1/logout',methods=['DELETE'])
def route_logout():

    route_require_auth()
    account_id = app.auth.get_request_auth_value()
    account.logout(account_id)
    data['_status'] = 'OK'
    event_track('logout', account_id)
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

    if 'token' in data:
        event_track('signin', data['_id'])
        data['_status'] = 'OK'
    else:
        data = {'_status':'ERR', '_code': 1}

    return render.render_json(data), 200, {'Content-Type': 'application/json; charset=utf-8'}

@app.route('/v1/loan',methods=['GET'])
def route_book_loan_all():
    route_require_auth()
    account_id = app.auth.get_request_auth_value()

    result = loan.all(account_id, request.args)
    data = {}
    data['_status'] = 'OK'
    data['_items'] = result

    return render.render_json(data), 200, {'Content-Type': 'application/json; charset=utf-8'}

@app.route('/v1/loan/<loan_id>',methods=['GET','POST'])
def route_book_loan(loan_id):
    route_require_auth()
    account_id = app.auth.get_request_auth_value()

    data = loan.info(account_id, ObjectId(loan_id))
    data['_status'] = 'OK'

    return render.render_json(data), 200, {'Content-Type': 'application/json; charset=utf-8'}

@app.route('/v1/loan/<loan_id>/address',methods=['PATCH'])
def route_book_loan_address(loan_id):
    route_require_auth()
    account_id = app.auth.get_request_auth_value()

    loan.address(account_id, ObjectId(loan_id), request.json['address'])
    data = {'_status' : 'OK' }

    return render.render_json(data), 200, {'Content-Type': 'application/json; charset=utf-8'}

@app.route('/v1/books/<book_id>/loan',methods=['POST'])
def route_book_loan_start(book_id):
    route_require_auth()
    account_id = app.auth.get_request_auth_value()

    data = loan.start_loan(account_id, ObjectId(book_id), ObjectId(request.json['friend_id']), request.json)
    data['_status'] = 'OK'
    return render.render_json(data), 200, {'Content-Type': 'application/json; charset=utf-8'}

@app.route('/v1/loan/<loan_id>/messages',methods=['POST','GET'])
def route_book_loan_message(loan_id):
    route_require_auth()
    account_id = app.auth.get_request_auth_value()
    loan_id = ObjectId(loan_id)


    if request.method == 'GET':
        time = None
        if 'offset' in request.args:
            offset = request.args['offset']

        messages = loan.messages(account_id, loan_id, offset)

        data = {
            '_status': 'OK',
            'interval': 2000,
            '_items': messages
        }
        return render.render_json(data), 200, {'Content-Type': 'application/json; charset=utf-8'}

    else:
        #@bug
        data = request.json
        if ('text' in data) and data['text']:
            comment = loan.create_messages(account_id, loan_id, data['text'])
            comment['_status'] = 'OK'
        return render.render_json(comment), 201, {'Content-Type': 'application/json; charset=utf-8'}


@app.route('/v1/loan/<loan_id>/status',methods=['POST'])
def route_book_loan_status(loan_id):
    route_require_auth()
    account_id = app.auth.get_request_auth_value()

    loan.change_status(account_id, ObjectId(loan_id), request.json)
    data = {
        '_status': 'OK'
    }

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
        event_track('signup', result['_id'])
    except:
        data = {
            '_status': 'ERR',
            '_code': 10,
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
    #@bugfix
    event_track('book_search', account_id)
    return render.render_json(data), 200, {'Content-Type': 'application/json; charset=utf-8'}

@app.route('/v1/books/<book_id>/info',methods=['GET'])
def route_book_info(book_id):
    route_require_auth()
    account_id = app.auth.get_request_auth_value()

    data = book.book_info(account_id, ObjectId(book_id))
    data['_status'] = 'OK'
    event_track('book_view', account_id)
    return render.render_json(data), 200, {'Content-Type': 'application/json; charset=utf-8'}

@app.route('/v1/accounts/<account_id>/info',methods=['GET'])
def route_account_info(account_id):
    route_require_auth()
    if not ObjectId(account_id) == app.auth.get_request_auth_value():
        abort(401, description='Not permission')

    data = account.account_info(ObjectId(account_id))

    return render.render_json(data), 200, {'Content-Type': 'application/json; charset=utf-8'}

@app.route('/v1/accounts/info',methods=['GET'])
def route_account():
    route_require_auth()
    account_id = app.auth.get_request_auth_value()

    data = account.account_info(account_id)

    data['_status'] = 'OK'

    return render.render_json(data), 200, {'Content-Type': 'application/json; charset=utf-8'}

@app.route('/v1/accounts/update',methods=['PATCH'])
def route_account_update():
    route_require_auth()
    account_id = app.auth.get_request_auth_value()

    account.account_update(account_id, request.json)

    data = {
        '_status': 'OK'
    }
    event_track('account_update', ObjectId(account_id))
    return render.render_json(data), 200, {'Content-Type': 'application/json; charset=utf-8'}


@app.route('/v1/accounts/<account_id>/update',methods=['PATCH'])
def route_account_update_old(account_id):
    route_require_auth()
    if not ObjectId(account_id) == app.auth.get_request_auth_value():
        abort(401, description='Not permission')

    account.account_update(ObjectId(account_id), request.json)

    data = {
        '_status': 'OK'
    }
    event_track('account_update', ObjectId(account_id))
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
    event_track('friend_books', account_id)
    return render.render_json(data), 200, {'Content-Type': 'application/json; charset=utf-8'}


@app.route('/v1/friends',methods=['GET'])
def route_friend_all():
    route_require_auth()
    account_id = app.auth.get_request_auth_value()
    result = friend.friend_all(account_id, request.args)
    data = {
        '_status': 'OK',
        '_items': result
    }
    event_track('friends', account_id)
    return render.render_json(data), 200, {'Content-Type': 'application/json; charset=utf-8'}

@app.route('/v1/friend',methods=['GET'])
def route_friend_all_old():
    route_require_auth()
    account_id = app.auth.get_request_auth_value()
    result = friend.friend_all(account_id, request.args)
    data = {
        '_status': 'OK',
        '_items': result
    }
    event_track('friends', account_id)
    return render.render_json(data), 200, {'Content-Type': 'application/json; charset=utf-8'}

@app.route('/v1/friends/<friend_id>',methods=['GET'])
def route_friend(friend_id):
    route_require_auth()
    account_id = app.auth.get_request_auth_value()
    result = friend.friend(account_id, ObjectId(friend_id))
    result['_status'] = 'OK'
    event_track('friend_view', account_id)
    return render.render_json(result), 200, {'Content-Type': 'application/json; charset=utf-8'}

@app.route('/v1/friends/<friend_id>',methods=['DELETE'])
def route_friend_delete(friend_id):
    route_require_auth()
    account_id = app.auth.get_request_auth_value()
    result = friend.delete(account_id, ObjectId(friend_id))
    event_track('friend_delete', account_id)
    result['_status'] = 'OK'
    return render.render_json(result), 200, {'Content-Type': 'application/json; charset=utf-8'}

@app.route('/v1/friends/<friend_id>/invite',methods=['POST','DELETE'])
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
    event_track('friend_invite', account_id)
    return render.render_json(data), 200, {'Content-Type': 'application/json; charset=utf-8'}

@app.route('/v1/friends/<friend_id>/invite/accept',methods=['POST'])
def route_friend_invite_accept(friend_id):
    route_require_auth()
    account_id = app.auth.get_request_auth_value()

    result = friend.friend_invite_accept(account_id, ObjectId(friend_id))

    data = {
        '_status': 'OK'
    }
    event_track('friend_accept', account_id)
    return render.render_json(data), 200, {'Content-Type': 'application/json; charset=utf-8'}

@app.route('/v1/friends/<friend_id>/invite/cancel',methods=['POST'])
def route_friend_invite_cancel(friend_id):
    route_require_auth()
    account_id = app.auth.get_request_auth_value()

    result = friend.friend_invite_cancel(account_id, ObjectId(friend_id))

    data = {
        '_status': 'OK'
    }
    event_track('friend_cancel', account_id)
    return render.render_json(data), 200, {'Content-Type': 'application/json; charset=utf-8'}

@app.route('/v1/friend/<friend_id>/invite',methods=['POST','DELETE'])
def route_friend_invite_old(friend_id):
    route_require_auth()
    account_id = app.auth.get_request_auth_value()
    if request.method == 'POST':
        result = friend.friend_invite(account_id, ObjectId(friend_id))
    else:
        result = friend.friend_invite_delete(account_id, ObjectId(friend_id))
    data = {
        '_status': 'OK'
    }
    event_track('friend_invite', account_id)
    return render.render_json(data), 200, {'Content-Type': 'application/json; charset=utf-8'}

@app.route('/v1/friend/<friend_id>/invite/accept',methods=['POST'])
def route_friend_invite_accept_old(friend_id):
    route_require_auth()
    account_id = app.auth.get_request_auth_value()

    result = friend.friend_invite_accept(account_id, ObjectId(friend_id))

    data = {
        '_status': 'OK'
    }
    event_track('friend_accept', account_id)
    return render.render_json(data), 200, {'Content-Type': 'application/json; charset=utf-8'}

@app.route('/v1/friend/<friend_id>/invite/cancel',methods=['POST'])
def route_friend_invite_cancel_old(friend_id):
    route_require_auth()
    account_id = app.auth.get_request_auth_value()

    result = friend.friend_invite_cancel(account_id, ObjectId(friend_id))

    data = {
        '_status': 'OK'
    }
    event_track('friend_cancel', account_id)
    return render.render_json(data), 200, {'Content-Type': 'application/json; charset=utf-8'}

@app.route('/v1/friends/suggest',methods=['GET'])
def route_friend_suggest():
    route_require_auth()
    account_id = app.auth.get_request_auth_value()

    result = friend.friend_suggest(account_id, request.args)

    data = {
        '_status': 'OK',
        '_items': result
    }
    event_track('friend_suggest', account_id)
    return render.render_json(data), 200, {'Content-Type': 'application/json; charset=utf-8'}

@app.route('/v1/friend/suggest',methods=['GET'])
def route_friend_suggest_old():
    route_require_auth()
    account_id = app.auth.get_request_auth_value()

    result = friend.friend_suggest(account_id, request.args)

    data = {
        '_status': 'OK',
        '_items': result
    }
    event_track('friend_suggest', account_id)
    return render.render_json(data), 200, {'Content-Type': 'application/json; charset=utf-8'}

@app.route('/v1/friends/search',methods=['GET'])
def route_friend_search():
    route_require_auth()
    account_id = app.auth.get_request_auth_value()

    result = friend.friend_search(account_id, request.args)

    data = {
        '_status': 'OK',
        '_items': result
    }
    event_track('friend_search', account_id)
    return render.render_json(data), 200, {'Content-Type': 'application/json; charset=utf-8'}

@app.route('/v1/friend/search',methods=['GET'])
def route_friend_search_old():
    route_require_auth()
    account_id = app.auth.get_request_auth_value()

    result = friend.friend_search(account_id, request.args)

    data = {
        '_status': 'OK',
        '_items': result
    }
    event_track('friend_search', account_id)
    return render.render_json(data), 200, {'Content-Type': 'application/json; charset=utf-8'}

@app.route('/v1/contacts',methods=['POST'])
def route_contacts():
    route_require_auth()
    account_id = app.auth.get_request_auth_value()

    result = contact.contact_save(account_id, request.json)

    data = {
        '_status': 'OK'
    }
    event_track('contacts_create', account_id)
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
    event_track('contacts', account_id)
    return render.render_json(data), 200, {'Content-Type': 'application/json; charset=utf-8'}

@app.route('/v1/contacts/<contact_id>/invite',methods=['POST'])
def route_contacts_invite(contact_id):
    route_require_auth()
    account_id = app.auth.get_request_auth_value()

    result = contact.contact_invite(account_id, ObjectId(contact_id))

    data = {
        '_status': 'OK'
    }
    event_track('contacts_invite', account_id)
    return render.render_json(data), 201, {'Content-Type': 'application/json; charset=utf-8'}

@app.route('/v1/books/<book_id>/recommend/<friend_id>',methods=['POST'])
def route_book_recommend(book_id, friend_id):
    route_require_auth()

    account_id = app.auth.get_request_auth_value()
    book_id = ObjectId(book_id)

    #@bugfix send push and notification
    result = book.book_recommend(account_id, ObjectId(friend_id), ObjectId(book_id))

    event_track('book_recommend', account_id)
    return render.render_json({'_status':'OK'}), 200, {'Content-Type': 'application/json; charset=utf-8'}

@app.route('/v1/books/<book_id>',methods=['PATCH'])
@app.route('/v1/books',methods=['POST'],defaults={'book_id': None})
def route_book_save(book_id):
    route_require_auth()
    account_id = app.auth.get_request_auth_value()
    if book_id:
        book_id = ObjectId(book_id)

    result = book.save(account_id, request.json, book_id)

    result['_status'] = 'OK'
    #@bugfix
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
    event_track('book_delete', account_id)
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

    event_track('book_like', account_id)
    return render.render_json({'_status':'OK'}), 200, {'Content-Type': 'application/json; charset=utf-8'}

@app.route('/v1/books/<book_id>/comments',methods=['POST','GET'])
def route_book_comment(book_id):
    route_require_auth()
    account_id = app.auth.get_request_auth_value()
    book_id = ObjectId(book_id)

    event_track('book_comment', account_id)

    if request.method == 'GET': #create
        comments = book.book_get_comment(book_id)

        data = {
            '_status': 'OK',
            '_items': comments
        }
        return render.render_json(data), 200, {'Content-Type': 'application/json; charset=utf-8'}

    else:
        #@bug
        data = request.json
        if ('comment' in data) and data['comment']:
            comment = book.book_create_comment(account_id, book_id, data['comment'])
            comment['_status'] = 'OK'
        return render.render_json(comment), 201, {'Content-Type': 'application/json; charset=utf-8'}


@app.route('/v1/notifications',methods=['POST','GET'])
def route_notifications():
    route_require_auth()
    account_id = app.auth.get_request_auth_value()
    event_track('notifications', account_id)
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


print "run"
if __name__ == '__main__':
    print "app.run"
    app.run()
