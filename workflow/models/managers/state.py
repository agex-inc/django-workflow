from workflow.models.managers.workflowmanager import WorkflowManager


class StateManager(WorkflowManager):
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)
