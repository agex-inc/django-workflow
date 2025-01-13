from workflow_config.admin.function_admin import *
from workflow_config.admin.hook_admins import *
from workflow_config.admin.transitionapprovalmeta import *
from workflow_config.admin.transitionmeta import *
from workflow_config.admin.workflow import *
from workflow_config.models import State
from workflow_config.models import Channel
from workflow_config.models import Template
from workflow_config.models import Actor
from workflow_config.models import NotificationTemplate

admin.site.register(State)
admin.site.register(Channel)
admin.site.register(Template)
admin.site.register(Actor)
admin.site.register(NotificationTemplate)