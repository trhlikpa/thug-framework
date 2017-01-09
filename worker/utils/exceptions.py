
class DatabaseRecordError(BaseException):
    def __init__(self, *args, **kwargs):
        super(DatabaseRecordError, self).__init__(*args, **kwargs)
