class BaseStateError(Exception):
    def __init__(self, message):
        self.message = message


class MissingLockError(BaseStateError):
    pass


class ConcurrentLockError(BaseStateError):
    pass
