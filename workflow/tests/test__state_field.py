from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet
from django.test import TestCase
from hamcrest import assert_that, has_property, is_, instance_of

from workflow.core.classworkflowmodelobject import ClassWorkflowModelObject
from workflow.core.instanceworkflowmodelobject import InstanceWorkflowModelObject
from workflow.core.workflowobject import WorkflowObject
from workflow.models import State
from workflow.models.factories import StateObjectFactory, TransitionApprovalMetaFactory, WorkflowModelFactory, TransitionMetaFactory
from workflow.tests.models import BasicTestModel


# noinspection PyMethodMayBeStatic
class StateFieldTest(TestCase):

    def test_shouldInjectTheField(self):  # pylint: disable=no-self-use
        assert_that(BasicTestModel, has_property('workflow', is_(instance_of(WorkflowObject))))
        assert_that(BasicTestModel.workflow, has_property('my_field', is_(instance_of(ClassWorkflowModelObject))))

        content_type = ContentType.objects.get_for_model(BasicTestModel)

        state1 = StateObjectFactory.create(label="state1")
        state2 = StateObjectFactory.create(label="state2")

        workflowmodel = WorkflowModelFactory(content_type=content_type, field_name="my_field", initial_state=state1)

        transition_meta = TransitionMetaFactory.create(
            workflowmodel=workflowmodel,
            source_state=state1,
            destination_state=state2,
        )

        TransitionApprovalMetaFactory.create(
            workflowmodel=workflowmodel,
            transition_meta=transition_meta,
            priority=0
        )
        test_model = BasicTestModel.objects.create()
        assert_that(test_model, has_property('workflow', is_(instance_of(WorkflowObject))))
        assert_that(test_model.workflow, has_property('my_field', is_(instance_of(InstanceWorkflowModelObject))))
        assert_that(BasicTestModel.workflow.my_field, has_property('initial_state', is_(instance_of(State))))
        assert_that(BasicTestModel.workflow.my_field, has_property('final_states', is_(instance_of(QuerySet))))

        assert_that(test_model.workflow.my_field, has_property('approve', has_property("__call__")))
        assert_that(test_model.workflow.my_field, has_property('on_initial_state', is_(instance_of(bool))))
        assert_that(test_model.workflow.my_field, has_property('on_final_state', is_(instance_of(bool))))
