from workflow.models.hook import Hook


class OnCompleteHook(Hook):
    class Meta:
        unique_together = [('callback_function', 'workflowmodel', 'content_type', 'object_id')]
