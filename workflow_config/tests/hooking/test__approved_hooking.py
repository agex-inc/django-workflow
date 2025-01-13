from django.contrib.contenttypes.models import ContentType
from hamcrest import equal_to, assert_that, none, has_entry, all_of, has_key, has_length, is_not

from workflow_config.models import TransitionApproval
from workflow_config.models.factories import PermissionObjectFactory, UserObjectFactory
from workflow_config.models.hook import BEFORE
from workflow_config.tests.hooking.base_hooking_test import BaseHookingTest
from workflow_config.tests.models import BasicTestModel
# noinspection DuplicatedCode
from workflow_configtest.flowbuilder import RawState, AuthorizationPolicyBuilder, FlowBuilder


class ApprovedHooking(BaseHookingTest):

    def test_shouldInvokeCallbackThatIsRegisteredWithInstanceWhenAnApprovingHappens(self):
        authorized_permission = PermissionObjectFactory()
        authorized_user = UserObjectFactory(user_permissions=[authorized_permission])

        content_type = ContentType.objects.get_for_model(BasicTestModel)

        state1 = RawState("state_1")
        state2 = RawState("state_2")

        authorization_policies = [
            AuthorizationPolicyBuilder().with_priority(0).with_permission(authorized_permission).build(),
            AuthorizationPolicyBuilder().with_priority(1).with_permission(authorized_permission).build(),
        ]
        flow = FlowBuilder("my_field", content_type) \
            .with_transition(state1, state2, authorization_policies) \
            .build()

        workflow_object = flow.objects[0]

        self.hook_pre_approve(flow.workflow, flow.transitions_approval_metas[0], workflow_object=workflow_object)

        assert_that(self.get_output(), none())

        assert_that(workflow_object.my_field, equal_to(flow.get_state(state1)))
        workflow_object.workflow_config.my_field.approve(as_user=authorized_user)
        assert_that(workflow_object.my_field, equal_to(flow.get_state(state1)))

        output = self.get_output()
        assert_that(output, has_length(1))
        assert_that(output[0], has_key("hook"))
        assert_that(output[0]["hook"], has_entry("type", "on-approved"))
        assert_that(output[0]["hook"], has_entry("when", BEFORE))
        assert_that(output[0]["hook"], has_entry(
            "payload",
            all_of(
                has_entry(equal_to("workflow_object"), equal_to(workflow_object)),
                has_entry(equal_to("transition_approval"), equal_to(flow.transitions_approval_metas[0].transition_approvals.all().first()))
            )
        ))

        workflow_object.workflow_config.my_field.approve(as_user=authorized_user)
        assert_that(workflow_object.my_field, equal_to(flow.get_state(state2)))

        output = self.get_output()
        assert_that(output, has_length(1))
        assert_that(output[0], has_key("hook"))
        assert_that(output[0]["hook"], has_entry("type", "on-approved"))
        assert_that(output[0]["hook"], has_entry("when", BEFORE))
        assert_that(output[0]["hook"], has_entry(
            "payload",
            all_of(
                has_entry(equal_to("workflow_object"), equal_to(workflow_object)),
                has_entry(equal_to("transition_approval"), equal_to(flow.transitions_approval_metas[0].transition_approvals.all().first()))

            )
        ))

    def test_shouldInvokeCallbackThatIsRegisteredWithoutInstanceWhenAnApprovingHappens(self):
        authorized_permission = PermissionObjectFactory()
        authorized_user = UserObjectFactory(user_permissions=[authorized_permission])
        content_type = ContentType.objects.get_for_model(BasicTestModel)

        state1 = RawState("state1")
        state2 = RawState("state2")

        authorization_policies = [
            AuthorizationPolicyBuilder().with_priority(0).with_permission(authorized_permission).build(),
            AuthorizationPolicyBuilder().with_priority(1).with_permission(authorized_permission).build(),
        ]
        flow = FlowBuilder("my_field", content_type) \
            .with_transition(state1, state2, authorization_policies) \
            .build()

        workflow_object = flow.objects[0]

        self.hook_pre_approve(flow.workflow, flow.transitions_approval_metas[0])

        assert_that(self.get_output(), none())

        assert_that(workflow_object.my_field, equal_to(flow.get_state(state1)))
        workflow_object.workflow_config.my_field.approve(as_user=authorized_user)
        assert_that(workflow_object.my_field, equal_to(flow.get_state(state1)))

        output = self.get_output()
        assert_that(output, has_length(1))
        assert_that(output[0], has_key("hook"))
        assert_that(output[0]["hook"], has_entry("type", "on-approved"))
        assert_that(output[0]["hook"], has_entry("when", BEFORE))
        assert_that(output[0]["hook"], has_entry(
            "payload",
            all_of(
                has_entry(equal_to("workflow_object"), equal_to(workflow_object)),
                has_entry(equal_to("transition_approval"), equal_to(flow.transitions_approval_metas[0].transition_approvals.all().first()))

            )
        ))

        workflow_object.workflow_config.my_field.approve(as_user=authorized_user)
        assert_that(workflow_object.my_field, equal_to(flow.get_state(state2)))

        output = self.get_output()
        assert_that(output, has_length(1))
        assert_that(output[0], has_key("hook"))
        assert_that(output[0]["hook"], has_entry("type", "on-approved"))
        assert_that(output[0]["hook"], has_entry("when", BEFORE))
        assert_that(output[0]["hook"], has_entry(
            "payload",
            all_of(
                has_entry(equal_to("workflow_object"), equal_to(workflow_object)),
                has_entry(equal_to("transition_approval"), equal_to(flow.transitions_approval_metas[0].transition_approvals.all().first()))

            )
        ))

    def test_shouldInvokeCallbackForTheOnlyGivenApproval(self):
        authorized_permission = PermissionObjectFactory()
        authorized_user = UserObjectFactory(user_permissions=[authorized_permission])

        content_type = ContentType.objects.get_for_model(BasicTestModel)

        state1 = RawState("state1")
        state2 = RawState("state2")
        state3 = RawState("state3")

        authorization_policies = [
            AuthorizationPolicyBuilder().with_permission(authorized_permission).build(),
        ]
        flow = FlowBuilder("my_field", content_type) \
            .with_transition(state1, state2, authorization_policies) \
            .with_transition(state2, state3, authorization_policies) \
            .with_transition(state3, state1, authorization_policies) \
            .build()

        workflow_object = flow.objects[0]
        workflow_object.workflow_config.my_field.approve(as_user=authorized_user)
        workflow_object.workflow_config.my_field.approve(as_user=authorized_user)
        workflow_object.workflow_config.my_field.approve(as_user=authorized_user)

        assert_that(TransitionApproval.objects.filter(meta=flow.transitions_approval_metas[0]), has_length(2))
        first_approval = TransitionApproval.objects.filter(meta=flow.transitions_approval_metas[0], transition__iteration=0).first()
        assert_that(first_approval, is_not(none()))

        self.hook_pre_approve(flow.workflow, flow.transitions_approval_metas[0], transition_approval=first_approval)

        output = self.get_output()
        assert_that(output, none())

        workflow_object.workflow_config.my_field.approve(as_user=authorized_user)

        output = self.get_output()
        assert_that(output, none())
