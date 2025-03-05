from workflow.admin.function_admin import *
from workflow.admin.hook_admins import *
from workflow.admin.transitionapprovalmeta import *
from workflow.admin.transitionmeta import *
from workflow.admin.workflowmodel import *
from workflow.admin.emaillayout_admin import *
from workflow.models import State
from workflow.models import Channel
from workflow.models import Template
from workflow.models import Actor
from workflow.models import NotificationTemplate



admin.site.register(State)
admin.site.register(Channel)
admin.site.register(Template)
admin.site.register(Actor)
admin.site.register(NotificationTemplate)