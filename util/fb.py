import facebook
import requests

def profile(token):
    graph = facebook.GraphAPI(access_token=token)

    data = {};
    me = graph.get_object('/me')

    data['first_name'] = me['first_name']
    data['last_name'] = me['last_name']
    data['fullname'] = me['name']
    data['email'] = me['email']
    data['gender'] = me['gender']
    data['id'] = me['id']
    data['photo'] = "http://graph.facebook.com/{}/picture?type=large".format(me['id']);

    return data


def friends(token):
    graph = facebook.GraphAPI(access_token=token)
    friends = graph.get_connections("me","friends")

    allfriends = []
    while(friends['data']):
        try:
            for friend in friends['data']:
                allfriends.append(friend)
            friends=requests.get(friends['paging']['next']).json()
        except KeyError:
           pass

    print allfriends