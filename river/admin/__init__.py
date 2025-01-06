from river.admin.function_admin import *
from river.admin.hook_admins import *
from river.admin.transitionapprovalmeta import *
from river.admin.transitionmeta import *
from river.admin.workflow import *
from river.models import State
from river.models import Channel
from river.models import Template
from river.models import Actor

admin.site.register(State)
admin.site.register(Channel)
admin.site.register(Template)
admin.site.register(Actor)
