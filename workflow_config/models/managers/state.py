from workflow_config.models.managers.workflow_configmanager import WorkflowConfigManager


class StateManager(WorkflowConfigManager):
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)
