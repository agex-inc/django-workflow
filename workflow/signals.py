import logging

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.dispatch import Signal

from workflow.models import WorkflowModel
from workflow.models.hook import BEFORE, AFTER
from workflow.models.on_approved_hook import OnApprovedHook
from workflow.models.on_complete_hook import OnCompleteHook
from workflow.models.on_transit_hook import OnTransitHook

pre_on_complete = Signal()
post_on_complete = Signal()

pre_transition = Signal()
post_transition = Signal()

pre_approve = Signal()
post_approve = Signal()

LOGGER = logging.getLogger(__name__)


class TransitionSignal(object):
    def __init__(self, status, workflowmodel_object, field_name, transition_approval):
        self.status = status
        self.workflowmodel_object = workflowmodel_object
        self.field_name = field_name
        self.transition_approval = transition_approval
        self.content_type = ContentType.objects.get_for_model(self.workflowmodel_object.__class__)
        self.workflowmodel = WorkflowModel.objects.get(content_type=self.content_type, field_name=self.field_name)

    def __enter__(self):
        if self.status:
            for hook in OnTransitHook.objects.filter(
                    (Q(object_id__isnull=True) | Q(object_id=self.workflowmodel_object.pk, content_type=self.content_type)) &
                    (Q(transition__isnull=True) | Q(transition=self.transition_approval.transition)) &
                    Q(
                        workflowmodel__field_name=self.field_name,
                        transition_meta=self.transition_approval.transition.meta,
                        hook_type=BEFORE
                    )
            ):
                hook.execute(self._get_context(BEFORE), hook)

            LOGGER.debug("The signal that is fired right before the transition ( %s ) happened for %s"
                         % (self.transition_approval.transition, self.workflowmodel_object))

    def __exit__(self, type, value, traceback):
        if self.status:
            for hook in OnTransitHook.objects.filter(
                    (Q(object_id__isnull=True) | Q(object_id=self.workflowmodel_object.pk, content_type=self.content_type)) &
                    (Q(transition__isnull=True) | Q(transition=self.transition_approval.transition)) &
                    Q(
                        workflowmodel=self.workflowmodel,
                        transition_meta=self.transition_approval.transition.meta,
                        hook_type=AFTER
                    )
            ):
                hook.execute(self._get_context(AFTER, hook))
            LOGGER.debug("The signal that is fired right after the transition ( %s) happened for %s"
                         % (self.transition_approval.transition, self.workflowmodel_object))

    def _get_context(self, when, hook):
        return {
            "hook": {
                "type": "on-transit",
                "when": when,
                "payload": {
                    "workflowmodel": self.workflowmodel,
                    "workflowmodel_object": self.workflowmodel_object,
                    "transition_approval": self.transition_approval,
                    "function": hook.callback_function
                }
            },
        }


class ApproveSignal(object):
    def __init__(self, workflowmodel_object, field_name, transition_approval):
        self.workflowmodel_object = workflowmodel_object
        self.field_name = field_name
        self.transition_approval = transition_approval
        self.content_type = ContentType.objects.get_for_model(self.workflowmodel_object.__class__)
        self.workflowmodel = WorkflowModel.objects.get(content_type=self.content_type, field_name=self.field_name)

#  Unncomment this to enable the before signal
    def __enter__(self):
        pass
    #     print("Enter for the approve signal")
    #     for hook in OnApprovedHook.objects.filter(
    #             (Q(object_id__isnull=True) | Q(object_id=self.workflowmodel_object.pk, content_type=self.content_type)) &
    #             (Q(transition_approval__isnull=True) | Q(transition_approval=self.transition_approval)) &
    #             Q(
    #                 workflowmodel__field_name=self.field_name,
    #                 transition_approval_meta=self.transition_approval.meta,
    #                 hook_type=BEFORE
    #             )
    #     ):
    #         print("Executing the hook, before")
    #         hook.execute(self._get_context(BEFORE))

    #     LOGGER.debug("The signal that is fired right before a transition approval is approved for %s due to transition %s -> %s" % (
    #         self.workflowmodel_object, self.transition_approval.transition.source_state.label, self.transition_approval.transition.destination_state.label))

    def __exit__(self, type, value, traceback):
        for hook in OnApprovedHook.objects.filter(
                (Q(object_id__isnull=True) | Q(object_id=self.workflowmodel_object.pk, content_type=self.content_type)) &
                (Q(transition_approval__isnull=True) | Q(transition_approval=self.transition_approval)) &
                Q(
                    workflowmodel__field_name=self.field_name,
                    transition_approval_meta=self.transition_approval.meta,
                )
        ):
            hook.execute(self._get_context(AFTER, hook))

        LOGGER.debug("The signal that is fired right after a transition approval is approved for %s due to transition %s -> %s" % (
            self.workflowmodel_object, self.transition_approval.transition.source_state.label, self.transition_approval.transition.destination_state.label))

    def _get_context(self, when, hook):
        return {
            "hook": {
                "type": "on-approved",
                "when": when,
                "payload": {
                    "workflowmodel": self.workflowmodel,
                    "workflowmodel_object": self.workflowmodel_object,
                    "transition_approval": self.transition_approval,
                    "function": hook.callback_function
                }
            },
        }


class OnCompleteSignal(object):
    def __init__(self, workflowmodel_object, field_name):
        self.workflowmodel_object = workflowmodel_object
        self.field_name = field_name
        self.workflowmodel = getattr(self.workflowmodel_object.workflow, self.field_name)
        self.status = self.workflowmodel.on_final_state
        self.content_type = ContentType.objects.get_for_model(self.workflowmodel_object.__class__)
        self.workflowmodel = WorkflowModel.objects.get(content_type=self.content_type, field_name=self.field_name)

    def __enter__(self):
        if self.status:
            for hook in OnCompleteHook.objects.filter(
                    (Q(object_id__isnull=True) | Q(object_id=self.workflowmodel_object.pk, content_type=self.content_type)) &
                    Q(
                        workflowmodel__field_name=self.field_name,
                        hook_type=BEFORE
                    )
            ):
                hook.execute(self._get_context(BEFORE, hook))
            LOGGER.debug("The signal that is fired right before the workflowmodel of %s is complete" % self.workflowmodel_object)

    def __exit__(self, type, value, traceback):
        if self.status:
            for hook in OnCompleteHook.objects.filter(
                    (Q(object_id__isnull=True) | Q(object_id=self.workflowmodel_object.pk, content_type=self.content_type)) &
                    Q(
                        workflowmodel__field_name=self.field_name,
                        hook_type=AFTER
                    )
            ):
                hook.execute(self._get_context(AFTER, hook))
            LOGGER.debug("The signal that is fired right after the workflowmodel of %s is complete" % self.workflowmodel_object)

    def _get_context(self, when, hook):
        return {
            "hook": {
                "type": "on-complete",
                "when": when,
                "payload": {
                    "workflowmodel": self.workflowmodel,
                    "workflowmodel_object": self.workflowmodel_object,
                    "function": hook.callback_function
                }
            },
        }
