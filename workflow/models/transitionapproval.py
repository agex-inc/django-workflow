import logging

from django.db.models import CASCADE, PROTECT, SET_NULL
from mptt.fields import TreeOneToOneField

from workflow.models import TransitionApprovalMeta, WorkflowModel
from workflow.models.transition import Transition

try:
    from django.contrib.contenttypes.fields import GenericForeignKey
except ImportError:
    from django.contrib.contenttypes.generic import GenericForeignKey

from django.db import models
from django.utils.translation import gettext_lazy as _

from workflow.models.base_model import BaseModel
from workflow.models.managers.transitionapproval import TransitionApprovalManager
from workflow.config import app_config

PENDING = "pending"
APPROVED = "approved"
JUMPED = "jumped"
CANCELLED = "cancelled"

STATUSES = [
    (PENDING, _('Pending')),
    (APPROVED, _('Approved')),
    (CANCELLED, _('Cancelled')),
    (JUMPED, _('Jumped')),
]

LOGGER = logging.getLogger(__name__)


class TransitionApproval(BaseModel):
    class Meta:
        app_label = 'workflow'
        verbose_name = _("Transition Approval")
        verbose_name_plural = _("Transition Approvals")

    objects = TransitionApprovalManager()

    content_type = models.ForeignKey(app_config.CONTENT_TYPE_CLASS, verbose_name=_('Content Type'), on_delete=CASCADE)

    object_id = models.CharField(max_length=50, verbose_name=_('Related Object'))
    workflowmodel_object = GenericForeignKey('content_type', 'object_id')

    meta = models.ForeignKey(TransitionApprovalMeta, verbose_name=_('Meta'), related_name="transition_approvals", null=True, blank=True, on_delete=SET_NULL)
    workflowmodel = models.ForeignKey(WorkflowModel, verbose_name=_("WorkflowModel"), related_name='transition_approvals', on_delete=PROTECT)

    transition = models.ForeignKey(Transition, verbose_name=_("Transition"), related_name='transition_approvals', on_delete=PROTECT)

    transactioner = models.ForeignKey(app_config.USER_CLASS, verbose_name=_('Transactioner'), null=True, blank=True, on_delete=SET_NULL)
    transaction_date = models.DateTimeField(null=True, blank=True)

    status = models.CharField(_('Status'), choices=STATUSES, max_length=100, default=PENDING)

    permissions = models.ManyToManyField(app_config.PERMISSION_CLASS, verbose_name=_('Permissions'))
    groups = models.ManyToManyField(app_config.GROUP_CLASS, verbose_name=_('Groups'))
    priority = models.IntegerField(default=0, verbose_name=_('Priority'))

    previous = TreeOneToOneField("self", verbose_name=_('Previous Transition'), related_name="next_transition", null=True, blank=True, on_delete=CASCADE)

    @property
    def peers(self):
        return TransitionApproval.objects.filter(
            workflowmodel_object=self.workflowmodel_object,
            workflowmodel=self.workflowmodel,
            transition=self.transition,
        ).exclude(pk=self.pk)
