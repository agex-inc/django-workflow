from behave import given, when

from features.steps.basic_steps import workflowmodel_object


@given('a bug "{description:ws}" identifier "{identifier:ws}"')
def issue(context, description, identifier):
    workflowmodel_object(context, identifier)


def _approve(context, workflowmodel_object_identifier, username, next_state):
    from django.contrib.auth.models import User
    from newname.models import State

    workflowmodel_object = getattr(context, "workflowmodel_objects", {})[workflowmodel_object_identifier]

    user = User.objects.get(username=username)
    workflowmodel_object.newname.my_field.approve(as_user=user, next_state=State.objects.get(label=next_state))


@when('"{workflowmodel_object_identifier:ws}" is attempted to be closed by {username:w}')
def close_issue(context, workflowmodel_object_identifier, username):
    _approve(context, workflowmodel_object_identifier, username, "Closed")


@when('"{workflowmodel_object_identifier:ws}" is attempted to be re-opened by {username:w}')
def re_open_issue(context, workflowmodel_object_identifier, username):
    _approve(context, workflowmodel_object_identifier, username, "Re-Opened")
