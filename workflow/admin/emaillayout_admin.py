from django.contrib import admin

from workflow.models import EmailLayout


class EmailLayoutAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'updated_at')
    search_fields = ('id','name')
    readonly_fields = ['id','updated_at']
 

admin.site.register(EmailLayout, EmailLayoutAdmin)
