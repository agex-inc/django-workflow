from workflow_config.models.managers.workflow_configmanager import WorkflowConfigManager


class TransitionApprovalMetadataManager(WorkflowConfigManager):
    def get_by_natural_key(self, workflow, source_state, destination_state, priority):
        return self.get(workflow=workflow, source_state=source_state, destination_state=destination_state, priority=priority)
