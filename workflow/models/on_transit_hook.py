from django.db import models
from django.db.models import CASCADE
from django.utils.translation import gettext_lazy as _

from workflow.models import TransitionMeta, Transition
from workflow.models.hook import Hook


class OnTransitHook(Hook):
    class Meta:
        unique_together = [('callback_function', 'workflowmodel', 'transition_meta', 'content_type', 'object_id', 'transition')]

    transition_meta = models.ForeignKey(TransitionMeta, verbose_name=_("Transition Meta"), related_name='on_transit_hooks', on_delete=CASCADE)
    transition = models.ForeignKey(Transition, verbose_name=_("Transition"), related_name='on_transit_hooks', null=True, blank=True, on_delete=CASCADE)
