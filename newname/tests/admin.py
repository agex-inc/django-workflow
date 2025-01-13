from django.contrib import admin
from django.contrib.admin import ModelAdmin

from newname.tests.models import BasicTestModel


class BasicTestModelAdmin(ModelAdmin):
    pass


admin.site.register(BasicTestModel, BasicTestModelAdmin)
