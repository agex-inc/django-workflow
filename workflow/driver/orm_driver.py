from django.contrib import auth
from django.db.models import Min, CharField, Q, F
from django.db.models.functions import Cast
from django_cte import With

from workflow.driver.workflow_driver import Workflowworkflow
from workflow.models import TransitionApproval, PENDING


class Ormworkflow(Workflowworkflow):

    def get_available_approvals(self, as_user, is_return_transition=False):
        those_with_max_priority = With(
            TransitionApproval.objects.filter(
                workflowmodel=self.workflowmodel, status=PENDING, transition__meta__is_return_transition=is_return_transition
            ).values(
                'workflowmodel', 'object_id', 'transition'
            ).annotate(min_priority=Min('priority'))
        )

        workflowmodel_objects = With(
            self.wokflow_object_class.objects.all(),
            name="workflowmodel_object"
        )

        approvals_with_max_priority = those_with_max_priority.join(
            self._authorized_approvals(as_user),
            workflowmodel_id=those_with_max_priority.col.workflowmodel_id,
            object_id=those_with_max_priority.col.object_id,
            transition_id=those_with_max_priority.col.transition_id,
        ).with_cte(
            those_with_max_priority
        ).annotate(
            object_id_as_str=Cast('object_id', CharField(max_length=200)),
            min_priority=those_with_max_priority.col.min_priority
        ).filter(min_priority=F("priority"))

        return workflowmodel_objects.join(
            approvals_with_max_priority, object_id_as_str=Cast(workflowmodel_objects.col.pk, CharField(max_length=200))
        ).with_cte(
            workflowmodel_objects
        ).filter(transition__source_state=getattr(workflowmodel_objects.col, self.field_name + "_id"))

    def _authorized_approvals(self, as_user):
        group_q = Q()
        for g in as_user.groups.all():
            group_q = group_q | Q(groups__in=[g])

        permissions = []
        for backend in auth.get_backends():
            permissions.extend(backend.get_all_permissions(as_user))

        permission_q = Q()
        for p in permissions:
            label, codename = p.split('.')
            permission_q = permission_q | Q(permissions__content_type__app_label=label,
                                            permissions__codename=codename)

        return TransitionApproval.objects.filter(
            Q(workflowmodel=self.workflowmodel, status=PENDING) &
            (
                    (Q(transactioner__isnull=True) | Q(transactioner=as_user)) &
                    (Q(permissions__isnull=True) | permission_q) &
                    (Q(groups__isnull=True) | group_q)
            )
        )
