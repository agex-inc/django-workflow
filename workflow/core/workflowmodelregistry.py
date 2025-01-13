class WorkflowModelRegistry(object):
    def __init__(self):
        self.workflowmodels = {}
        self.class_index = {}

    def add(self, name, cls):
        self.workflowmodels[id(cls)] = self.workflowmodels.get(id(cls), set())
        self.workflowmodels[id(cls)].add(name)
        self.class_index[id(cls)] = cls

    def get_class_fields(self, model):
        return self.workflowmodels[id(model)]


workflowmodel_registry = WorkflowModelRegistry()
