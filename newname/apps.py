import logging
import operator
from functools import reduce

from django.apps import AppConfig
from django.db.utils import OperationalError, ProgrammingError

LOGGER = logging.getLogger(__name__)


class NewNameApp(AppConfig):
    name = 'newname'
    label = 'newname'

    def ready(self):
        for field_name in self._get_all_workflowmodel_fields():
            try:
                workflowmodels = self.get_model('WorkflowModel').objects.filter(field_name=field_name)
                if workflowmodels.count() == 0:
                    LOGGER.warning("%s field doesn't seem have any workflowmodel defined in database. You should create its workflowmodel" % field_name)
            except (OperationalError, ProgrammingError):
                pass

        from newname.config import app_config

        if app_config.INJECT_MODEL_ADMIN:
            for model_class in self._get_all_workflowmodel_classes():
                self._register_hook_inlines(model_class)

        LOGGER.debug('NewNameApp is loaded.')

    @classmethod
    def _get_all_workflowmodel_fields(cls):
        from newname.core.workflowmodelregistry import workflowmodel_registry
        return reduce(operator.concat, map(list, workflowmodel_registry.workflowmodels.values()), [])

    @classmethod
    def _get_all_workflowmodel_classes(cls):
        from newname.core.workflowmodelregistry import workflowmodel_registry
        return list(workflowmodel_registry.class_index.values())

    @classmethod
    def _get_workflowmodel_class_fields(cls, model):
        from newname.core.workflowmodelregistry import workflowmodel_registry
        return workflowmodel_registry.workflowmodels[id(model)]

    def _register_hook_inlines(self, model):  # pylint: disable=no-self-use
        from django.contrib import admin
        from newname.core.workflowmodelregistry import workflowmodel_registry
        from newname.admin import OnApprovedHookInline, DefaultWorkflowModelodelAdmin

        registered_admin = admin.site._registry.get(model, None)
        if registered_admin:
            if OnApprovedHookInline not in registered_admin.inlines:
                registered_admin.readonly_fields = list(set(list(registered_admin.readonly_fields) + list(workflowmodel_registry.get_class_fields(model))))
                admin.site._registry[model] = registered_admin
        else:
            admin.site.register(model, DefaultWorkflowModelodelAdmin)
