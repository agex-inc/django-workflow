

from django.db.models import QuerySet
from django.db.models.manager import BaseManager

from newname.config import app_config


class NewNameQuerySet(QuerySet):
    def first(self):
        if app_config.IS_MSSQL:
            return next(iter(self), None)
        else:
            return super(NewNameQuerySet, self).first()


class NewNameManager(BaseManager.from_queryset(NewNameQuerySet)):
    pass
