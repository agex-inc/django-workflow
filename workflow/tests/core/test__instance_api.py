from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from hamcrest import assert_that, equal_to, has_item, has_property, raises, calling, has_length, is_not, all_of, none

from workflow.models import TransitionApproval, PENDING, CANCELLED, APPROVED, Transition, JUMPED
from workflow.models.factories import UserObjectFactory, PermissionObjectFactory
from workflow.tests.matchers import has_approval
from workflow.tests.models import BasicTestModel, ModelWithTwoStateFields, ModelWithStringPrimaryKey
from workflow.tests.models.factories import ModelWithTwoStateFieldsObjectFactory
from workflow.utils.exceptions import WorkflowException
# noinspection PyMethodMayBeStatic,DuplicatedCode
from workflowtest.flowbuilder import FlowBuilder, AuthorizationPolicyBuilder, RawState


class InstanceApiTest(TestCase):

    def __init__(self, *args, **kwargs):
        super(InstanceApiTest, self).__init__(*args, **kwargs)
        self.content_type = ContentType.objects.get_for_model(BasicTestModel)

    def test_shouldNotReturnOtherObjectsApprovalsForTheAuthorizedUser(self):
        authorized_permission = PermissionObjectFactory()
        authorized_user = UserObjectFactory(user_permissions=[authorized_permission])
        state1 = RawState("state1")
        state2 = RawState("state2")

        authorization_policies = [AuthorizationPolicyBuilder().with_permission(authorized_permission).build()]
        flow = FlowBuilder("my_field", self.content_type) \
            .with_transition(state1, state2, authorization_policies) \
            .with_objects(2) \
            .build()

        workflowmodel_object1 = flow.objects[0]
        workflowmodel_object2 = flow.objects[1]

        available_approvals = workflowmodel_object1.workflow.my_field.get_available_approvals(as_user=authorized_user)
        assert_that(available_approvals, has_length(1))
        assert_that(list(available_approvals), has_item(
            has_property("workflowmodel_object", workflowmodel_object1)
        ))
        assert_that(list(available_approvals), has_item(
            is_not(has_property("workflowmodel_object", workflowmodel_object2))
        ))

    def test_shouldNotAllowUnauthorizedUserToProceedToNextState(self):
        unauthorized_user = UserObjectFactory()
        authorized_permission = PermissionObjectFactory()

        state1 = RawState("state1")
        state2 = RawState("state2")

        authorization_policies = [AuthorizationPolicyBuilder().with_permission(authorized_permission).build()]
        flow = FlowBuilder("my_field", self.content_type) \
            .with_transition(state1, state2, authorization_policies) \
            .build()

        workflowmodel_object = flow.objects[0]

        assert_that(
            calling(workflowmodel_object.workflow.my_field.approve).with_args(as_user=unauthorized_user),
            raises(WorkflowException, "There is no available approval for the user")
        )

    def test_shouldAllowAuthorizedUserToProceedToNextState(self):
        authorized_permission = PermissionObjectFactory()
        authorized_user = UserObjectFactory(user_permissions=[authorized_permission])

        state1 = RawState("state1")
        state2 = RawState("state2")

        authorization_policies = [AuthorizationPolicyBuilder().with_permission(authorized_permission).build()]
        flow = FlowBuilder("my_field", self.content_type) \
            .with_transition(state1, state2, authorization_policies) \
            .build()

        workflowmodel_object = flow.objects[0]

        assert_that(workflowmodel_object.my_field, equal_to(flow.get_state(state1)))
        workflowmodel_object.workflow.my_field.approve(as_user=authorized_user)
        assert_that(workflowmodel_object.my_field, equal_to(flow.get_state(state2)))

    def test_shouldNotLetUserWhosePriorityComesLaterApproveProceed(self):
        manager_permission = PermissionObjectFactory()
        team_leader_permission = PermissionObjectFactory()

        manager = UserObjectFactory(user_permissions=[manager_permission])

        state1 = RawState("state1")
        state2 = RawState("state2")

        authorization_policies = [
            AuthorizationPolicyBuilder().with_priority(0).with_permission(team_leader_permission).build(),
            AuthorizationPolicyBuilder().with_priority(1).with_permission(manager_permission).build(),
        ]
        flow = FlowBuilder("my_field", self.content_type) \
            .with_transition(state1, state2, authorization_policies) \
            .build()

        workflowmodel_object = flow.objects[0]

        assert_that(
            calling(workflowmodel_object.workflow.my_field.approve).with_args(as_user=manager),
            raises(WorkflowException, "There is no available approval for the user")
        )

    def test_shouldNotTransitToNextStateWhenThereAreMultipleApprovalsToBeApproved(self):
        manager_permission = PermissionObjectFactory()
        team_leader_permission = PermissionObjectFactory()

        team_leader = UserObjectFactory(user_permissions=[team_leader_permission])

        state1 = RawState("state1")
        state2 = RawState("state2")

        authorization_policies = [
            AuthorizationPolicyBuilder().with_priority(0).with_permission(team_leader_permission).build(),
            AuthorizationPolicyBuilder().with_priority(1).with_permission(manager_permission).build(),
        ]
        flow = FlowBuilder("my_field", self.content_type) \
            .with_transition(state1, state2, authorization_policies) \
            .build()

        workflowmodel_object = flow.objects[0]

        assert_that(workflowmodel_object.my_field, equal_to(flow.get_state(state1)))
        workflowmodel_object.workflow.my_field.approve(team_leader)
        assert_that(workflowmodel_object.my_field, equal_to(flow.get_state(state1)))

    def test_shouldTransitToNextStateWhenAllTheApprovalsAreApproved(self):
        manager_permission = PermissionObjectFactory()
        team_leader_permission = PermissionObjectFactory()

        manager = UserObjectFactory(user_permissions=[manager_permission])
        team_leader = UserObjectFactory(user_permissions=[team_leader_permission])

        state1 = RawState("state1")
        state2 = RawState("state2")

        authorization_policies = [
            AuthorizationPolicyBuilder().with_priority(0).with_permission(team_leader_permission).build(),
            AuthorizationPolicyBuilder().with_priority(1).with_permission(manager_permission).build(),
        ]
        flow = FlowBuilder("my_field", self.content_type) \
            .with_transition(state1, state2, authorization_policies) \
            .build()

        workflowmodel_object = flow.objects[0]

        assert_that(workflowmodel_object.my_field, equal_to(flow.get_state(state1)))
        workflowmodel_object.workflow.my_field.approve(team_leader)
        assert_that(workflowmodel_object.my_field, equal_to(flow.get_state(state1)))

        assert_that(workflowmodel_object.my_field, equal_to(flow.get_state(state1)))
        workflowmodel_object.workflow.my_field.approve(manager)
        assert_that(workflowmodel_object.my_field, equal_to(flow.get_state(state2)))

    def test_shouldDictatePassingNextStateWhenThereAreMultiple(self):
        authorized_permission = PermissionObjectFactory()

        authorized_user = UserObjectFactory(user_permissions=[authorized_permission])

        state1 = RawState("state1")
        state2 = RawState("state2")
        state3 = RawState("state3")

        authorization_policies = [AuthorizationPolicyBuilder().with_permission(authorized_permission).build(), ]
        flow = FlowBuilder("my_field", self.content_type) \
            .with_transition(state1, state2, authorization_policies) \
            .with_transition(state1, state3, authorization_policies) \
            .build()

        workflowmodel_object = flow.objects[0]
        assert_that(
            calling(workflowmodel_object.workflow.my_field.approve).with_args(as_user=authorized_user),
            raises(WorkflowException, "State must be given when there are multiple states for destination")
        )

    def test_shouldTransitToTheGivenNextStateWhenThereAreMultipleNextStates(self):
        authorized_permission = PermissionObjectFactory()

        authorized_user = UserObjectFactory(user_permissions=[authorized_permission])

        state1 = RawState("state1")
        state2 = RawState("state2")
        state3 = RawState("state3")

        authorization_policies = [AuthorizationPolicyBuilder().with_permission(authorized_permission).build(), ]
        flow = FlowBuilder("my_field", self.content_type) \
            .with_transition(state1, state2, authorization_policies) \
            .with_transition(state1, state3, authorization_policies) \
            .build()

        workflowmodel_object = flow.objects[0]

        assert_that(workflowmodel_object.my_field, equal_to(flow.get_state(state1)))
        workflowmodel_object.workflow.my_field.approve(as_user=authorized_user, next_state=flow.get_state(state3))
        assert_that(workflowmodel_object.my_field, equal_to(flow.get_state(state3)))

    def test_shouldNotAcceptANextStateWhichIsNotAmongPossibleNextStates(self):
        authorized_permission = PermissionObjectFactory()

        authorized_user = UserObjectFactory(user_permissions=[authorized_permission])

        state1 = RawState("state1")
        state2 = RawState("state2")
        state3 = RawState("state3")
        invalid_state = RawState("state4")

        authorization_policies = [AuthorizationPolicyBuilder().with_permission(authorized_permission).build(), ]
        flow = FlowBuilder("my_field", self.content_type) \
            .with_transition(state1, state2, authorization_policies) \
            .with_transition(state1, state3, authorization_policies) \
            .with_additional_state(invalid_state) \
            .build()

        workflowmodel_object = flow.objects[0]

        assert_that(
            calling(workflowmodel_object.workflow.my_field.approve).with_args(as_user=authorized_user, next_state=flow.get_state(invalid_state)),
            raises(WorkflowException,
                   "Invalid state is given\(%s\). Valid states is\(are\) (%s|%s)" % (
                       invalid_state.label,
                       ",".join([state2.label, state3.label]),
                       ",".join([state3.label, state2.label]))
                   )
        )

    def test_shouldAllowCyclicTransitions(self):
        authorized_permission = PermissionObjectFactory()

        authorized_user = UserObjectFactory(user_permissions=[authorized_permission])

        cycle_state_1 = RawState("cycle_state_1")
        cycle_state_2 = RawState("cycle_state_2")
        cycle_state_3 = RawState("cycle_state_3")
        off_the_cycle_state = RawState("off_the_cycle_state")
        final_state = RawState("final_state")

        authorization_policies = [AuthorizationPolicyBuilder().with_permission(authorized_permission).build(), ]
        flow = FlowBuilder("my_field", self.content_type) \
            .with_transition(cycle_state_1, cycle_state_2, authorization_policies) \
            .with_transition(cycle_state_2, cycle_state_3, authorization_policies) \
            .with_transition(cycle_state_3, cycle_state_1, authorization_policies) \
            .with_transition(cycle_state_3, off_the_cycle_state, authorization_policies) \
            .with_transition(off_the_cycle_state, final_state, authorization_policies) \
            .build()

        workflowmodel_object = flow.objects[0]

        assert_that(workflowmodel_object.my_field, equal_to(flow.get_state(cycle_state_1)))
        workflowmodel_object.workflow.my_field.approve(as_user=authorized_user)
        assert_that(workflowmodel_object.my_field, equal_to(flow.get_state(cycle_state_2)))
        workflowmodel_object.workflow.my_field.approve(as_user=authorized_user)
        assert_that(workflowmodel_object.my_field, equal_to(flow.get_state(cycle_state_3)))

        transitions = Transition.objects.filter(workflowmodel=flow.workflowmodel, workflowmodel_object=workflowmodel_object)
        assert_that(transitions, has_length(5))

        approvals = TransitionApproval.objects.filter(workflowmodel=flow.workflowmodel, workflowmodel_object=workflowmodel_object)
        assert_that(approvals, has_length(5))

        assert_that(approvals, has_approval(cycle_state_1, cycle_state_2, APPROVED, iteration=0, permissions=[authorized_permission]))
        assert_that(approvals, has_approval(cycle_state_2, cycle_state_3, APPROVED, iteration=1, permissions=[authorized_permission]))
        assert_that(approvals, has_approval(cycle_state_3, cycle_state_1, PENDING, iteration=2, permissions=[authorized_permission]))
        assert_that(approvals, has_approval(cycle_state_3, off_the_cycle_state, PENDING, iteration=2, permissions=[authorized_permission]))
        assert_that(approvals, has_approval(off_the_cycle_state, final_state, PENDING, iteration=3, permissions=[authorized_permission]))

        workflowmodel_object.workflow.my_field.approve(as_user=authorized_user, next_state=flow.get_state(cycle_state_1))
        assert_that(workflowmodel_object.my_field, equal_to(flow.get_state(cycle_state_1)))

        transitions = Transition.objects.filter(workflowmodel=flow.workflowmodel, workflowmodel_object=workflowmodel_object)
        assert_that(transitions, has_length(10))

        approvals = TransitionApproval.objects.filter(workflowmodel=flow.workflowmodel, workflowmodel_object=workflowmodel_object)
        assert_that(approvals, has_length(10))

        assert_that(approvals, has_approval(cycle_state_1, cycle_state_2, APPROVED, iteration=0, permissions=[authorized_permission]))
        assert_that(approvals, has_approval(cycle_state_2, cycle_state_3, APPROVED, iteration=1, permissions=[authorized_permission]))
        assert_that(approvals, has_approval(cycle_state_3, cycle_state_1, APPROVED, iteration=2, permissions=[authorized_permission]))
        assert_that(approvals, has_approval(cycle_state_3, off_the_cycle_state, CANCELLED, iteration=2, permissions=[authorized_permission]))
        assert_that(approvals, has_approval(off_the_cycle_state, final_state, CANCELLED, iteration=3, permissions=[authorized_permission]))

        assert_that(approvals, has_approval(cycle_state_1, cycle_state_2, PENDING, iteration=3, permissions=[authorized_permission]))
        assert_that(approvals, has_approval(cycle_state_2, cycle_state_3, PENDING, iteration=4, permissions=[authorized_permission]))
        assert_that(approvals, has_approval(cycle_state_3, cycle_state_1, PENDING, iteration=5, permissions=[authorized_permission]))
        assert_that(approvals, has_approval(cycle_state_3, off_the_cycle_state, PENDING, iteration=5, permissions=[authorized_permission]))
        assert_that(approvals, has_approval(off_the_cycle_state, final_state, PENDING, iteration=6, permissions=[authorized_permission]))

    def test_shouldHandleSecondCycleProperly(self):
        authorized_permission = PermissionObjectFactory()

        authorized_user = UserObjectFactory(user_permissions=[authorized_permission])

        cycle_state_1 = RawState("cycle_state_1")
        cycle_state_2 = RawState("cycle_state_2")
        cycle_state_3 = RawState("cycle_state_3")
        off_the_cycle_state = RawState("off_the_cycle_state")
        final_state = RawState("final_state")

        authorization_policies = [AuthorizationPolicyBuilder().with_permission(authorized_permission).build(), ]
        flow = FlowBuilder("my_field", self.content_type) \
            .with_transition(cycle_state_1, cycle_state_2, authorization_policies) \
            .with_transition(cycle_state_2, cycle_state_3, authorization_policies) \
            .with_transition(cycle_state_3, cycle_state_1, authorization_policies) \
            .with_transition(cycle_state_3, off_the_cycle_state, authorization_policies) \
            .with_transition(off_the_cycle_state, final_state, authorization_policies) \
            .build()

        workflowmodel_object = flow.objects[0]

        assert_that(workflowmodel_object.my_field, equal_to(flow.get_state(cycle_state_1)))
        workflowmodel_object.workflow.my_field.approve(as_user=authorized_user)
        assert_that(workflowmodel_object.my_field, equal_to(flow.get_state(cycle_state_2)))
        workflowmodel_object.workflow.my_field.approve(as_user=authorized_user)
        assert_that(workflowmodel_object.my_field, equal_to(flow.get_state(cycle_state_3)))

        transitions = Transition.objects.filter(workflowmodel=flow.workflowmodel, workflowmodel_object=workflowmodel_object)
        assert_that(transitions, has_length(5))

        approvals = TransitionApproval.objects.filter(workflowmodel=flow.workflowmodel, workflowmodel_object=workflowmodel_object)
        assert_that(approvals, has_length(5))

        assert_that(approvals, has_approval(cycle_state_1, cycle_state_2, APPROVED, iteration=0, permissions=[authorized_permission]))
        assert_that(approvals, has_approval(cycle_state_2, cycle_state_3, APPROVED, iteration=1, permissions=[authorized_permission]))
        assert_that(approvals, has_approval(cycle_state_3, cycle_state_1, PENDING, iteration=2, permissions=[authorized_permission]))
        assert_that(approvals, has_approval(cycle_state_3, off_the_cycle_state, PENDING, iteration=2, permissions=[authorized_permission]))
        assert_that(approvals, has_approval(off_the_cycle_state, final_state, PENDING, iteration=3, permissions=[authorized_permission]))

        workflowmodel_object.workflow.my_field.approve(as_user=authorized_user, next_state=flow.get_state(cycle_state_1))
        assert_that(workflowmodel_object.my_field, equal_to(flow.get_state(cycle_state_1)))
        workflowmodel_object.workflow.my_field.approve(as_user=authorized_user)
        assert_that(workflowmodel_object.my_field, equal_to(flow.get_state(cycle_state_2)))
        workflowmodel_object.workflow.my_field.approve(as_user=authorized_user)
        assert_that(workflowmodel_object.my_field, equal_to(flow.get_state(cycle_state_3)))
        workflowmodel_object.workflow.my_field.approve(as_user=authorized_user, next_state=flow.get_state(cycle_state_1))
        assert_that(workflowmodel_object.my_field, equal_to(flow.get_state(cycle_state_1)))

        approvals = TransitionApproval.objects.filter(workflowmodel=flow.workflowmodel, workflowmodel_object=workflowmodel_object)
        assert_that(approvals, has_length(15))

        assert_that(approvals, has_approval(cycle_state_1, cycle_state_2, APPROVED, iteration=0, permissions=[authorized_permission]))
        assert_that(approvals, has_approval(cycle_state_2, cycle_state_3, APPROVED, iteration=1, permissions=[authorized_permission]))
        assert_that(approvals, has_approval(cycle_state_3, cycle_state_1, APPROVED, iteration=2, permissions=[authorized_permission]))
        assert_that(approvals, has_approval(cycle_state_3, off_the_cycle_state, CANCELLED, iteration=2, permissions=[authorized_permission]))
        assert_that(approvals, has_approval(off_the_cycle_state, final_state, CANCELLED, iteration=3, permissions=[authorized_permission]))

        assert_that(approvals, has_approval(cycle_state_1, cycle_state_2, APPROVED, iteration=3, permissions=[authorized_permission]))
        assert_that(approvals, has_approval(cycle_state_2, cycle_state_3, APPROVED, iteration=4, permissions=[authorized_permission]))
        assert_that(approvals, has_approval(cycle_state_3, cycle_state_1, APPROVED, iteration=5, permissions=[authorized_permission]))
        assert_that(approvals, has_approval(cycle_state_3, off_the_cycle_state, CANCELLED, iteration=5, permissions=[authorized_permission]))
        assert_that(approvals, has_approval(off_the_cycle_state, final_state, CANCELLED, iteration=6, permissions=[authorized_permission]))

        assert_that(approvals, has_approval(cycle_state_1, cycle_state_2, PENDING, iteration=6, permissions=[authorized_permission]))
        assert_that(approvals, has_approval(cycle_state_2, cycle_state_3, PENDING, iteration=7, permissions=[authorized_permission]))
        assert_that(approvals, has_approval(cycle_state_3, cycle_state_1, PENDING, iteration=8, permissions=[authorized_permission]))
        assert_that(approvals, has_approval(cycle_state_3, off_the_cycle_state, PENDING, iteration=8, permissions=[authorized_permission]))
        assert_that(approvals, has_approval(off_the_cycle_state, final_state, PENDING, iteration=9, permissions=[authorized_permission]))

    def test__shouldHandleUndefinedSecondWorkflowModelCase(self):
        state1 = RawState("state1")
        state2 = RawState("state2")

        authorization_policies = []
        flow = FlowBuilder("status1", ContentType.objects.get_for_model(ModelWithTwoStateFields)) \
            .with_object_factory(lambda: ModelWithTwoStateFieldsObjectFactory().model) \
            .with_transition(state1, state2, authorization_policies) \
            .build()

        workflowmodel_object = flow.objects[0]

        assert_that(workflowmodel_object.status1, equal_to(flow.get_state(state1)))
        assert_that(workflowmodel_object.status2, none())

    def test__shouldReturnNextApprovals(self):
        state1 = RawState("state1")
        state2 = RawState("state2")
        state3 = RawState("state3")

        authorization_policies = [AuthorizationPolicyBuilder().build()]
        flow = FlowBuilder("my_field", self.content_type) \
            .with_transition(state1, state2, authorization_policies) \
            .with_transition(state1, state3, authorization_policies) \
            .build()

        workflowmodel_object = flow.objects[0]

        assert_that(workflowmodel_object.my_field, equal_to(flow.get_state(state1)))
        next_approvals = workflowmodel_object.workflow.my_field.next_approvals
        assert_that(next_approvals, has_length(2))
        assert_that(next_approvals, has_item(flow.transitions_approval_metas[0].transition_approvals.first()))
        assert_that(next_approvals, has_item(flow.transitions_approval_metas[1].transition_approvals.first()))

    def test_shouldCancelAllOtherStateTransition(self):
        authorized_permission = PermissionObjectFactory()

        authorized_user = UserObjectFactory(user_permissions=[authorized_permission])

        state1 = RawState("state1")
        state2 = RawState("state2")
        state3 = RawState("state3")
        state4 = RawState("state4")

        authorization_policies = [AuthorizationPolicyBuilder().with_permission(authorized_permission).build(), ]
        flow = FlowBuilder("my_field", self.content_type) \
            .with_transition(state1, state2, authorization_policies) \
            .with_transition(state1, state3, authorization_policies) \
            .with_transition(state1, state4, authorization_policies) \
            .build()

        workflowmodel_object = flow.objects[0]

        assert_that(workflowmodel_object.my_field, equal_to(flow.get_state(state1)))
        workflowmodel_object.workflow.my_field.approve(as_user=authorized_user, next_state=flow.get_state(state3))
        assert_that(workflowmodel_object.my_field, equal_to(flow.get_state(state3)))

        assert_that(
            flow.transitions_approval_metas[0].transition_approvals.all(),
            all_of(
                has_length(1),
                has_item(has_property("status", CANCELLED))
            )
        ),

        assert_that(
            flow.transitions_approval_metas[1].transition_approvals.all(),
            all_of(
                has_length(1),
                has_item(has_property("status", APPROVED))
            )
        ),

        assert_that(
            flow.transitions_approval_metas[2].transition_approvals.all(),
            all_of(
                has_length(1),
                has_item(has_property("status", CANCELLED))
            )
        )

    def test_shouldCancelAllOtherStateTransitionDescendants(self):
        authorized_permission = PermissionObjectFactory()

        authorized_user = UserObjectFactory(user_permissions=[authorized_permission])

        state1 = RawState("state1")
        state2 = RawState("state2")
        state3 = RawState("state3")
        state4 = RawState("state4")
        state5 = RawState("state5")

        authorization_policies = [AuthorizationPolicyBuilder().with_permission(authorized_permission).build(), ]
        flow = FlowBuilder("my_field", self.content_type) \
            .with_transition(state1, state2, authorization_policies) \
            .with_transition(state1, state3, authorization_policies) \
            .with_transition(state1, state4, authorization_policies) \
            .with_transition(state4, state5, authorization_policies) \
            .build()

        workflowmodel_object = flow.objects[0]

        assert_that(workflowmodel_object.my_field, equal_to(flow.get_state(state1)))
        workflowmodel_object.workflow.my_field.approve(as_user=authorized_user, next_state=flow.get_state(state3))
        assert_that(workflowmodel_object.my_field, equal_to(flow.get_state(state3)))

        assert_that(
            flow.transitions_approval_metas[0].transition_approvals.all(),
            all_of(
                has_length(1),
                has_item(has_property("status", CANCELLED))
            )
        )

        assert_that(
            flow.transitions_approval_metas[1].transition_approvals.all(),
            all_of(
                has_length(1),
                has_item(has_property("status", APPROVED))
            )
        )

        assert_that(
            flow.transitions_approval_metas[2].transition_approvals.all(),
            all_of(
                has_length(1),
                has_item(has_property("status", CANCELLED))
            )
        )

        assert_that(
            flow.transitions_approval_metas[3].transition_approvals.all(),
            all_of(
                has_length(1),
                has_item(has_property("status", CANCELLED))
            )
        )

    def test_shouldNotCancelDescendantsIfItIsPartOfPossibleFuture(self):
        authorized_permission = PermissionObjectFactory()

        authorized_user = UserObjectFactory(user_permissions=[authorized_permission])

        first_state = RawState("first")
        diamond_left_state_1 = RawState("diamond-left-1")
        diamond_left_state_2 = RawState("diamond-left-2")
        diamond_right_state_1 = RawState("diamond-right-1")
        diamond_right_state_2 = RawState("diamond-right-2")
        diamond_join_state = RawState("diamond-join")
        final_state = RawState("final")

        authorization_policies = [AuthorizationPolicyBuilder().with_permission(authorized_permission).build(), ]
        flow = FlowBuilder("my_field", self.content_type) \
            .with_transition(first_state, diamond_left_state_1, authorization_policies) \
            .with_transition(first_state, diamond_right_state_1, authorization_policies) \
            .with_transition(diamond_left_state_1, diamond_left_state_2, authorization_policies) \
            .with_transition(diamond_right_state_1, diamond_right_state_2, authorization_policies) \
            .with_transition(diamond_left_state_2, diamond_join_state, authorization_policies) \
            .with_transition(diamond_right_state_2, diamond_join_state, authorization_policies) \
            .with_transition(diamond_join_state, final_state, authorization_policies) \
            .build()

        workflowmodel_object = flow.objects[0]

        assert_that(workflowmodel_object.my_field, equal_to(flow.get_state(first_state)))
        workflowmodel_object.workflow.my_field.approve(as_user=authorized_user, next_state=flow.get_state(diamond_left_state_1))
        assert_that(workflowmodel_object.my_field, equal_to(flow.get_state(diamond_left_state_1)))

        approvals = TransitionApproval.objects.filter(workflowmodel=flow.workflowmodel, workflowmodel_object=workflowmodel_object)

        assert_that(approvals, has_approval(first_state, diamond_left_state_1, APPROVED))
        assert_that(approvals, has_approval(diamond_left_state_1, diamond_left_state_2, PENDING))
        assert_that(approvals, has_approval(diamond_left_state_2, diamond_join_state, PENDING))
        assert_that(approvals, has_approval(first_state, diamond_right_state_1, CANCELLED))
        assert_that(approvals, has_approval(diamond_right_state_1, diamond_right_state_2, CANCELLED))
        assert_that(approvals, has_approval(diamond_right_state_2, diamond_join_state, CANCELLED))
        assert_that(approvals, has_approval(diamond_join_state, final_state, PENDING))

    def test_shouldAssessIterationsCorrectly(self):
        authorized_permission1 = PermissionObjectFactory()
        authorized_permission2 = PermissionObjectFactory()

        state1 = RawState("state1")
        state2 = RawState("state2")
        state3 = RawState("state3")

        flow = FlowBuilder("my_field", self.content_type) \
            .with_transition(state1, state2, [AuthorizationPolicyBuilder().with_permission(authorized_permission1).build()]) \
            .with_transition(state2, state3,
                             [
                                 AuthorizationPolicyBuilder().with_permission(authorized_permission1).build(),
                                 AuthorizationPolicyBuilder().with_priority(1).with_permission(authorized_permission2).build(),
                             ]) \
            .build()

        workflowmodel_object = flow.objects[0]

        approvals = TransitionApproval.objects.filter(workflowmodel=flow.workflowmodel, workflowmodel_object=workflowmodel_object)
        assert_that(approvals, has_length(3))

        assert_that(approvals, has_approval(state1, state2, PENDING, iteration=0))
        assert_that(approvals, has_approval(state2, state3, PENDING, iteration=1, permissions=[authorized_permission1]))
        assert_that(approvals, has_approval(state2, state3, PENDING, iteration=1, permissions=[authorized_permission2]))

    def test_shouldAssessIterationsCorrectlyWhenCycled(self):
        authorized_permission = PermissionObjectFactory()
        authorized_user = UserObjectFactory(user_permissions=[authorized_permission])

        cycle_state_1 = RawState("cycle_state_1")
        cycle_state_2 = RawState("cycle_state_2")
        cycle_state_3 = RawState("cycle_state_3")
        off_the_cycle_state = RawState("off_the_cycle_state")
        final_state = RawState("final_state")

        authorization_policies = [AuthorizationPolicyBuilder().with_permission(authorized_permission).build(), ]
        flow = FlowBuilder("my_field", self.content_type) \
            .with_transition(cycle_state_1, cycle_state_2, authorization_policies) \
            .with_transition(cycle_state_2, cycle_state_3, authorization_policies) \
            .with_transition(cycle_state_3, cycle_state_1, authorization_policies) \
            .with_transition(cycle_state_3, off_the_cycle_state, authorization_policies) \
            .with_transition(off_the_cycle_state, final_state, authorization_policies) \
            .build()

        workflowmodel_object = flow.objects[0]

        assert_that(workflowmodel_object.my_field, equal_to(flow.get_state(cycle_state_1)))
        workflowmodel_object.workflow.my_field.approve(as_user=authorized_user)
        assert_that(workflowmodel_object.my_field, equal_to(flow.get_state(cycle_state_2)))
        workflowmodel_object.workflow.my_field.approve(as_user=authorized_user)
        assert_that(workflowmodel_object.my_field, equal_to(flow.get_state(cycle_state_3)))

        approvals = TransitionApproval.objects.filter(workflowmodel=flow.workflowmodel, workflowmodel_object=workflowmodel_object)
        assert_that(approvals, has_length(5))

        workflowmodel_object.workflow.my_field.approve(as_user=authorized_user, next_state=flow.get_state(cycle_state_1))
        assert_that(workflowmodel_object.my_field, equal_to(flow.get_state(cycle_state_1)))

        approvals = TransitionApproval.objects.filter(workflowmodel=flow.workflowmodel, workflowmodel_object=workflowmodel_object)
        assert_that(approvals, has_length(10))

        assert_that(approvals, has_approval(cycle_state_1, cycle_state_2, APPROVED, iteration=0))
        assert_that(approvals, has_approval(cycle_state_2, cycle_state_3, APPROVED, iteration=1))
        assert_that(approvals, has_approval(cycle_state_3, cycle_state_1, APPROVED, iteration=2))
        assert_that(approvals, has_approval(cycle_state_3, off_the_cycle_state, CANCELLED, iteration=2))
        assert_that(approvals, has_approval(off_the_cycle_state, final_state, CANCELLED, iteration=3))

        assert_that(approvals, has_approval(cycle_state_1, cycle_state_2, PENDING, iteration=3))
        assert_that(approvals, has_approval(cycle_state_2, cycle_state_3, PENDING, iteration=4))
        assert_that(approvals, has_approval(cycle_state_3, cycle_state_1, PENDING, iteration=5))
        assert_that(approvals, has_approval(cycle_state_3, off_the_cycle_state, PENDING, iteration=5))
        assert_that(approvals, has_approval(off_the_cycle_state, final_state, PENDING, iteration=6))

    def test_shouldJumpToASpecificState(self):
        authorized_permission = PermissionObjectFactory()

        state1 = RawState("state1")
        state2 = RawState("state2")
        state3 = RawState("state3")

        authorization_policies = [AuthorizationPolicyBuilder().with_permission(authorized_permission).build(), ]
        flow = FlowBuilder("my_field", self.content_type) \
            .with_transition(state1, state2, authorization_policies) \
            .with_transition(state2, state3, authorization_policies) \
            .build()

        workflowmodel_object = flow.objects[0]

        assert_that(workflowmodel_object.my_field, equal_to(flow.get_state(state1)))

        approvals = TransitionApproval.objects.filter(workflowmodel_object=workflowmodel_object)
        assert_that(approvals, has_approval(state1, state2, PENDING))
        assert_that(approvals, has_approval(state2, state3, PENDING))

        workflowmodel_object.workflow.my_field.jump_to(flow.get_state(state3))

        assert_that(workflowmodel_object.my_field, equal_to(flow.get_state(state3)))

        approvals = TransitionApproval.objects.filter(workflowmodel_object=workflowmodel_object)
        assert_that(approvals, has_approval(state1, state2, JUMPED))
        assert_that(approvals, has_approval(state2, state3, JUMPED))

    def test_shouldNotJumpBackToAPreviousState(self):
        authorized_permission = PermissionObjectFactory()
        authorized_user = UserObjectFactory(user_permissions=[authorized_permission])

        state1 = RawState("state1")
        state2 = RawState("state2")

        authorization_policies = [AuthorizationPolicyBuilder().with_permission(authorized_permission).build(), ]
        flow = FlowBuilder("my_field", self.content_type) \
            .with_transition(state1, state2, authorization_policies) \
            .build()

        workflowmodel_object = flow.objects[0]

        workflowmodel_object.workflow.my_field.approve(as_user=authorized_user, next_state=flow.get_state(state2))
        assert_that(
            calling(workflowmodel_object.workflow.my_field.jump_to).with_args(flow.get_state(state1)),
            raises(WorkflowException, "This state is not available to be jumped in the future of this object")
        )

    def test_shouldJumpToASpecificStateWhenThereAreMultipleNextState(self):
        authorized_permission = PermissionObjectFactory()

        state1 = RawState("state1")
        state2 = RawState("state2")
        state3 = RawState("state3")

        authorization_policies = [AuthorizationPolicyBuilder().with_permission(authorized_permission).build(), ]
        flow = FlowBuilder("my_field", self.content_type) \
            .with_transition(state1, state2, authorization_policies) \
            .with_transition(state1, state3, authorization_policies) \
            .build()

        workflowmodel_object = flow.objects[0]

        assert_that(workflowmodel_object.my_field, equal_to(flow.get_state(state1)))

        approvals = TransitionApproval.objects.filter(workflowmodel_object=workflowmodel_object)
        assert_that(approvals, has_approval(state1, state2, PENDING))
        assert_that(approvals, has_approval(state1, state3, PENDING))

        workflowmodel_object.workflow.my_field.jump_to(flow.get_state(state3))

        approvals = TransitionApproval.objects.filter(workflowmodel_object=workflowmodel_object)
        assert_that(approvals, has_approval(state1, state2, JUMPED))
        assert_that(approvals, has_approval(state1, state3, JUMPED))

    def test_shouldNotCrashWhenAModelObjectWithStringPrimaryKeyIsApproved(self):
        content_type = ContentType.objects.get_for_model(ModelWithStringPrimaryKey)
        authorized_permission = PermissionObjectFactory(content_type=content_type)
        authorized_user = UserObjectFactory(user_permissions=[authorized_permission])

        state1 = RawState("state1")
        state2 = RawState("state2")
        authorization_policies = [AuthorizationPolicyBuilder().with_permission(authorized_permission).build(), ]
        flow = FlowBuilder("status", content_type) \
            .with_transition(state1, state2, authorization_policies) \
            .with_object_factory(lambda: ModelWithStringPrimaryKey.objects.create()) \
            .build()

        workflowmodel_object = flow.objects[0]

        assert_that(workflowmodel_object.status, equal_to(flow.get_state(state1)))
        workflowmodel_object.workflow.status.approve(as_user=authorized_user)
        assert_that(workflowmodel_object.status, equal_to(flow.get_state(state2)))

    def test_shouldAllowMultipleCyclicTransitions(self):
        authorized_permission = PermissionObjectFactory()

        authorized_user = UserObjectFactory(user_permissions=[authorized_permission])

        initial_state = RawState("initial_state")
        cycle_state_1 = RawState("cycle_state_1")
        cycle_state_2 = RawState("cycle_state_2")
        off_the_cycle_state = RawState("off_the_cycle_state")
        cycle_state_3 = RawState("cycle_state_3")
        cycle_state_4 = RawState("cycle_state_4")
        final_state = RawState("final_state")

        authorization_policies = [AuthorizationPolicyBuilder().with_permission(authorized_permission).build(), ]
        flow = FlowBuilder("my_field", self.content_type) \
            .with_transition(initial_state, cycle_state_1, authorization_policies) \
            .with_transition(cycle_state_1, cycle_state_2, authorization_policies) \
            .with_transition(cycle_state_2, cycle_state_1, authorization_policies) \
            .with_transition(cycle_state_1, off_the_cycle_state, authorization_policies) \
            .with_transition(off_the_cycle_state, cycle_state_3, authorization_policies) \
            .with_transition(cycle_state_3, cycle_state_4, authorization_policies) \
            .with_transition(cycle_state_4, cycle_state_3, authorization_policies) \
            .with_transition(cycle_state_3, final_state, authorization_policies) \
            .build()

        workflowmodel_object = flow.objects[0]

        assert_that(workflowmodel_object.my_field, equal_to(flow.get_state(initial_state)))

        workflowmodel_object.workflow.my_field.approve(as_user=authorized_user)
        assert_that(workflowmodel_object.my_field, equal_to(flow.get_state(cycle_state_1)))

        workflowmodel_object.workflow.my_field.approve(as_user=authorized_user, next_state=flow.get_state(cycle_state_2))
        assert_that(workflowmodel_object.my_field, equal_to(flow.get_state(cycle_state_2)))

        workflowmodel_object.workflow.my_field.approve(as_user=authorized_user)
        assert_that(workflowmodel_object.my_field, equal_to(flow.get_state(cycle_state_1)))

    def test_shouldNotCancelDescendantsThatCanBeTransitedInTheFuture(self):
        authorized_permission = PermissionObjectFactory()

        authorized_user = UserObjectFactory(user_permissions=[authorized_permission])

        state1 = RawState("state_1")
        state2 = RawState("state_2")
        state3 = RawState("state_3")
        final_state = RawState("final_state")

        authorization_policies = [AuthorizationPolicyBuilder().with_permission(authorized_permission).build(), ]
        flow = FlowBuilder("my_field", self.content_type) \
            .with_transition(state1, state2, authorization_policies) \
            .with_transition(state1, state3, authorization_policies) \
            .with_transition(state2, state3, authorization_policies) \
            .with_transition(state3, final_state, authorization_policies) \
            .build()

        workflowmodel_object = flow.objects[0]

        assert_that(workflowmodel_object.my_field, equal_to(flow.get_state(state1)))
        workflowmodel_object.workflow.my_field.approve(as_user=authorized_user, next_state=flow.get_state(state2))
        assert_that(workflowmodel_object.my_field, equal_to(flow.get_state(state2)))

        approvals = TransitionApproval.objects.filter(workflowmodel=flow.workflowmodel, workflowmodel_object=workflowmodel_object)

        assert_that(approvals, has_approval(state3, final_state, PENDING))
