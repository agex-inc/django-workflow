class NewNameException(Exception):
    code = None

    def __init__(self, error_code, *args, **kwargs):
        super(NewNameException, self).__init__(*args, **kwargs)
        self.code = error_code
