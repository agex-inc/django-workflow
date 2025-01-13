class WorkflowConfigException(Exception):
    code = None

    def __init__(self, error_code, *args, **kwargs):
        super(WorkflowConfigException, self).__init__(*args, **kwargs)
        self.code = error_code
