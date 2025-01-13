from workflow_config.models.managers.workflow_configmanager import WorkflowConfigManager


class WorkflowManager(WorkflowConfigManager):
    def get_by_natural_key(self, content_type, field_name):
        return self.get(content_type=content_type, field_name=field_name)
