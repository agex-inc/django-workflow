from uuid import uuid4

from .base import *

DB_HOST = os.environ['POSTGRES_HOST']
DB_PORT = os.environ['POSTGRES_5432_TCP_PORT']
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'workflow_config',
        'USER': 'workflow_config',
        'PASSWORD': 'workflow_config',
        'HOST': DB_HOST,
        'PORT': DB_PORT,
        'TEST': {
            'NAME': 'workflow_config' + str(uuid4()),

        },
    }
}

INSTALLED_APPS += (
    'workflow_config.tests',
)

# if django.get_version() >= '1.9.0':
#     MIGRATION_MODULES = DisableMigrations()
