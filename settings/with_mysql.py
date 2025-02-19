from uuid import uuid4

from .base import *

DB_HOST = os.environ['MYSQL_HOST']
DB_PORT = os.environ['MYSQL_3306_TCP_PORT']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'workflow',
        'USER': 'root',
        'PASSWORD': 'workflow',
        'HOST': DB_HOST,
        'PORT': DB_PORT,
        'TEST': {
            'NAME': 'workflow' + str(uuid4()),
        },
    }
}

INSTALLED_APPS += (
    'workflow.tests',
)

# if django.get_version() >= '1.9.0':
#     MIGRATION_MODULES = DisableMigrations()
