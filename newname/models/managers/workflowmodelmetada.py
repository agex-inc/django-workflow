from newname.models.managers.newnamemanager import NewNameManager


class WorkflowModelManager(NewNameManager):
    def get_by_natural_key(self, content_type, field_name):
        return self.get(content_type=content_type, field_name=field_name)
