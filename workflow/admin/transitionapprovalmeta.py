from django.contrib import admin
from django import forms

from workflow.models.transitionapprovalmeta import TransitionApprovalMeta


class TransitionApprovalMetaForm(forms.ModelForm):
    class Meta:
        model = TransitionApprovalMeta
        fields = ('workflowmodel', 'transition_meta', 'permissions', 'groups', 'priority')


class TransitionApprovalMetaAdmin(admin.ModelAdmin):
    form = TransitionApprovalMetaForm
    list_display = ('workflowmodel', 'transition_meta', 'priority')


admin.site.register(TransitionApprovalMeta, TransitionApprovalMetaAdmin)
