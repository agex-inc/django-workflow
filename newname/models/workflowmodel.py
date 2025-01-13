from django.db import models
from django.db.models import PROTECT
from django.utils.translation import gettext_lazy as _

from newname.config import app_config
from newname.models import BaseModel, State
from newname.models.managers.workflowmodelmetada import WorkflowModelManager


class WorkflowModel(BaseModel):
    class Meta:
        app_label = 'newname'
        verbose_name = _("WorkflowModel")
        verbose_name_plural = _("WorkflowModels")
        unique_together = [("content_type", "field_name")]

    objects = WorkflowModelManager()

    content_type = models.ForeignKey(app_config.CONTENT_TYPE_CLASS, verbose_name=_('Content Type'), on_delete=PROTECT)
    field_name = models.CharField(_("Field Name"), max_length=200)
    initial_state = models.ForeignKey(State, verbose_name=_("Initial State"), related_name='workflowmodel_this_set_as_initial_state', on_delete=PROTECT)

    def natural_key(self):
        return self.content_type, self.field_name

    def __str__(self):
        return "%s.%s" % (self.content_type.model, self.field_name)
