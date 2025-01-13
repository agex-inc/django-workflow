from django import forms
from django.contrib import admin

from newname.models import TransitionMeta


class TransitionMetaForm(forms.ModelForm):
    class Meta:
        model = TransitionMeta
        fields = ('workflowmodel', 'source_state', 'destination_state')


class TransitionMetaAdmin(admin.ModelAdmin):
    form = TransitionMetaForm
    list_display = ('workflowmodel', 'source_state', 'destination_state')


admin.site.register(TransitionMeta, TransitionMetaAdmin)
