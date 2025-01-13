from newname.admin.function_admin import *
from newname.admin.hook_admins import *
from newname.admin.transitionapprovalmeta import *
from newname.admin.transitionmeta import *
from newname.admin.workflowmodel import *
from newname.models import State
from newname.models import Channel
from newname.models import Template
from newname.models import Actor
from newname.models import NotificationTemplate

admin.site.register(State)
admin.site.register(Channel)
admin.site.register(Template)
admin.site.register(Actor)
admin.site.register(NotificationTemplate)