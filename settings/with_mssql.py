from time import sleep
from uuid import uuid4

import pyodbc

from .base import *

DB_DNewName = 'ODBC newname 17 for SQL Server'
DB_HOST = os.environ['MCR_MICROSOFT_COM_MSSQL_SERVER_HOST']
DB_PORT = os.environ['MCR_MICROSOFT_COM_MSSQL_SERVER_1433_TCP']
DB_USER = 'sa'
DB_PASSWORD = 'NewName@Credentials'
sleep(10)
db_connection = pyodbc.connect(f"DNewName={DB_DNewName};SERVER={DB_HOST},{DB_PORT};DATABASE=master;UID={DB_USER};PWD={DB_PASSWORD}", autocommit=True)
cursor = db_connection.cursor()
cursor.execute(
    """
     If(db_id(N'newname') IS NULL)
    BEGIN
        CREATE DATABASE newname
    END;
    """)

DATABASES = {
    'default': {
        'ENGINE': 'sql_server.pyodbc',
        'NAME': 'newname',
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
        'TEST': {
            'NAME': 'newname' + str(uuid4()),
        },
        'OPTIONS': {
            'newname': DB_DNewName
        },
    }
}

INSTALLED_APPS += (
    'newname.tests',
)

# if django.get_version() >= '1.9.0':
#     MIGRATION_MODULES = DisableMigrations()
