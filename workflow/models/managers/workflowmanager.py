

from django.db.models import QuerySet
from django.db.models.manager import BaseManager

from workflow.config import app_config


class WorkflowQuerySet(QuerySet):
    def first(self):
        if app_config.IS_MSSQL:
            return next(iter(self), None)
        else:
            return super(WorkflowQuerySet, self).first()


class WorkflowManager(BaseManager.from_queryset(WorkflowQuerySet)):
    pass
