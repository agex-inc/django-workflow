from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet
from django.test import TestCase
from hamcrest import assert_that, has_property, is_, instance_of

from newname.core.classworkflowmodelobject import ClassWorkflowModelObject
from newname.core.instanceworkflowmodelobject import InstanceWorkflowModelObject
from newname.core.newnameobject import NewNameObject
from newname.models import State
from newname.models.factories import StateObjectFactory, TransitionApprovalMetaFactory, WorkflowModelFactory, TransitionMetaFactory
from newname.tests.models import BasicTestModel


# noinspection PyMethodMayBeStatic
class StateFieldTest(TestCase):

    def test_shouldInjectTheField(self):  # pylint: disable=no-self-use
        assert_that(BasicTestModel, has_property('newname', is_(instance_of(NewNameObject))))
        assert_that(BasicTestModel.newname, has_property('my_field', is_(instance_of(ClassWorkflowModelObject))))

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
        assert_that(test_model, has_property('newname', is_(instance_of(NewNameObject))))
        assert_that(test_model.newname, has_property('my_field', is_(instance_of(InstanceWorkflowModelObject))))
        assert_that(BasicTestModel.newname.my_field, has_property('initial_state', is_(instance_of(State))))
        assert_that(BasicTestModel.newname.my_field, has_property('final_states', is_(instance_of(QuerySet))))

        assert_that(test_model.newname.my_field, has_property('approve', has_property("__call__")))
        assert_that(test_model.newname.my_field, has_property('on_initial_state', is_(instance_of(bool))))
        assert_that(test_model.newname.my_field, has_property('on_final_state', is_(instance_of(bool))))
