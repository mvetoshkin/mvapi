class AppException(Exception):
    pass


class NoCommandException(Exception):
    pass


class NoSettingsModuleSpecified(Exception):
    pass


###

class ModelKeyError(AppException):
    pass


class NotFoundError(AppException):
    pass
