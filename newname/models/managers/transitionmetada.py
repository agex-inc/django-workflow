from newname.models.managers.newnamemanager import NewNameManager


class TransitionApprovalMetadataManager(NewNameManager):
    def get_by_natural_key(self, workflowmodel, source_state, destination_state, priority):
        return self.get(workflowmodel=workflowmodel, source_state=source_state, destination_state=destination_state, priority=priority)
