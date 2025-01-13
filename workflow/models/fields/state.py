import logging

from django.contrib.contenttypes.models import ContentType
from django.db.models import CASCADE
from django.db.models.signals import post_save, post_delete

from workflow.core.workflowobject import WorkflowObject
from workflow.core.workflowmodelregistry import workflowmodel_registry
from workflow.models import OnApprovedHook, OnTransitHook, OnCompleteHook

try:
    from django.contrib.contenttypes.fields import GenericRelation
except ImportError:
    from django.contrib.contenttypes.generic import GenericRelation

from workflow.models.state import State
from workflow.models.transitionapproval import TransitionApproval
from workflow.models.transition import Transition

from django.db import models

LOGGER = logging.getLogger(__name__)


class classproperty(object):
    def __init__(self, getter):
        self.getter = getter

    def __get__(self, instance, owner):
        return self.getter(instance) if instance else self.getter(owner)


class StateField(models.ForeignKey):
    def __init__(self, *args, **kwargs):
        self.field_name = None
        kwargs['null'] = True
        kwargs['blank'] = True
        kwargs['to'] = '%s.%s' % (State._meta.app_label, State._meta.object_name)
        kwargs['on_delete'] = kwargs.get('on_delete', CASCADE)
        kwargs['related_name'] = "+"
        super(StateField, self).__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name, *args, **kwargs):
        @classproperty
        def workflow(_self):
            return WorkflowObject(_self)

        self.field_name = name

        self._add_to_class(cls, self.field_name + "_transition_approvals",
                           GenericRelation('%s.%s' % (TransitionApproval._meta.app_label, TransitionApproval._meta.object_name)))
        self._add_to_class(cls, self.field_name + "_transitions", GenericRelation('%s.%s' % (Transition._meta.app_label, Transition._meta.object_name)))

        if id(cls) not in workflowmodel_registry.workflowmodels:
            self._add_to_class(cls, "workflow", workflow)

        super(StateField, self).contribute_to_class(cls, name, *args, **kwargs)

        if id(cls) not in workflowmodel_registry.workflowmodels:
            post_save.connect(_on_workflowmodel_object_saved, self.model, False, dispatch_uid='%s_%s_workflowstatefield_post' % (self.model, name))
            post_delete.connect(_on_workflowmodel_object_deleted, self.model, False, dispatch_uid='%s_%s_workflowstatefield_post' % (self.model, name))

        workflowmodel_registry.add(self.field_name, cls)

    @staticmethod
    def _add_to_class(cls, key, value, ignore_exists=False):
        if ignore_exists or not hasattr(cls, key):
            cls.add_to_class(key, value)


def _on_workflowmodel_object_saved(sender, instance, created, *args, **kwargs):
    for instance_workflowmodel in instance.workflow.all(instance.__class__):
        if created:
            instance_workflowmodel.initialize_approvals()
            if not instance_workflowmodel.get_state():
                init_state = getattr(instance.__class__.workflow, instance_workflowmodel.field_name).initial_state
                instance_workflowmodel.set_state(init_state)
                instance.save()


def _on_workflowmodel_object_deleted(sender, instance, *args, **kwargs):
    OnApprovedHook.objects.filter(object_id=instance.pk, content_type=ContentType.objects.get_for_model(instance.__class__)).delete()
    OnTransitHook.objects.filter(object_id=instance.pk, content_type=ContentType.objects.get_for_model(instance.__class__)).delete()
    OnCompleteHook.objects.filter(object_id=instance.pk, content_type=ContentType.objects.get_for_model(instance.__class__)).delete()
