from django_cte import CTEManager

from newname.config import app_config
from newname.models.managers.newnamemanager import NewNameManager


class TransitionApprovalManager(NewNameManager if app_config.IS_MSSQL else CTEManager):
    def __init__(self, *args, **kwargs):
        super(TransitionApprovalManager, self).__init__(*args, **kwargs)

    def filter(self, *args, **kwarg):
        workflowmodel_object = kwarg.pop('workflowmodel_object', None)
        if workflowmodel_object:
            kwarg['content_type'] = app_config.CONTENT_TYPE_CLASS.objects.get_for_model(workflowmodel_object)
            kwarg['object_id'] = workflowmodel_object.pk

        return super(TransitionApprovalManager, self).filter(*args, **kwarg)

    def update_or_create(self, *args, **kwarg):
        workflowmodel_object = kwarg.pop('workflowmodel_object', None)
        if workflowmodel_object:
            kwarg['content_type'] = app_config.CONTENT_TYPE_CLASS.objects.get_for_model(workflowmodel_object)
            kwarg['object_id'] = workflowmodel_object.pk

        return super(TransitionApprovalManager, self).update_or_create(*args, **kwarg)
