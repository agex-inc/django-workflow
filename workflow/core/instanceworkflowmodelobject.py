import logging

import six
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import Q, Max
from django.db.transaction import atomic
from django.utils import timezone

from workflow.config import app_config
from workflow.models import TransitionApproval, PENDING, State, APPROVED, WorkflowModel, CANCELLED, Transition, DONE, JUMPED
from workflow.signals import ApproveSignal, TransitionSignal, OnCompleteSignal
from workflow.utils.error_code import ErrorCode
from workflow.utils.exceptions import WorkflowException

LOGGER = logging.getLogger(__name__)


class InstanceWorkflowModelObject(object):

    def __init__(self, workflowmodel_object, field_name):
        self.class_workflowmodel = getattr(workflowmodel_object.__class__.workflow, field_name)
        self.workflowmodel_object = workflowmodel_object
        self.content_type = app_config.CONTENT_TYPE_CLASS.objects.get_for_model(self.workflowmodel_object)
        self.field_name = field_name
        self.workflowmodel = WorkflowModel.objects.filter(content_type=self.content_type, field_name=self.field_name).first()
        self.initialized = False

    @transaction.atomic
    def initialize_approvals(self):
        if not self.initialized:
            if self.workflowmodel and self.workflowmodel.transition_approvals.filter(workflowmodel_object=self.workflowmodel_object).count() == 0:
                transition_meta_list = self.workflowmodel.transition_metas.filter(source_state=self.workflowmodel.initial_state)
                iteration = 0
                processed_transitions = []
                while transition_meta_list:
                    for transition_meta in transition_meta_list:
                        transition = Transition.objects.create(
                            workflowmodel=self.workflowmodel,
                            workflowmodel_object=self.workflowmodel_object,
                            source_state=transition_meta.source_state,
                            destination_state=transition_meta.destination_state,
                            meta=transition_meta,
                            iteration=iteration
                        )
                        for transition_approval_meta in transition_meta.transition_approval_meta.all():
                            transition_approval = TransitionApproval.objects.create(
                                workflowmodel=self.workflowmodel,
                                workflowmodel_object=self.workflowmodel_object,
                                transition=transition,
                                priority=transition_approval_meta.priority,
                                meta=transition_approval_meta
                            )
                            transition_approval.permissions.add(*transition_approval_meta.permissions.all())
                            transition_approval.groups.add(*transition_approval_meta.groups.all())
                        processed_transitions.append(transition_meta.pk)
                    transition_meta_list = self.workflowmodel.transition_metas.filter(
                        source_state__in=transition_meta_list.values_list("destination_state", flat=True)
                    ).exclude(pk__in=processed_transitions)

                    iteration += 1
                self.initialized = True
                LOGGER.debug("Transition approvals are initialized for the workflowmodel object %s" % self.workflowmodel_object)

    @property
    def on_initial_state(self):
        return self.get_state() == self.class_workflowmodel.initial_state

    @property
    def on_final_state(self):
        return self.class_workflowmodel.final_states.filter(pk=self.get_state().pk).count() > 0

    @property
    def next_approvals(self):
        transitions = Transition.objects.filter(workflowmodel=self.workflowmodel, object_id=self.workflowmodel_object.pk, source_state=self.get_state())
        return TransitionApproval.objects.filter(transition__in=transitions)

    @property
    def recent_approval(self):
        try:
            return getattr(self.workflowmodel_object, self.field_name + "_transition_approvals").filter(transaction_date__isnull=False).latest('transaction_date')
        except TransitionApproval.DoesNotExist:
            return None

    @transaction.atomic
    def jump_to(self, state):
        def _transitions_before(iteration):
            return Transition.objects.filter(workflowmodel=self.workflowmodel, workflowmodel_object=self.workflowmodel_object, iteration__lte=iteration)

        try:
            # recent_iteration = self.recent_approval.transition.iteration if self.recent_approval else 0
            # jumped_transition = getattr(self.workflowmodel_object, self.field_name + "_transitions").filter(
            #     iteration__gte=recent_iteration, destination_state=state, status=PENDING
            # ).earliest("iteration")

            # Disabling this part to not approve the previous states, allowing the user to go back and execute again the flows if needed.
            # jumped_transitions = _transitions_before(jumped_transition.iteration).filter(status=PENDING)
            # for approval in TransitionApproval.objects.filter(pk__in=jumped_transitions.values_list("transition_approvals__pk", flat=True)):
            #     approval.status = JUMPED
            #     approval.save()
            # jumped_transitions.update(status=JUMPED)
            self.set_state(state)
            self.workflowmodel_object.save()

        except Transition.DoesNotExist:
            raise WorkflowException(ErrorCode.STATE_IS_NOT_AVAILABLE_TO_BE_JUMPED, "This state is not available to be jumped in the future of this object")

    def get_available_states(self, as_user=None):
        all_destination_state_ids = self.get_available_approvals(as_user=as_user).values_list('transition__destination_state', flat=True)
        return State.objects.filter(pk__in=all_destination_state_ids)

    def get_available_approvals(self, as_user=None, destination_state=None, include_return_transitions=False):
        qs = self.class_workflowmodel.get_available_approvals(as_user, include_return_transitions).filter(object_id=self.workflowmodel_object.pk)
        if destination_state:
            qs = qs.filter(transition__destination_state=destination_state)

        return qs

    @atomic
    def approve(self, as_user, next_state=None):
        available_approvals = self.get_available_approvals(as_user=as_user)
        number_of_available_approvals = available_approvals.count()
        if number_of_available_approvals == 0:
            raise WorkflowException(ErrorCode.NO_AVAILABLE_NEXT_STATE_FOR_USER, "There is no available approval for the user.")
        elif next_state:
            available_approvals = available_approvals.filter(transition__destination_state=next_state)
            if available_approvals.count() == 0:
                available_states = self.get_available_states(as_user)
                raise WorkflowException(ErrorCode.INVALID_NEXT_STATE_FOR_USER, "Invalid state is given(%s). Valid states is(are) %s" % (
                    next_state.__str__(), ','.join([ast.__str__() for ast in available_states])))
        elif number_of_available_approvals > 1 and not next_state:
            raise WorkflowException(ErrorCode.NEXT_STATE_IS_REQUIRED, "State must be given when there are multiple states for destination")

        approval = available_approvals.first()
        approval.status = APPROVED
        approval.transactioner = as_user
        approval.transaction_date = timezone.now()
        approval.previous = self.recent_approval
        approval.save()

        if next_state:
            self.cancel_impossible_future(approval)

        has_transit = False
        if approval.peers.filter(status=PENDING).count() == 0:
            approval.transition.status = DONE
            approval.transition.save()
            previous_state = self.get_state()
            self.set_state(approval.transition.destination_state)
            has_transit = True
            if self._check_if_it_cycled(approval.transition):
                self._re_create_cycled_path(approval.transition)
            LOGGER.debug("WorkflowModel object %s is proceeded for next transition. Transition: %s -> %s" % (
                self.workflowmodel_object, previous_state, self.get_state()))

        with self._approve_signal(approval), self._transition_signal(has_transit, approval), self._on_complete_signal():
            self.workflowmodel_object.save()

    @atomic
    def cancel_impossible_future(self, approved_approval):
        transition = approved_approval.transition

        possible_transition_ids = {transition.pk}

        possible_next_states = {transition.destination_state.label}
        while possible_next_states:
            possible_transitions = Transition.objects.filter(
                workflowmodel=self.workflowmodel,
                object_id=self.workflowmodel_object.pk,
                status=PENDING,
                source_state__label__in=possible_next_states
            ).exclude(pk__in=possible_transition_ids)

            possible_transition_ids.update(set(possible_transitions.values_list("pk", flat=True)))

            possible_next_states = set(possible_transitions.values_list("destination_state__label", flat=True))

        cancelled_transitions = Transition.objects.filter(
            workflowmodel=self.workflowmodel,
            object_id=self.workflowmodel_object.pk,
            status=PENDING,
            iteration__gte=transition.iteration
        ).exclude(pk__in=possible_transition_ids)

        TransitionApproval.objects.filter(transition__in=cancelled_transitions).update(status=CANCELLED)
        cancelled_transitions.update(status=CANCELLED)

    def _approve_signal(self, approval):
        return ApproveSignal(self.workflowmodel_object, self.field_name, approval)

    def _transition_signal(self, has_transit, approval):
        return TransitionSignal(has_transit, self.workflowmodel_object, self.field_name, approval)

    def _on_complete_signal(self):
        return OnCompleteSignal(self.workflowmodel_object, self.field_name)

    @property
    def _content_type(self):
        return ContentType.objects.get_for_model(self.workflowmodel_object)

    def _to_key(self, source_state):
        return str(self.content_type.pk) + self.field_name + source_state.label

    def _check_if_it_cycled(self, done_transition):
        qs = Transition.objects.filter(
            workflowmodel_object=self.workflowmodel_object,
            workflowmodel=self.class_workflowmodel.workflowmodel,
            source_state=done_transition.destination_state
        )

        return qs.filter(status=DONE).count() > 0 and qs.filter(status=PENDING).count() == 0

    def _get_transition_images(self, source_states):
        meta_max_iteration = Transition.objects.filter(
            workflowmodel=self.workflowmodel,
            workflowmodel_object=self.workflowmodel_object,
            source_state__pk__in=source_states,
        ).values_list("meta").annotate(max_iteration=Max("iteration"))

        return Transition.objects.filter(
            Q(workflowmodel=self.workflowmodel, object_id=self.workflowmodel_object.pk) &
            six.moves.reduce(lambda agg, q: q | agg, [Q(meta__id=meta_id, iteration=max_iteration) for meta_id, max_iteration in meta_max_iteration], Q(pk=-1))
        )

    def _re_create_cycled_path(self, done_transition):
        old_transitions = self._get_transition_images([done_transition.destination_state.pk])

        iteration = done_transition.iteration + 1
        regenerated_transitions = set()
        while old_transitions:
            for old_transition in old_transitions:
                cycled_transition = Transition.objects.create(
                    source_state=old_transition.source_state,
                    destination_state=old_transition.destination_state,
                    workflowmodel=old_transition.workflowmodel,
                    object_id=old_transition.workflowmodel_object.pk,
                    content_type=old_transition.content_type,
                    status=PENDING,
                    iteration=iteration,
                    meta=old_transition.meta
                )

                for old_approval in old_transition.transition_approvals.all():
                    cycled_approval = TransitionApproval.objects.create(
                        transition=cycled_transition,
                        workflowmodel=old_approval.workflowmodel,
                        object_id=old_approval.workflowmodel_object.pk,
                        content_type=old_approval.content_type,
                        priority=old_approval.priority,
                        status=PENDING,
                        meta=old_approval.meta
                    )
                    cycled_approval.permissions.set(old_approval.permissions.all())
                    cycled_approval.groups.set(old_approval.groups.all())

            regenerated_transitions.add((old_transition.source_state, old_transition.destination_state))

            old_transitions = self._get_transition_images(old_transitions.values_list("destination_state__pk", flat=True)).exclude(
                six.moves.reduce(lambda agg, q: q | agg, [Q(source_state=source_state, destination_state=destination_state) for source_state, destination_state in regenerated_transitions], Q(pk=-1))
            )

            iteration += 1

    def get_state(self):
        return getattr(self.workflowmodel_object, self.field_name)

    def set_state(self, state):
        return setattr(self.workflowmodel_object, self.field_name, state)
