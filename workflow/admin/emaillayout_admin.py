from django.contrib import admin

from workflow.models import EmailLayout


class EmailLayoutAdmin(admin.ModelAdmin):
    list_display = ('name', 'actor', 'subject', 'updated_at')
    search_fields = ('name', 'subject', 'actor')
    readonly_fields = ['updated_at']
 

admin.site.register(EmailLayout, EmailLayoutAdmin)
