from uuid import uuid4

from django.test import TestCase

from newname.models import Function, OnTransitHook, OnApprovedHook, OnCompleteHook
from newname.models.hook import BEFORE, AFTER

callback_output = {

}

callback_method = """
from newname.tests.hooking.base_hooking_test import callback_output
def handle(context):
    print(context)
    key = '%s'
    callback_output[key] = callback_output.get(key,[]) + [context]
"""


class BaseHookingTest(TestCase):

    def setUp(self):
        self.identifier = str(uuid4())
        self.callback_function = Function.objects.create(name=uuid4(), body=callback_method % self.identifier)

    def get_output(self):
        return callback_output.get(self.identifier, None)

    def hook_pre_transition(self, workflowmodel, transition_meta, workflowmodel_object=None, transition=None):
        OnTransitHook.objects.create(
            workflowmodel=workflowmodel,
            callback_function=self.callback_function,
            transition_meta=transition_meta,
            transition=transition,
            hook_type=BEFORE,
            workflowmodel_object=workflowmodel_object,
        )

    def hook_post_transition(self, workflowmodel, transition_meta, workflowmodel_object=None, transition=None):
        OnTransitHook.objects.create(
            workflowmodel=workflowmodel,
            callback_function=self.callback_function,
            transition_meta=transition_meta,
            transition=transition,
            hook_type=AFTER,
            workflowmodel_object=workflowmodel_object,
        )

    def hook_pre_approve(self, workflowmodel, transition_approval_meta, workflowmodel_object=None, transition_approval=None):
        OnApprovedHook.objects.create(
            workflowmodel=workflowmodel,
            callback_function=self.callback_function,
            transition_approval_meta=transition_approval_meta,
            hook_type=BEFORE,
            workflowmodel_object=workflowmodel_object,
            transition_approval=transition_approval
        )

    def hook_post_approve(self, workflowmodel, transition_approval_meta, workflowmodel_object=None, transition_approval=None):
        OnApprovedHook.objects.create(
            workflowmodel=workflowmodel,
            callback_function=self.callback_function,
            transition_approval_meta=transition_approval_meta,
            hook_type=AFTER,
            workflowmodel_object=workflowmodel_object,
            transition_approval=transition_approval
        )

    def hook_pre_complete(self, workflowmodel, workflowmodel_object=None):
        OnCompleteHook.objects.create(
            workflowmodel=workflowmodel,
            callback_function=self.callback_function,
            hook_type=BEFORE,
            workflowmodel_object=workflowmodel_object
        )

    def hook_post_complete(self, workflowmodel, workflowmodel_object=None):
        OnCompleteHook.objects.create(
            workflowmodel=workflowmodel,
            callback_function=self.callback_function,
            hook_type=AFTER,
            workflowmodel_object=workflowmodel_object
        )
