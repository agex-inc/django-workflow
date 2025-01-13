from time import sleep
from uuid import uuid4

import pyodbc

from .base import *

DB_DWorkflowConfig = 'ODBC workflow_config 17 for SQL Server'
DB_HOST = os.environ['MCR_MICROSOFT_COM_MSSQL_SERVER_HOST']
DB_PORT = os.environ['MCR_MICROSOFT_COM_MSSQL_SERVER_1433_TCP']
DB_USER = 'sa'
DB_PASSWORD = 'WorkflowConfig@Credentials'
sleep(10)
db_connection = pyodbc.connect(f"DWorkflowConfig={DB_DWorkflowConfig};SERVER={DB_HOST},{DB_PORT};DATABASE=master;UID={DB_USER};PWD={DB_PASSWORD}", autocommit=True)
cursor = db_connection.cursor()
cursor.execute(
    """
     If(db_id(N'workflow_config') IS NULL)
    BEGIN
        CREATE DATABASE workflow_config
    END;
    """)

DATABASES = {
    'default': {
        'ENGINE': 'sql_server.pyodbc',
        'NAME': 'workflow_config',
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
        'TEST': {
            'NAME': 'workflow_config' + str(uuid4()),
        },
        'OPTIONS': {
            'workflow_config': DB_DWorkflowConfig
        },
    }
}

INSTALLED_APPS += (
    'workflow_config.tests',
)

# if django.get_version() >= '1.9.0':
#     MIGRATION_MODULES = DisableMigrations()
