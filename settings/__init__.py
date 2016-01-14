import os
from pymongo import MongoClient

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

#######################################################################
# Celery Task Broker settings.
#######################################################################

# Task Broker
RABBITMQ_HOST = 'localhost'
RABBITMQ_USER = 'guest'
RABBITMQ_PASSWORD = 'guest'

BROKER_HEARTBEAT = 0
BROKER_URL = "amqp://"
CELERY_RESULT_BACKEND = "amqp://"
CELERY_TASK_RESULT_EXPIRES = 1
CELERY_ACCEPT_CONTENT = ['pickle']
CELERY_IMPORTS = (
    'tasks.check_syntax',
    'tasks.check_local',
    'tasks.check_domain',
    'tasks.check_tld',
    'tasks.check_mx',
    'tasks.insert_db',
    'tasks.make_csv',
    'tasks.check_file',
    'tasks.webhook',
    'tasks.download_file'

)
CELERYD_CONCURRENCY = 8


REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
MONGO_DB = "mongodb://localhost:4321"

AWS = {
    'AWS_ACCESS_KEY_ID': 'AKIAIBMTRNWUF2TRMYVA',
    'AWS_SECRET_ACCESS_KEY': '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',
    'AWS_ASSOCIATE_TAG': 'livrio08-20'
}


EVE_SETTINGS = {
    'WTF_CSRF_ENABLED':True,
    'SECRET_KEY':'you-will-never-guess',
    'MONGO_HOST': 'localhost',
    'MONGO_PORT': 4321,
    'MONGO_DBNAME': 'livrio',
    'DEBUG': True,
    'SOFT_DELETE': True,
    'SORTING': True,
    'PAGINATION': True,
    'API_VERSION': 'v1',
    'X_EXPOSE_HEADERS': ['content-type'],
    'X_HEADERS': ['content-type'],
    'X_DOMAINS': '*',
    'EXTRA_RESPONSE_FIELDS':[],
    'HATEOAS': False,
    'AUTH_FIELD': 'account_id',

    'OPLOG': True,
    'OPLOG_AUDIT': True,
    'IF_MATCH': False,
    'VALIDATION_ERROR_AS_STRING': True,
    'DOMAIN': {
        'accounts': {
            'allowed_roles': ['superuser', 'admin'],
            'cache_control': '',
            'cache_expires': 0,
            'extra_response_fields': ['token'],
            'schema': {
                'username': {
                    'type': 'string',
                    'required': True,
                    'unique': True,
                },
                'password': {
                    'type': 'string',
                    'required': True,
                },
                'roles': {
                    'type': 'list',
                    'allowed': ['user', 'superuser', 'admin'],
                    'required': True,
                },
                'token': {
                    'type': 'string'
                }
            }
        },
        'isbn':{
            'cache_control': '',
            'cache_expires': 0,
            'schema': {
                'title': {
                    'type': 'string'
                },
                'subtitle': {
                    'type': 'string'
                },
                'isbn_10': {
                    'type': 'string'
                },
                'isbn_13': {
                    'type': 'string'
                },
                'isbn_other': {
                    'type': 'string'
                },
                'authors': {
                    'type': 'string'
                },
                'publisher': {
                    'type': 'string'
                },
                'publishedDate': {
                    'type': 'string'
                },
                'pageCount': {
                    'type': 'string'
                },
                'categories': {
                    'type': 'list'
                },
                'language': {
                    'type': 'string'
                },
                'description': {
                    'type': 'string'
                },
                'cover': {
                    'type': 'string'
                }
            }
        }
    },
    'RESOURCE_METHODS' : ['GET','POST','DELETE'],
    'ITEM_METHODS': [ 'GET','DELETE' ]
}


## MONGODB CONNECTION
#mongo_client = MongoClient(MONGO_DB)
#db = mongo_client.livrio
