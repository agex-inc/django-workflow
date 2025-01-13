from django.conf import settings

from django.db import models
from django.utils.translation import gettext_lazy as _

from workflow.models.managers.workflowmanager import WorkflowManager

AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


class BaseModel(models.Model):
    objects = WorkflowManager()

    date_created = models.DateTimeField(_('Date Created'), null=True, blank=True, auto_now_add=True)
    date_updated = models.DateTimeField(_('Date Updated'), null=True, blank=True, auto_now=True)

    class Meta:
        app_label = 'workflow'
        abstract = True

    def details(self):
        return {'pk': self.pk}
