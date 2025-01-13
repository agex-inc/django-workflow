from abc import abstractmethod


class NewNamenewname(object):

    def __init__(self, workflowmodel, wokflow_object_class, field_name):
        self.workflowmodel = workflowmodel
        self.wokflow_object_class = wokflow_object_class
        self.field_name = field_name
        self._cached_workflowmodel = None

    @abstractmethod
    def get_available_approvals(self, as_user):
        raise NotImplementedError()
