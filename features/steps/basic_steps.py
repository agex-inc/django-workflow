from datetime import datetime

from behave import given, when, then
from hamcrest import assert_that, has_length, is_

from newname.models import State


@given('a permission with name {name:w}')
def permission(context, name):
    from newname.models.factories import PermissionObjectFactory

    PermissionObjectFactory(name=name)


@given('a group with name "{name:ws}"')
def group(context, name):
    from newname.models.factories import GroupObjectFactory

    GroupObjectFactory(name=name)


@given('a user with name {name:w} with permission "{permission_name:ws}"')
def user_with_permission(context, name, permission_name):
    from django.contrib.auth.models import Permission
    from newname.models.factories import UserObjectFactory

    permission = Permission.objects.get(name=permission_name)
    UserObjectFactory(username=name, user_permissions=[permission])


@given('a user with name {name:w} with group "{group_name:ws}"')
def user_with_group(context, name, group_name):
    from django.contrib.auth.models import Group
    from newname.models.factories import UserObjectFactory

    group = Group.objects.get(name=group_name)
    UserObjectFactory(username=name, groups=[group])


@given('a state with label "{state_label:ws}"')
def state_with_label(context, state_label):
    from newname.models.factories import StateObjectFactory

    StateObjectFactory(label=state_label)


@given('a workflowmodel with an identifier "{identifier:ws}"')
def workflowmodel(context, identifier):
    context.workflowmodel_identifier = identifier


@given('a transition "{source_state_label:ws}" -> "{destination_state_label:ws}" in "{workflowmodel_identifier:ws}"')
def transition(context, source_state_label, destination_state_label, workflowmodel_identifier):
    from newname.models import State
    from django.contrib.contenttypes.models import ContentType
    from newname.models.factories import TransitionMetaFactory
    from newname.tests.models import BasicTestModel
    from newname.models.factories import WorkflowModelFactory

    source_state, _ = State.objects.get_or_create(label=source_state_label)
    workflowmodel = getattr(context, "workflowmodels", {}).get(workflowmodel_identifier, None)
    if not workflowmodel:
        content_type = ContentType.objects.get_for_model(BasicTestModel)
        workflowmodel = WorkflowModelFactory(initial_state=source_state, content_type=content_type, field_name="my_field")
        if "workflowmodels" not in context:
            context.workflowmodels = {}
        context.workflowmodels[workflowmodel_identifier] = workflowmodel

    destination_state, _ = State.objects.get_or_create(label=destination_state_label)
    transition = TransitionMetaFactory.create(
        workflowmodel=workflowmodel,
        source_state=source_state,
        destination_state=destination_state,
    )
    identifier = source_state_label + destination_state_label
    transitions = getattr(context, "transitions", {})
    transitions[identifier] = transition
    context.transitions = transitions


@given('an authorization rule for the transition "{source_state_label:ws}" -> "{destination_state_label:ws}" with permission "{permission_name:ws}" and priority {priority:d}')
def authorization_rule_with_permission(context, source_state_label, destination_state_label, permission_name, priority):
    from django.contrib.auth.models import Permission
    from newname.models.factories import TransitionApprovalMetaFactory

    permission = Permission.objects.get(name=permission_name)
    transition_identifier = source_state_label + destination_state_label
    transition_meta = getattr(context, "transitions", {})[transition_identifier]
    TransitionApprovalMetaFactory.create(
        workflowmodel=transition_meta.workflowmodel,
        transition_meta=transition_meta,
        priority=priority,
        permissions=[permission]
    )


@given('an authorization rule for the transition "{source_state_label:ws}" -> "{destination_state_label:ws}" with group "{group_name:ws}" and priority {priority:d}')
def authorization_rule_with_group(context, source_state_label, destination_state_label, group_name, priority):
    authorization_rule_with_groups(context, source_state_label, destination_state_label, [group_name], priority)


@given('an authorization rule for the transition "{source_state_label:ws}" -> "{destination_state_label:ws}" with groups "{group_names:list}" and priority {priority:d}')
def authorization_rule_with_groups(context, source_state_label, destination_state_label, group_names, priority):
    from django.contrib.auth.models import Group
    from newname.models.factories import TransitionApprovalMetaFactory

    transition_identifier = source_state_label + destination_state_label
    transition_meta = getattr(context, "transitions", {})[transition_identifier]
    transition_approval_meta = TransitionApprovalMetaFactory.create(
        workflowmodel=transition_meta.workflowmodel,
        transition_meta=transition_meta,
        priority=priority,
    )
    transition_approval_meta.groups.set(Group.objects.filter(name__in=group_names))


@given('a workflowmodel object with identifier "{identifier:ws}"')
def workflowmodel_object(context, identifier):
    from newname.tests.models.factories import BasicTestModelObjectFactory

    workflowmodel_object = BasicTestModelObjectFactory().model
    workflowmodel_objects = getattr(context, "workflowmodel_objects", {})
    workflowmodel_objects[identifier] = workflowmodel_object
    context.workflowmodel_objects = workflowmodel_objects


@given('"{workflowmodel_object_identifier:ws}" is jumped on state "{state_label:ws}"')
def jump_workflowmodel_object(context, workflowmodel_object_identifier, state_label):
    from newname.models import State

    state = State.objects.get(label=state_label)
    workflowmodel_object = getattr(context, "workflowmodel_objects", {})[workflowmodel_object_identifier]
    workflowmodel_object.newname.my_field.jump_to(state)


@given('{number:d} workflowmodel objects')
def many_workflowmodel_object(context, number):
    from newname.tests.models.factories import BasicTestModelObjectFactory

    BasicTestModelObjectFactory.create_batch(250)


@when('available approvals are fetched with user {username:w}')
def fetched_approvals(context, username):
    from django.contrib.auth.models import User
    from newname.tests.models import BasicTestModel

    user = User.objects.get(username=username)

    context.before = datetime.now()
    context.result = BasicTestModel.newname.my_field.get_on_approval_objects(as_user=user)
    context.after = datetime.now()


@when('get current state of "{workflowmodel_object_identifier:ws}"')
def get_current_state(context, workflowmodel_object_identifier):
    workflowmodel_object = getattr(context, "workflowmodel_objects", {})[workflowmodel_object_identifier]
    from newname.tests.models import BasicTestModel
    workflowmodel_object = BasicTestModel.objects.get(pk=workflowmodel_object.pk)
    context.current_state = workflowmodel_object.my_field


@when('"{workflowmodel_object_identifier:ws}" is attempted to be approved by {username:w}')
def approve_by(context, workflowmodel_object_identifier, username):
    from django.contrib.auth.models import User
    workflowmodel_object = getattr(context, "workflowmodel_objects", {})[workflowmodel_object_identifier]

    user = User.objects.get(username=username)
    workflowmodel_object.newname.my_field.approve(as_user=user)


@when('"{workflowmodel_object_identifier:ws}" is attempted to be approved for next state "{next_state:ws}" by {username:w}')
def approve_for_next_state_by(context, workflowmodel_object_identifier, next_state, username):
    from django.contrib.auth.models import User
    workflowmodel_object = getattr(context, "workflowmodel_objects", {})[workflowmodel_object_identifier]

    user = User.objects.get(username=username)
    workflowmodel_object.newname.my_field.approve(as_user=user, next_state=State.objects.get(label=next_state))


@then('return {number:d} items')
def check_output_count(context, number):
    assert_that(context.result, has_length(number))


@then('return current state as "{state_name:ws}"')
def check_current_state(context, state_name):
    assert_that(context.current_state.label, is_(state_name))
