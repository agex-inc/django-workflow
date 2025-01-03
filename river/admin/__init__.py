from river.admin.function_admin import *
from river.admin.hook_admins import *
from river.admin.transitionapprovalmeta import *
from river.admin.transitionmeta import *
from river.admin.workflow import *
from river.models import State
from river.models import Channel

admin.site.register(State)
admin.site.register(Channel)
