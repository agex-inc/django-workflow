import inspect

from newname.core.classworkflowmodelobject import ClassWorkflowModelObject
from newname.core.instanceworkflowmodelobject import InstanceWorkflowModelObject
from newname.core.workflowmodelregistry import workflowmodel_registry


# noinspection PyMethodMayBeStatic
class NewNameObject(object):

    def __init__(self, owner):
        self.owner = owner
        self.is_class = inspect.isclass(owner)

    def __getattr__(self, field_name):
        cls = self.owner if self.is_class else self.owner.__class__
        if field_name not in workflowmodel_registry.workflowmodels[id(cls)]:
            raise Exception("WorkflowModel with name:%s doesn't exist for class:%s" % (field_name, cls.__name__))
        if self.is_class:
            return ClassWorkflowModelObject(self.owner, field_name)
        else:
            return InstanceWorkflowModelObject(self.owner, field_name)

    def all(self, cls):
        return list([getattr(self, field_name) for field_name in workflowmodel_registry.workflowmodels[id(cls)]])

    def all_field_names(self, cls):  # pylint: disable=no-self-use
        return [field_name for field_name in workflowmodel_registry.workflowmodels[id(cls)]]
