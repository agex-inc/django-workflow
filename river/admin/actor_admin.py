from django import forms
from django.contrib import admin
from river.models import Actor

class ActorForm(forms.ModelForm):
    class Meta:
        model = Actor
        fields = ('name',)

class ActorAdmin(admin.ModelAdmin):
    form = ActorForm
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]

admin.site.register(Actor, ActorAdmin)