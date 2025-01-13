from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from newname.core.workflowmodelregistry import workflowmodel_registry
from newname.models import OnApprovedHook, OnTransitHook, OnCompleteHook


class BaseHookInline(GenericTabularInline):
    fields = ("callback_function", "hook_type")


class OnApprovedHookInline(BaseHookInline):
    model = OnApprovedHook

    def __init__(self, *args, **kwargs):
        super(OnApprovedHookInline, self).__init__(*args, **kwargs)
        self.fields += ("transition_approval_meta",)


class OnTransitHookInline(BaseHookInline):
    model = OnTransitHook

    def __init__(self, *args, **kwargs):
        super(OnTransitHookInline, self).__init__(*args, **kwargs)
        self.fields += ("transition_meta",)


class OnCompleteHookInline(BaseHookInline):
    model = OnCompleteHook


class DefaultWorkflowModelodelAdmin(admin.ModelAdmin):
    inlines = [
        OnApprovedHookInline,
        OnTransitHookInline,
        OnCompleteHookInline
    ]

    def __init__(self, *args, **kwargs):
        super(DefaultWorkflowModelodelAdmin, self).__init__(*args, **kwargs)
        self.readonly_fields += tuple(workflowmodel_registry.get_class_fields(self.model))


class OnApprovedHookAdmin(admin.ModelAdmin):
    list_display = ('workflowmodel', 'callback_function', 'transition_approval_meta')


class OnTransitHookAdmin(admin.ModelAdmin):
    list_display = ('workflowmodel', 'callback_function', 'transition_meta')


class OnCompleteHookAdmin(admin.ModelAdmin):
    list_display = ('workflowmodel', 'callback_function')


admin.site.register(OnApprovedHook, OnApprovedHookAdmin)
admin.site.register(OnTransitHook, OnTransitHookAdmin)
admin.site.register(OnCompleteHook, OnCompleteHookAdmin)
