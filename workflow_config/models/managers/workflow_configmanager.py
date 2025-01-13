

from django.db.models import QuerySet
from django.db.models.manager import BaseManager

from workflow_config.config import app_config


class WorkflowConfigQuerySet(QuerySet):
    def first(self):
        if app_config.IS_MSSQL:
            return next(iter(self), None)
        else:
            return super(WorkflowConfigQuerySet, self).first()


class WorkflowConfigManager(BaseManager.from_queryset(WorkflowConfigQuerySet)):
    pass
