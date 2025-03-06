from django.contrib import admin
from workflow.models import ActorEmailLayout


class ActorEmailLayoutAdmin(admin.ModelAdmin):
    list_display = ('actor', 'email_layout')
    search_fields = ('actor__name', 'email_layout__name')
    list_filter = ('actor', 'email_layout')

admin.site.register(ActorEmailLayout, ActorEmailLayoutAdmin)
