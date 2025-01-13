from time import sleep
from uuid import uuid4

import pyodbc

from .base import *

DB_DWorkflow = 'ODBC workflow 17 for SQL Server'
DB_HOST = os.environ['MCR_MICROSOFT_COM_MSSQL_SERVER_HOST']
DB_PORT = os.environ['MCR_MICROSOFT_COM_MSSQL_SERVER_1433_TCP']
DB_USER = 'sa'
DB_PASSWORD = 'Workflow@Credentials'
sleep(10)
db_connection = pyodbc.connect(f"DWorkflow={DB_DWorkflow};SERVER={DB_HOST},{DB_PORT};DATABASE=master;UID={DB_USER};PWD={DB_PASSWORD}", autocommit=True)
cursor = db_connection.cursor()
cursor.execute(
    """
     If(db_id(N'workflow') IS NULL)
    BEGIN
        CREATE DATABASE workflow
    END;
    """)

DATABASES = {
    'default': {
        'ENGINE': 'sql_server.pyodbc',
        'NAME': 'workflow',
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
        'TEST': {
            'NAME': 'workflow' + str(uuid4()),
        },
        'OPTIONS': {
            'workflow': DB_DWorkflow
        },
    }
}

INSTALLED_APPS += (
    'workflow.tests',
)

# if django.get_version() >= '1.9.0':
#     MIGRATION_MODULES = DisableMigrations()
