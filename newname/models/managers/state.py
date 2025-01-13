from newname.models.managers.newnamemanager import NewNameManager


class StateManager(NewNameManager):
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)
