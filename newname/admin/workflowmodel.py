from django import forms
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType

from newname.core.workflowmodelregistry import workflowmodel_registry
from newname.models import WorkflowModel


def get_workflowmodel_choices():
    class_by_id = lambda cid: workflowmodel_registry.class_index[cid]
    result = []
    for class_id, field_names in workflowmodel_registry.workflowmodels.items():
        cls = class_by_id(class_id)
        content_type = ContentType.objects.get_for_model(cls)
        for field_name in field_names:
            result.append(("%s %s" % (content_type.pk, field_name), "%s.%s - %s" % (cls.__module__, cls.__name__, field_name)))
    return result


class WorkflowModelForm(forms.ModelForm):
    workflowmodel = forms.ChoiceField(choices=[])

    class Meta:
        model = WorkflowModel
        fields = ('workflowmodel', 'initial_state')

    def __init__(self, *args, **kwargs):
        instance = kwargs.get("instance", None)
        self.declared_fields['workflowmodel'].choices = get_workflowmodel_choices()
        if instance and instance.pk:
            self.declared_fields['workflowmodel'].initial = "%s %s" % (instance.content_type.pk, instance.field_name)

        super(WorkflowModelForm, self).__init__(*args, **kwargs)

    def clean_workflowmodel(self):
        if self.cleaned_data.get('workflowmodel') == '' or ' ' not in self.cleaned_data.get('workflowmodel'):
            return None, None
        else:
            return self.cleaned_data.get('workflowmodel').split(" ")

    def save(self, *args, **kwargs):
        content_type_pk, field_name = self.cleaned_data.get('workflowmodel')
        instance = super(WorkflowModelForm, self).save(commit=False)
        instance.content_type = ContentType.objects.get(pk=content_type_pk)
        instance.field_name = field_name
        return super(WorkflowModelForm, self).save(*args, **kwargs)


# noinspection PyMethodMayBeStatic
class WorkflowModelAdmin(admin.ModelAdmin):
    form = WorkflowModelForm
    list_display = ('model_class', 'field_name', 'initial_state')

    def model_class(self, obj):
        cls = obj.content_type.model_class()
        if cls:
            return "%s.%s" % (cls.__module__, cls.__name__)
        else:
            return "Class not found in the workspace"

    def field_name(self, obj):  # pylint: disable=no-self-use
        return obj.workflowmodel.field_name


admin.site.register(WorkflowModel, WorkflowModelAdmin)
