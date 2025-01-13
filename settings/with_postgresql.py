from uuid import uuid4

from .base import *

DB_HOST = os.environ['POSTGRES_HOST']
DB_PORT = os.environ['POSTGRES_5432_TCP_PORT']
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'newname',
        'USER': 'newname',
        'PASSWORD': 'newname',
        'HOST': DB_HOST,
        'PORT': DB_PORT,
        'TEST': {
            'NAME': 'newname' + str(uuid4()),

        },
    }
}

INSTALLED_APPS += (
    'newname.tests',
)

# if django.get_version() >= '1.9.0':
#     MIGRATION_MODULES = DisableMigrations()
