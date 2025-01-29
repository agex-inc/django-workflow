from django.contrib.contenttypes.models import ContentType

# from workflow.driver.workflow.mssql_workflow import MsSqlworkflow
from workflow.driver.mssql_driver import MsSqlworkflow
from workflow.driver.orm_driver import Ormworkflow
from workflow.models import State, TransitionApprovalMeta, WorkflowModel, app_config, TransitionMeta


class ClassWorkflowModelObject(object):

    def __init__(self, wokflow_object_class, field_name):
        self.wokflow_object_class = wokflow_object_class
        self.field_name = field_name
        self.workflowmodel = WorkflowModel.objects.filter(field_name=self.field_name, content_type=self._content_type).first()
        self._cached_workflow_workflow = None

    @property
    def _workflow_workflow(self):
        if self._cached_workflow_workflow:
            return self._cached_workflow_workflow
        else:
            if app_config.IS_MSSQL:
                self._cached_workflow_workflow = MsSqlworkflow(self.workflowmodel, self.wokflow_object_class, self.field_name)
            else:
                self._cached_workflow_workflow = Ormworkflow(self.workflowmodel, self.wokflow_object_class, self.field_name)
            return self._cached_workflow_workflow

    def get_on_approval_objects(self, as_user):
        approvals = self.get_available_approvals(as_user)
        object_ids = list(approvals.values_list('object_id', flat=True))
        return self.wokflow_object_class.objects.filter(pk__in=object_ids)

    def get_available_approvals(self, as_user, include_return_transitions=False):
        return self._workflow_workflow.get_available_approvals(as_user, include_return_transitions=include_return_transitions)

    @property
    def initial_state(self):
        workflowmodel = WorkflowModel.objects.filter(content_type=self._content_type, field_name=self.field_name).first()
        return workflowmodel.initial_state if workflowmodel else None

    @property
    def final_states(self):
        all_states = TransitionMeta.objects.filter(workflowmodel=self.workflowmodel).values_list("source_state", "destination_state")
        source_states = set([states[0] for states in all_states])
        destination_states = set([states[1] for states in all_states])
        final_states = destination_states - source_states
        return State.objects.filter(pk__in=final_states)

    @property
    def _content_type(self):
        return ContentType.objects.get_for_model(self.wokflow_object_class)
