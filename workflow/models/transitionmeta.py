from __future__ import unicode_literals

from django.db import models
from django.db.models import PROTECT
from django.utils.translation import gettext_lazy as _

from workflow.models import State, WorkflowModel
from workflow.models.base_model import BaseModel


class TransitionMeta(BaseModel):
    class Meta:
        app_label = 'workflow'
        verbose_name = _("Transition Meta")
        verbose_name_plural = _("Transition Meta")
        unique_together = [('workflowmodel', 'source_state', 'destination_state')]

    workflowmodel = models.ForeignKey(WorkflowModel, verbose_name=_("WorkflowModel"), related_name='transition_metas', on_delete=PROTECT)
    source_state = models.ForeignKey(State, verbose_name=_("Source State"), related_name='transition_meta_as_source', on_delete=PROTECT)
    destination_state = models.ForeignKey(State, verbose_name=_("Destination State"), related_name='transition_meta_as_destination', on_delete=PROTECT)

    def __str__(self):
        return 'Field Name:%s, %s -> %s' % (
            self.workflowmodel,
            self.source_state,
            self.destination_state
        )
