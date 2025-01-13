from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from hamcrest import assert_that, has_length, has_item, has_property, none

from workflow.models import TransitionApproval, APPROVED, PENDING
from workflow.tests.models import BasicTestModel
# noinspection PyMethodMayBeStatic
from workflowtest.flowbuilder import RawState, FlowBuilder, AuthorizationPolicyBuilder


class TransitionApprovalMetaModelTest(TestCase):

    def test_shouldNotDeleteApprovedTransitionWhenDeleted(self):
        content_type = ContentType.objects.get_for_model(BasicTestModel)

        state1 = RawState("state_1")
        state2 = RawState("state_2")

        authorization_policies = [AuthorizationPolicyBuilder().build()]
        flow = FlowBuilder("my_field", content_type) \
            .with_transition(state1, state2, authorization_policies) \
            .build()

        TransitionApproval.objects.filter(workflowmodel=flow.workflowmodel).update(status=APPROVED)
        approvals = TransitionApproval.objects.filter(workflowmodel=flow.workflowmodel)
        assert_that(approvals, has_length(1))
        assert_that(approvals, has_item(has_property("meta", flow.transitions_approval_metas[0])))

        flow.transitions_approval_metas[0].delete()

        approvals = TransitionApproval.objects.filter(workflowmodel=flow.workflowmodel)
        assert_that(approvals, has_length(1))
        assert_that(approvals, has_item(has_property("meta", none())))

    def test_shouldNotDeletePendingTransitionWhenDeleted(self):
        content_type = ContentType.objects.get_for_model(BasicTestModel)

        state1 = RawState("state_1")
        state2 = RawState("state_2")

        authorization_policies = [AuthorizationPolicyBuilder().build()]
        flow = FlowBuilder("my_field", content_type) \
            .with_transition(state1, state2, authorization_policies) \
            .build()

        TransitionApproval.objects.filter(workflowmodel=flow.workflowmodel).update(status=PENDING)
        assert_that(TransitionApproval.objects.filter(workflowmodel=flow.workflowmodel), has_length(1))

        flow.transitions_approval_metas[0].delete()

        assert_that(TransitionApproval.objects.filter(workflowmodel=flow.workflowmodel), has_length(0))
